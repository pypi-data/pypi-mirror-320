import numpy as np,pandas as pd
def get_interviewee_responses(input_text):
    """Returns a list of interviewee responses, this function is only used for cleaning annotated datasets by the human annotators"""
    parts = input_text.split('Interviewer:')  # Split by 'Interviewer:'
    interviewee_segments = []

    for part in parts:
        interviewee_part = part.split('Interviewee:')
        if len(interviewee_part) > 1:
            interviewee_segments.append(interviewee_part[1].strip())

    return [i for i in interviewee_segments if len(i) > 30]


