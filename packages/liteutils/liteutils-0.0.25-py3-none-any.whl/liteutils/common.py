import json
from pathlib import Path

def write_json(data, filepath):
    """Write JSON data to a file using Pathlib."""
    path = Path(filepath)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(filepath):
    """Read JSON data from a file using Pathlib."""
    path = Path(filepath)
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)
