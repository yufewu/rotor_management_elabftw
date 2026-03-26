import json
from api_services.client import get_shared_items_api_client
from utils.data_parser import flatten_rotor_data


def get_single_item(item_id: int) -> dict:
    """
    Retrieve the raw data for a single item based on its ID and automatically parse its metadata once.
    """
    api_instance = get_shared_items_api_client()
    api_response = api_instance.get_item(item_id, _preload_content=False)

    data_json = json.loads(api_response.data.decode("utf-8"))
    
    metadata_string = data_json.get("metadata")
    if metadata_string and isinstance(metadata_string, str):
        try:
            data_json["metadata_parsed"] = json.loads(metadata_string)
        except json.JSONDecodeError:
            data_json["metadata_parsed"] = {"error": "无法解析 JSON 字符串"}
    else:
        data_json["metadata_parsed"] = {}

    return data_json


def get_single_rotor(item_id: int) -> dict:
    """
    Retrieve the raw data for a single rotor item based on its ID and parse all meta date into a flattened dictionary.
    """
    api_instance = get_shared_items_api_client()
    api_response = api_instance.get_item(item_id, _preload_content=False)

    data_json = json.loads(api_response.data.decode("utf-8"))
    
    return flatten_rotor_data(data_json)


def get_all_rotors(category_id: int) -> list[dict]:
    """
    Retrieve all items from eLabFTW, then filter and clean them to create a flattened list of Rotors.
    """
    api_instance = get_shared_items_api_client()
    
    try:
        api_response = api_instance.read_items(cat=f"{category_id}", _preload_content=False)
        
        items = json.loads(api_response.data.decode("utf-8"))
        
        all_rotors = []
        
        for item in items:
            flattened_item = flatten_rotor_data(item)
            
            if flattened_item.get("Rotor number") != "N/A":
                all_rotors.append(flattened_item)
                
        return all_rotors

    except Exception as e:
        print(f"Error fetching all rotors: {e}")
        raise e


def create_rotor(new_data: dict, category_id: int):
    """
    Create a new Rotor in eLabFTW.
    new_data: A dictionary containing all fields.
    category_id: The category ID of your Rotor template in eLabFTW. 
    """
    api_instance = get_shared_items_api_client()

    try:
        body = {"category": category_id}
        response = api_instance.post_item(body=body, _preload_content=False)
        new_id = None
        
        location = response.headers.get("Location")
        if location:
            new_id = int(location.split("/")[-1])
            
        if new_id is None:
            return {"success": False, "message": "The request was sent successfully, but the returned ID could not be parsed. "}

        metadata = {"extra_fields": {}}
        for key, value in new_data.items():
            metadata["extra_fields"][key] = {"value": value, "type": "text"}
            
        rotor_number = new_data.get("Rotor number", "New Rotor")
        
        patch_body = {
            "title": f"Rotor #{rotor_number}", # 设置一个规范的标题
            "metadata": json.dumps(metadata)
        }
        api_instance.patch_item(patch_body, new_id)
        
        return {"success": True, "message": f"Creation successful! Rotor #{rotor_number} has been generated. (Backend ID: {new_id})"}

    except Exception as e:
        print(f"Create failed: {e}")
        return {"success": False, "message": str(e)}


def update_rotor(item_id: int, new_data: dict) -> dict:
    """
    Update the Rotor data with the specified ID.
    """
    api_instance = get_shared_items_api_client()
    
    try:
        current_item = api_instance.get_item(item_id, _preload_content=False)
        current_data = json.loads(current_item.data.decode("utf-8"))
        
        metadata = json.loads(current_data.get("metadata", "{}"))
        if "extra_fields" not in metadata:
            metadata["extra_fields"] = {}

        for key, value in new_data.items():
            if key in metadata["extra_fields"]:
                metadata["extra_fields"][key]["value"] = value
            else:
                metadata["extra_fields"][key] = {"value": value}

        updated_metadata_str = json.dumps(metadata)

        body = {"metadata": updated_metadata_str}
        
        api_response = api_instance.patch_item(body, item_id)
        
        return {"success": True, "message": f"Item {item_id} updated"}

    except Exception as e:
        print(f"Update failed: {e}")
        return {"success": False, "message": str(e)}