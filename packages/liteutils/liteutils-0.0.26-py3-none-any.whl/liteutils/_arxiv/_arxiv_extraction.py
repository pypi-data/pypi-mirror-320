import re


def extract_abstract(text):
    # Use regex to find the abstract section
    pattern = r'abstract\s*([\s\S]*?)(?=introduction|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()
    else:
        return None