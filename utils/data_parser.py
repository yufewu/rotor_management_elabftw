import json
import tomllib
from pathlib import Path
from .supporting_data import COLORS


def get_username_translator() -> dict[str, str]:
    toml_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"

    with open(toml_path, "rb") as f:
        config = tomllib.load(f)
    
    translator = {}
    
    alias_groups = ["group_members", "former_members", "students"]
    for group in alias_groups:
        group_data = config.get(group, {})
        for real_name, aliases in group_data.items():
            translator[real_name] = real_name
            for alias in aliases:
                translator[alias] = real_name
                
    return translator


_translator = get_username_translator()


def real_name(input):
    if not input:
        return input
    
    input_lower = input.strip().lower()

    for alias in _translator.keys():
        if input_lower.startswith(alias):
            return _translator[alias]
        
    return input_lower
    

def parse_data(data_raw: str | None) -> dict:
    """
    Parses the raw data string from eLabFTW API response into a dictionary.
    Handles NoneType and JSON formatting errors.
    """
    if not data_raw or not isinstance(data_raw, str):
        return {}
    
    try:
        return json.loads(data_raw)
    except json.JSONDecodeError:
        return {}


def interpret_rotor_response(parsed_response_data: dict) -> dict:
    """
    Pass in the complete dictionary of a single item returned by the API.
    Output a "interpreted" clean dictionary that directly extracts the values from `extra_fields`.
    """
    result = {
        "id": parsed_response_data.get("id"),
        "title": parsed_response_data.get("title"),
        "tags": parsed_response_data.get("tags", []),
        "body": parsed_response_data.get("body"),
    }
    
    _raw_metadata = parsed_response_data.get("metadata")
    _parsed_metadata = parse_data(_raw_metadata)   # parsed_response_data.get("metadata") returns metadata_raw as a json string, and then gets parsed into a python dictionary
    _rotor_information = _parsed_metadata.get("extra_fields", {})
    
    target_fields = ["Rotor number", "Status", "Owner", "Sample name", "Location", "Date", "Note"]
    
    for field in target_fields:
        field_data = _rotor_information.get(field, {})
        value = field_data.get("value", "")

        if field == "Owner":
            result[field] = real_name(value)
        else: 
            result[field] = value
    
    result["Rotor size"] = result["Rotor number"][:2]

    return result


def color_row_by_status(row):
    if row['Status'] in COLORS:
        color = f"background-color: {COLORS[row['Status']]}"
    else:
        color = ""
    return [color] * len(row)