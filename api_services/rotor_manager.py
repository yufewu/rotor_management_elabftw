import json
import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from api_services.client import get_shared_items_api_client
from api_services.types import ApiResponse
from utils.data_parser import interpret_rotor_response, parse_data
from utils.supporting_data import STATUS_OPTIONS, HEADER, END_TAG
from typing import Literal


@dataclass
class Rotor:
    """Represents a single Rotor item from eLabFTW."""
    item_id: int
    _response_data: dict = field(init=False, default_factory=dict)
    _parsed_metadata: dict = field(init=False, default_factory=dict)
    

    def get_raw_data(self) -> dict:
        """
        Retrieve the raw data for this rotor, automatically parsing metadata once.
        """
        api_instance = get_shared_items_api_client()
        api_response: ApiResponse = api_instance.get_item(self.item_id, _preload_content=False)  # type: ignore
        
        self._response_data = json.loads(api_response.data.decode("utf-8"))
        #self._parsed_metadata = parse_data(self._response_data.get("metadata"))
        
        return self._response_data
    

    def get_rotor(self) -> dict[str, str]:
        """
        Retrieve and return flattened rotor data.
        """
        if not self._response_data:
            self.get_raw_data()
        
        return interpret_rotor_response(self._response_data)
    
    
    def update(self, 
               new_rotor_information: dict[str, dict[Literal["value", "type", "options"], str | list]], 
               override_timestamp: bool = False
               ) -> dict:
        """
        Update this rotor with new information.
        
        Args:
            new_rotor_information: Dictionary containing fields to update
            override_timestamp: If True, use the timestamp from new_rotor_information instead of current time
            
        Returns:
            Dictionary with success status and message
        """
        api_instance = get_shared_items_api_client()
        
        try:
            self.get_raw_data()  # This will also update self._response_data

            current_body = self._response_data.get("body", "")
            updated_body = self._append_csv_log(current_body, new_rotor_information, override_timestamp)
            
            metadata = parse_data(self._response_data.get("metadata", ""))
            if "extra_fields" not in metadata:
                metadata["extra_fields"] = {}

            for key, value in new_rotor_information.items():
                if key in metadata["extra_fields"]:
                    metadata["extra_fields"][key]["value"] = value
                else:
                    metadata["extra_fields"][key] = {"value": value["value"], "type": value["type"]}
                    if key == "Status":
                        metadata["extra_fields"][key]["options"] = STATUS_OPTIONS

            updated_metadata_str = json.dumps(metadata)

            patch_body = {
                "metadata": updated_metadata_str, 
                "body": updated_body, 
            }
            
            _api_response: ApiResponse = api_instance.patch_item(patch_body, self.item_id)  # type: ignore
            
            return {"success": True, "message": f"Item {self.item_id} updated"}

        except Exception as e:
            print(f"Update failed: {e}")
            return {"success": False, "message": str(e)}
    
    @staticmethod

    
    @staticmethod
    def _append_csv_log(current_body: str, 
                        new_rotor_information: dict[str, dict[Literal["value", "type", "options"], str | list]], 
                        override_timestamp: bool
                        ) -> str:
        """Generate a new body containing CSV logs"""
        

        def get_value(data: dict, key: str, default: str = "") -> str:
            item = data.get(key, {})
            if isinstance(item, dict):
                return str(item.get("value", default))
            return str(item) if item else default
        

        if override_timestamp:
            timestamp = get_value(new_rotor_information, "Date", "")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        note = get_value(new_rotor_information, "Note", "").replace('\n', ' ')
        
        row = [
            timestamp, 
            get_value(new_rotor_information, "Owner"), 
            get_value(new_rotor_information, "Status"), 
            get_value(new_rotor_information, "Sample name"), 
            get_value(new_rotor_information, "Location"), 
            note, 
            get_value(new_rotor_information, "Date"), 
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(row)
        csv_line = output.getvalue().strip()
        
        if HEADER in current_body and END_TAG in current_body:
            new_body = current_body.replace(HEADER, f"{HEADER}\n{csv_line}")
        else:
            log_block = f"""
<hr>
<p><strong>Update history:</strong></p>
<pre>
{HEADER}
{csv_line}
{END_TAG}
</pre>
"""
            new_body = current_body + log_block
            
        return new_body
    

    @classmethod
    def create(cls, 
               new_data: dict[str, dict[Literal["value", "type", "options"], str | list]], 
               category_id: int, 
               override_timestamp: bool = False
               ) -> dict:
        """
        Create a new Rotor in eLabFTW.
        
        Args:
            new_data: A dictionary containing all fields
            category_id: The category ID of your Rotor template in eLabFTW
            override_timestamp: If True, use timestamp from new_data
            
        Returns:
            Dictionary with success status, message, and new_id if successful
        """
        api_instance = get_shared_items_api_client()

        try:
            post_body = {
                "category": category_id,
                "canread_base": 20, 
                "canwrite_base": 10, 
                }
            response: ApiResponse = api_instance.post_item(body=post_body, _preload_content=False)  # type: ignore
            
            location = response.headers.get("Location")
            if location:
                new_id = int(location.split("/")[-1])
            else:
                new_id = None
                return {"success": False, "message": "The request was sent successfully, but the returned ID could not be parsed."}

            metadata = {"extra_fields": {}}
            for key, value in new_data.items():
                metadata["extra_fields"][key] = {"value": value["value"], "type": value["type"]}
                if key == "Status":
                    metadata["extra_fields"][key]["options"] = STATUS_OPTIONS
            
            updated_body = cls._append_csv_log("", new_data, override_timestamp)
            rotor_number = new_data.get("Rotor number", "New Rotor")
            patch_body = {
                "title": f"Rotor #{rotor_number}",
                "body": updated_body, 
                "metadata": json.dumps(metadata), 
            }
            _api_response: ApiResponse = api_instance.patch_item(patch_body, new_id)  # type: ignore
            
            return {"success": True, "message": f"Creation successful! Rotor #{rotor_number} has been generated. (Backend ID: {new_id})", "rotor": cls(new_id)}

        except Exception as e:
            print(f"Create failed: {e}")
            return {"success": False, "message": str(e)}
    

    @classmethod
    def get_all(cls, category_id: int) -> list["Rotor"]:
        """
        Retrieve all rotors from a category.
        
        Args:
            category_id: The category ID to retrieve rotors from
            
        Returns:
            List of Rotor instances (containing only those with valid Rotor numbers)
        """
        api_instance = get_shared_items_api_client()
        
        try:
            api_response: ApiResponse = api_instance.read_items(cat=f"{category_id}", _preload_content=False)  # type: ignore
            
            items = parse_data(api_response.data.decode("utf-8"))
            
            rotors = []
            
            for item in items:
                rotor_information = interpret_rotor_response(item)
                
                if rotor_information.get("Rotor number") != "N/A":
                    rotor_id = item.get("id")
                    if rotor_id:
                        rotors.append(cls(rotor_id))
                    
            return rotors

        except Exception as e:
            print(f"Error fetching all rotors: {e}")
            raise e


# Backward compatibility: Keep existing function signatures for legacy code
def get_single_item(item_id: int) -> dict:
    """
    Retrieve the raw data for a single item based on its ID and automatically parse its metadata once.
    
    DEPRECATED: Use Rotor(item_id).get_raw_data() instead.
    """
    return Rotor(item_id).get_raw_data()


def get_single_rotor(item_id: int) -> dict:
    """
    Retrieve the raw data for a single rotor item based on its ID and parse all meta date into a flattened dictionary.
    
    DEPRECATED: Use Rotor(item_id).get_flattened_data() instead.
    """
    return Rotor(item_id).get_rotor()


def get_all_rotors(category_id: int) -> list[dict]:
    """
    Retrieve all items from eLabFTW, then filter and clean them to create a flattened list of Rotors.
    
    DEPRECATED: Use Rotor.get_all(category_id) instead.
    """
    rotors = Rotor.get_all(category_id)
    return [rotor.get_rotor() for rotor in rotors]


def create_rotor(new_data: dict, category_id: int, override_timestamp: bool = False) -> dict:
    """
    Create a new Rotor in eLabFTW.
    
    DEPRECATED: Use Rotor.create() instead.
    """
    return Rotor.create(new_data, category_id, override_timestamp)


def update_rotor(item_id: int, new_data: dict, override_timestamp: bool = False) -> dict:
    """
    Update the Rotor data with the specified ID.
    
    DEPRECATED: Use Rotor(item_id).update() instead.
    """
    rotor = Rotor(item_id)
    return rotor.update(new_data, override_timestamp)