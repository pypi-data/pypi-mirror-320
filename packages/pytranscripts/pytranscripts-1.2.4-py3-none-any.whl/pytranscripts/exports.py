import os
import re
import numpy as np
import pandas as pd
from docx import Document
import tqdm
from typing import List


def export_docx_from_folder(input_directory:str, output_file:str, labels:List[str] = None) -> None:

    """
    Process interview transcripts from .docx files into structured format.
    
    Parameters
    ----------
    input_directory : str
        Directory containing .docx transcript files
        
    output_file : str
        Path where output file will be saved (.csv or .xlsx format)
    
    labels : List[str]
        List of labels for columns. Default is None.
        
    Returns
    -------
    None
        Saves processed data to output file
        
    Examples
    --------
    >>> export_docx_from_folder("raw_transcripts/", "processed_data.csv")
    
    Notes
    -----
    Expected .docx format:
    - Each file named with unique participant ID
    - Content alternating between "Interviewer:" and "Interviewee:" lines
    - Consistent formatting throughout document
    """

    def read_doc(file_path):
        """Read the .docx file and return the content as text."""
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def process_interview(text):
        """
        Parse the raw interview data from the given text into a pandas DataFrame.
        
        Parameters:
        text (str): The raw interview text.

        Returns:
        pd.DataFrame: A DataFrame containing the parsed interview data.
        """
        # Split the text into interview segments by "Interviewer:"
        lines = text.replace('\n', '').split('Interviewer:')
        interviews = []

        # Loop over each segment
        for line in lines:
            if not line.strip():
                continue

            # Split each segment into interviewer and interviewee parts
            parts = line.split('Interviewee:')
            interviewer = parts[0].strip()
            interviewee = parts[1].strip() if len(parts) > 1 else "[No Reply]"

            interviews.append({'Interviewer': interviewer, 'Interviewee': interviewee})

        # Convert list of interview data to DataFrame
        return pd.DataFrame(interviews)

    # Step 1: Gather all .docx files from the specified directory
    doc_files = []
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".docx"):
                full_path = os.path.join(root, file)
                doc_files.append(full_path)

    print(f"Found {len(doc_files)} .docx files in the directory.")

    # Step 2: Process each .docx file and append the results to a list of DataFrames
    df_list = []
    for doc_file in tqdm.tqdm(doc_files, desc="Processing files"):
        text = read_doc(doc_file)
        df = process_interview(text)
        df["Participant ID"] = os.path.basename(doc_file).split('.')[0]
        df_list.append(df)

    # Step 3: Concatenate all DataFrames into a single DataFrame
    if df_list:
        final_df = pd.concat(df_list)
        print(f"Total rows in the concatenated DataFrame: {final_df.shape[0]}")
        if labels:
            for label in labels:
                final_df[label] = 0

    else:
        print("No data found to concatenate.")
        return

    # Step 4: Save the concatenated DataFrame based on file extension
    file_extension = os.path.splitext(output_file)[1].lower()
    
    if file_extension == '.csv':
        final_df.to_csv(output_file, index=False)
    elif file_extension == '.xlsx':
        final_df.to_excel(output_file, index=False)
    else:
        raise ValueError(f"Unsupported output format: {file_extension}. Please use .csv or .xlsx")
        
    print(f"Generated Survey Data has been successfully saved to {output_file}")


# Example usage:
# export_docx_from_folder('Dataset/ORIGINAL DATASET', 'SURVEY_TABLE.csv')  # For CSV
# export_docx_from_folder('Dataset/ORIGINAL DATASET', 'SURVEY_TABLE.xlsx')  # For Excel
