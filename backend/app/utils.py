import json
from pathlib import Path
from typing import Any, List, Dict, Union
import time

def save_json(data: Union[List, Dict], filename: str, directory: str = "data") -> str:
    """
    Saves data in JSON format.

    Args:
        data: The data to save (list or dictionary)
        filename: Name of the file (without extension)
        directory: Directory to save the file (default: "data")

    Returns:
        str: Full path of the saved file
    """
    # Create the directory if it doesn't exist
    save_dir = Path(__file__).parent / Path(directory)
    save_dir.mkdir(exist_ok=True)

    # Build the full path
    filepath = save_dir / f"{filename}.json"
    print(filepath)

    # Save with a timestamp
    save_data = {
        "timestamp": time.time(),
        "data": data
    }

    # Write to the file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
        
    print(f"Données sauvegardées dans {filepath}")
    return str(filepath)




def load_json(filename: str, directory: str = "data") -> Union[List, Dict]:
    """
    Loads data from a JSON file.

    Args:
        filename: Name of the file (without extension)
        directory: Directory containing the file (default: "data")

    Returns:
        The loaded data (list or dictionary)

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    # Build the full path
    filepath = Path(__file__).parent / directory / f"{filename}.json"

    # Check if the file exists
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)

    # Check the structure
    if not isinstance(loaded_data, dict) or "data" not in loaded_data:
        raise ValueError(f"Invalid data format in {filepath}")

    # Display information about the loaded data
    timestamp = loaded_data.get("timestamp", "unknown")
    if timestamp != "unknown":
        from datetime import datetime
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Données sauvegardées le: {date_str}")
    
    return loaded_data["data"]
