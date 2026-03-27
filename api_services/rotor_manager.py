import json
import csv
import io
from datetime import datetime
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


def _append_csv_log(current_body: str, form_data: dict) -> str:
    """Internal function: Generate a new body containing CSV logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    note = str(form_data.get("Note", "")).replace('\n', ' ')
    
    row = [
        timestamp, 
        form_data.get("Owner", ""), 
        form_data.get("Status", ""), 
        form_data.get("Sample name", ""), 
        form_data.get("Location", ""), 
        note, 
        form_data.get("Date", ""), 
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(row)
    csv_line = output.getvalue().strip()
    
    START_TAG = "<p>--------------------------</p>"
    END_TAG = "<p>**************************</p>"
    
    # 3. 插入逻辑
    if START_TAG in current_body and END_TAG in current_body:
        # 如果已经存在日志区块，通过字符串替换，在结束标签前插入新行
        new_body = current_body.replace(END_TAG, f"{csv_line}\n{END_TAG}")
    else:
        # 如果是第一次写入，创建完整的 HTML 结构（使用 <pre> 让它在网页上显示整齐）
        header = "Timestamp,Owner,Status,Sample name,Location,Note,Date"
        log_block = f"""
<hr>
<p><strong>Update history:</strong></p>
{START_TAG}
<pre>
{header}
{csv_line}
{END_TAG}
</pre>
"""
        new_body = current_body + log_block
        
    return new_body


def create_rotor(new_data: dict, category_id: int) -> dict:
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
        
        updated_body = _append_csv_log("", new_data)
            
        rotor_number = new_data.get("Rotor number", "New Rotor")
        
        patch_body = {
            "title": f"Rotor #{rotor_number}",
            "body": updated_body, 
            "metadata": json.dumps(metadata), 
        }
        _api_response = api_instance.patch_item(patch_body, new_id)
        
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

        current_body = current_data.get("body", "")
        updated_body = _append_csv_log(current_body, new_data)
        
        metadata = json.loads(current_data.get("metadata", "{}"))
        if "extra_fields" not in metadata:
            metadata["extra_fields"] = {}

        for key, value in new_data.items():
            if key in metadata["extra_fields"]:
                metadata["extra_fields"][key]["value"] = value
            else:
                metadata["extra_fields"][key] = {"value": value}

        updated_metadata_str = json.dumps(metadata)

        patch_body = {
            "metadata": updated_metadata_str, 
            "body": updated_body, 
            }
        
        _api_response = api_instance.patch_item(patch_body, item_id)
        
        return {"success": True, "message": f"Item {item_id} updated"}

    except Exception as e:
        print(f"Update failed: {e}")
        return {"success": False, "message": str(e)}