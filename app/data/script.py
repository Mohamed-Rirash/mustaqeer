import json
import os

def load_json_data(file_name):
    """
    Load JSON data from a file in the app/data directory.

    Args:
        file_name (str): Name of the JSON file to load.

    Returns:
        dict: Loaded JSON data as a Python dictionary.
    """
    file_path = os.path.join('app', 'data', file_name)

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found in the app/data directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse '{file_name}' as JSON.")
        return None

# Example usage:

json_data = load_json_data('juz.json')

