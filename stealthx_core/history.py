import json
import os
from datetime import datetime

HISTORY_FILE = "stealthx_history.json"

def save_to_history(action_type: str, details: dict):
    """Saves a record to the history file. Does not store actual passwords."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "type": action_type,
        "details": details
    }
    
    history = get_history()
    history.append(record)
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def get_history() -> list:
    """Retrieves all history records."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
