import json


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
        result[field] = field_data.get("value", "")
        
    return result