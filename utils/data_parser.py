import json


def parse_metadata(metadata_raw: str) -> dict:
    """
    Parses the raw metadata string from eLabFTW into a dictionary.
    Handles NoneType and JSON formatting errors.
    """
    if not metadata_raw or not isinstance(metadata_raw, str):
        return {}
    
    try:
        return json.loads(metadata_raw)
    except json.JSONDecodeError:
        return {}


def flatten_rotor_data(data_json: dict) -> dict:
    """
    Pass in the complete dictionary of a single item returned by the API.
    Output a "flattened" clean dictionary that directly extracts the values from `extra_fields`.
    """
    result = {
        "id": data_json.get("id"),
        "title": data_json.get("title"),
        "tags": data_json.get("tags", []),
    }
    
    metadata_raw = data_json.get("metadata")
    assert isinstance(metadata_raw, str)
    metadata = parse_metadata(metadata_raw)   # data_json.get("metadata") returns metadata_raw as a json string, and then gets parsed into a python dictionary
    metadata_extra_fields = metadata.get("extra_fields", {})
    
    target_fields = ["Rotor number", "Status", "Owner", "Sample name", "Location", "Date", "Note"]
    
    for field in target_fields:
        field_data = metadata_extra_fields.get(field, {})
        result[field] = field_data.get("value", "")
        
    return result