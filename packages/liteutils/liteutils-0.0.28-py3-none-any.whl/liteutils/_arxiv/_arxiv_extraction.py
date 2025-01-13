import re


def extract_abstract(text):
    # Use regex to find the abstract section
    pattern = r'abstract\s*([\s\S]*?)(?=introduction|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()
    else:
        return None


def extract_references(text):
    # Use regex to find the references section
    pattern = r'references\s*([\s\S]*?)(?=bibliography|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()
    else:
        return None


def remove_references(text):
    # Use regex to find and remove the references section
    pattern = r'references\s*([\s\S]*?)(?=bibliography|\Z)'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove everything after the last occurrence of "References"
    final_pattern = r'References\s*([\s\S]*)'
    final_match = re.search(final_pattern, cleaned_text, re.IGNORECASE)
    
    if final_match:
        cleaned_text = cleaned_text[:final_match.start()]
    
    return cleaned_text.strip()
