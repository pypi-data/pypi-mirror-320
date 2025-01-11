import os
import numpy as np
import pandas as pd
import torch
from typing import List, Optional, Dict
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer, 
    DataCollatorWithPadding, 
    pipeline
)
import evaluate

from sklearn.model_selection import train_test_split




class TranscriptTrainer:
    def __init__(
        self, 
        input_file: str, 
        destination_path: Optional[str] = None, 
        text_column:str = "full_quote",
        target_column:str = 'target',
        test_size:int = 0.2,
        max_length: int = 512,
        num_train_epochs: int = 20,
        learning_rate_distilbert: float = 1e-5,
        learning_rate_electra: float = 2e-5,
        labels: Optional[List[str]] = None,
        upper_lower_mapping: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize the TranscriptTrainer

        Args:
            input_file (str): Path to the input file (.csv or .xlsx format)
            destination_path (str, optional): Path to save model outputs and results
            max_length (int, optional): Maximum sequence length for tokenization
            num_train_epochs (int, optional): Number of training epochs
            learning_rate_distilbert (float, optional): Learning rate for DistilBERT
            learning_rate_electra (float, optional): Learning rate for Electra
            labels (List[str], optional): List of classification labels
            upper_lower_mapping (Dict[str, List[str]], optional): Dictionary mapping top-level categories to their subcategories
        """
        # Default Labels
        self.LABELS = labels or [
            'Value equation',
            'Credentialing / Quality Assurance Infrastructure',
            'Finanicial Impact',
            'Health System Characteristics',
            'Clinical utility & efficiency-Provider perspective',
            'Workflow related problems',
            'Provider Characteristics',
            'Training',
            'Patient/Physican interaction in LUS',
            'Imaging modalities in general'
        ]

        # Default Top Levels (with more flexible structure)
        self.upper_lower_mapping = upper_lower_mapping or {
            "multi_level_org_char": [
                "Provider Characteristics", 
                "Health System Characteristics"
            ],
            "multi_level_org_perspect": [
                "Imaging modalities in general",
                'Value equation',
                "Clinical utility & efficiency-Provider perspective",
                "Patient/Physican interaction in LUS",
                'Workflow related problems'
            ],
            "impl_sust_infra": [
                "Training",
                'Credentialing / Quality Assurance Infrastructure',
                "Finanicial Impact"
            ]
        }

        # Flatten categories for easier processing
        self.CATEGORIES = {}
        for top_level, subcategories in self.upper_lower_mapping.items():
            for category in subcategories:
                self.CATEGORIES[category] = top_level

        # Configurations
        self.input_file = input_file
        self.destination_path = destination_path or os.path.dirname(input_file)
        self.max_length = max_length
        self.num_train_epochs = num_train_epochs
        self.learning_rate_distilbert = learning_rate_distilbert
        self.learning_rate_electra = learning_rate_electra
        self.test_size = test_size
        self.text_column = text_column

        # Devices
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Load and prepare data
        self._load_and_prepare_data()
        print("DATASET LABELS AND IDS PREPARED SUCCESSFULLY")

    def _load_and_prepare_data(self):
        """Load input data and prepare for training"""
        # Determine file type and load accordingly
        file_extension = os.path.splitext(self.input_file)[1].lower()
        
        if file_extension == '.csv':
            full_data = pd.read_csv(self.input_file)
        elif file_extension == '.xlsx':
            full_data = pd.read_excel(self.input_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Please use .csv or .xlsx files.")
        
        # Reset index to ensure unique labels
        full_data = full_data.reset_index(drop=True)
        
        # Add target column
        full_data['target'] = 'Unknown'
        
        # Assign target based on label columns
        for col in self.LABELS:
            full_data.loc[full_data[col] == 1, 'target'] = col
        
        # Perform train-test split
        msk_train, msk_test = train_test_split(
            full_data.index, 
            test_size=0.2, 
            stratify=full_data.target, 
            random_state=0
        )
        
        # Use vectorized operations to assign split labels
        full_data['split'] = 'neither'
        full_data.loc[msk_train, 'split'] = 'train'
        full_data.loc[msk_test, 'split'] = 'test'
        
        # Remove Unknown target rows
        full_data = full_data[full_data['target'] != 'Unknown']
        
        # Add numeric labels
        full_data['labels'] = full_data.target.astype('category').cat.codes

        # Save to CSV instead of Excel
        full_data.to_csv(os.path.join(self.destination_path, "SplitHuman.csv"), index=False)
        
        # Store the processed dataframe
        self.full_data = full_data

        
        # Generate label mappings
        labels = full_data.target.unique().tolist()
        self.label2id = {i: labels.index(i) for i in labels}
        self.id2label = {v: k for k, v in self.label2id.items()}
        
        # Prepare train and eval datasets
        self.train_data = full_data[full_data['split'] == 'train']
        self.eval_data = full_data[full_data['split'] == 'test']
        
        # Create Hugging Face datasets
        self.train_dataset = Dataset.from_dict({
            'text': self.train_data[self.text_column].values.tolist(),
            'label': self.train_data.labels.tolist()
        })
        self.eval_dataset = Dataset.from_dict({
            'text': self.eval_data[self.text_column].values.tolist(),
            'label': self.eval_data.labels.tolist()
        })
        
        # Print dataset shape for verification
        print(f"Full dataset shape: {full_data.shape}")


    def _preprocess_data(self, tokenizer):
        """Preprocess data for model training"""
        def preprocess_function(examples):
            return tokenizer(
                examples["text"], 
                truncation=True, 
                max_length=self.max_length
            )

        train_dataset = self.train_dataset.map(preprocess_function)
        eval_dataset = self.eval_dataset.map(preprocess_function)

        return train_dataset, eval_dataset

    def _compute_metrics(self, eval_pred):
        """Compute accuracy metrics"""
        accuracy = evaluate.load("accuracy")
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return accuracy.compute(predictions=predictions, references=labels)

        print("COMPUTE METRIC LOADED")

    
    def train_distilbert(self):
        """Train DistilBERT model"""
        output_dir = os.path.join(self.destination_path, 'interview_classifier')
        os.makedirs(output_dir, exist_ok=True)

        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", 
            id2label=self.id2label, 
            label2id=self.label2id
        ).to(self.device)

        tokenizer = AutoTokenizer.from_pretrained(
            "distilbert-base-uncased", 
            max_length=self.max_length
        )

        train_dataset, eval_dataset = self._preprocess_data(tokenizer)
        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.learning_rate_distilbert,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            num_train_epochs=self.num_train_epochs,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            report_to=['none']
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
            compute_metrics=self._compute_metrics
        )

        trainer.train()

        return trainer

    def train_electra(self):
        """Train Electra model"""
        output_dir = os.path.join(self.destination_path, 'interview_electra')
        os.makedirs(output_dir, exist_ok=True)

        model = AutoModelForSequenceClassification.from_pretrained(
            "mrm8488/electra-small-finetuned-squadv2", 
            id2label=self.id2label, 
            label2id=self.label2id
        ).to(self.device)

        tokenizer = AutoTokenizer.from_pretrained(
            "mrm8488/electra-small-finetuned-squadv2", 
            max_length=self.max_length
        )

        train_dataset, eval_dataset = self._preprocess_data(tokenizer)
        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.learning_rate_electra,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            num_train_epochs=self.num_train_epochs,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            report_to=['none']
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
            compute_metrics=self._compute_metrics
        )

        trainer.train()


        return trainer

    def _classify_text(self, text, pipeline_model):
        """
        Classify a single text using a pipeline model

        Args:
            text (str): Text to classify
            pipeline_model (pipeline): Trained pipeline model

        Returns:
            dict: Classification result with additional top-level information
        """
        output = pipeline_model(text, max_length=self.max_length, truncation=True)
        
        # Add top-level category to the output
        label = output[0]['label']
        output[0]['top level'] = self.CATEGORIES.get(label, '')

        return output

    def classify_sheet_with_model(self, model_path, input_dataframe):
        """
        Classify text using a trained model

        Args:
            model_path (str): Path to the trained model
            input_dataframe (pd.DataFrame): DataFrame to classify

        Returns:
            pd.DataFrame: Classified DataFrame
        """
        model_pipeline = pipeline('text-classification', model_path)
        result_sheet = input_dataframe.copy()

        for index, row in result_sheet.iterrows():
            if row[self.LABELS].values.sum() > 0:
                prediction = self._classify_text(row[self.text_column], model_pipeline)
                feature = prediction[0]['label']

                result_sheet.at[index, feature] = 1

                # Add top-level category columns
                for top_level, categories in self.upper_lower_mapping.items():
                    column_name = top_level.lower().replace(' ', '_')
                    if feature in categories:
                        result_sheet.at[index, column_name] = 1

        return result_sheet


    def _get_latest_checkpoint(self, model_dir):
        """
        Get the latest checkpoint from a model directory

        Args:
            model_dir (str): Directory containing model checkpoints

        Returns:
            str: Path to the latest checkpoint
        """
        checkpoints = [
            os.path.join(model_dir, d) 
            for d in os.listdir(model_dir) 
            if d.startswith("checkpoint-")
        ]
        latest_checkpoint = max(checkpoints, key=lambda x: int(x.split('-')[-1]))
        return latest_checkpoint



    def train_and_classify(self):
        """Train both models and classify"""
        bert_trainer = self.train_distilbert()
        electra_trainer = self.train_electra()

        bert_checkpoint = self._get_latest_checkpoint(
            os.path.join(self.destination_path, 'interview_classifier')
        )
        electra_checkpoint = self._get_latest_checkpoint(
            os.path.join(self.destination_path, 'interview_electra')
        )

        bert_sheet = self.classify_sheet_with_model(bert_checkpoint, self.full_data)
        electra_sheet = self.classify_sheet_with_model(electra_checkpoint, self.full_data)

        # Save to CSV files instead of Excel
        bert_file = os.path.join(self.destination_path, f'SplitBert.csv')
        electra_file = os.path.join(self.destination_path, f'SplitElectra.csv')

        bert_sheet.to_csv(bert_file, index=False)
        electra_sheet.to_csv(electra_file, index=False)

        return bert_trainer, electra_trainer




if __name__ == "__main__":

    trainer = TranscriptTrainer(
        input_file='CompletedMerged.csv',  #can be .xlsx or .csv
        destination_path='results',
        max_length=512,
        num_train_epochs=10
    )

    bert_model, electra_model = trainer.train_and_classify()
