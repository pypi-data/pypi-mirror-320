import os
import re
import numpy as np
import pandas as pd
from docx import Document
import tqdm


def docx_transcripts_to_excel(input_directory, output_file):
    """
    This function reads all .docx files from the specified directory,
    processes interview data, and exports it to an Excel file.

    Parameters:
    input_directory (str): Directory containing the de-identified transcripts in .docx format.
    output_file (str): The path where the resulting Excel file should be saved.

    Returns:
    None: Saves the processed data into an Excel file.
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
    else:
        print("No data found to concatenate.")
        return

    # Step 4: Save the concatenated DataFrame to an Excel file
    final_df.to_excel(output_file, index=False)
    print(f"Generated Survey Data has been successfully saved to {output_file}")


# Example usage:
# process_transcripts_to_excel('De-identified transcripts', 'SURVEY_TABLE.xlsx')
