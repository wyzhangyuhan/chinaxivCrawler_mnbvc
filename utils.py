import re

def mark_finish():
    ...

def extract_text(input_str):
    """
    Extract and return the text inside and outside of parentheses.

    Parameters:
    - input_str: A string that includes text and parentheses.

    Returns:
    A tuple where the first element is a list of texts outside the parentheses,
    and the second element is a list of texts inside the parentheses.
    """

    pattern = re.compile(r'([^\(\)]+)(?:\((\d+)\))')
    match = pattern.search(input_str)
    
    text, number = match.groups()

    return text, number