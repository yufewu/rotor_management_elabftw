import time
import streamlit as st
from datetime import datetime
from api_services.rotor_manager import Rotor
from utils.supporting_data import STATUS_OPTIONS
from typing import Literal


if "needs_reset" not in st.session_state:
    st.session_state.needs_reset = False


FORM_FIELDS = {
    "rotor_num": "",
    "status": "Borrowed",
    "owner": "",
    "date": datetime.today().date(), 
    "location": "",
    "sample_name": "",
    "note": "", 
}


for key, default_val in FORM_FIELDS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


if st.session_state.needs_reset:
    for key, default_val in FORM_FIELDS.items():
        st.session_state[key] = default_val
    st.session_state.last_processed_num = None
    st.session_state.needs_reset = False
    st.rerun()


st.set_page_config(page_title="Update rotor status", page_icon="📝")
st.title("📝 Update rotor status")
RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]

with st.sidebar:
    st.info("""
    **Instructions:**
    1. Select "Rotor" from the drop-down menu at the top.
    2. The system will automatically retrieve the current data from eLabFTW.
    3. Click the "Submit" button when you are finished making changes.
    4. All changes will be synchronized to the lab database in real time.
    """)

# Fetch all existing rotors
try:
    with st.spinner("Fetching existing rotor information..."):
        if 'all_rotors' not in st.session_state:
            all_rotors = Rotor.get_all(RESOURCE_CATEGORY_ID)
            st.session_state.all_rotors = all_rotors
        if 'all_rotors_list' not in st.session_state:
            all_rotors_list = [r.information for r in st.session_state.all_rotors]
            st.session_state.all_rotors_list = all_rotors_list


    rotor_dict = {
        str(r.get("Rotor number")).strip(): r for r in st.session_state.all_rotors_list
        if r.get("Rotor number") and r.get("Rotor number") != "N/A"
    }
    
except Exception as e:
    st.error(f"Failed to fetch existing rotor information: {e}")
    st.stop()

# Input a rotor number
input = st.text_input(
    "Write the rotor number", 
    placeholder="Enter an existing rotor number to edit, or a new one to create...", 
    key="rotor_num",
)
rotor_number = input.strip()


# Update rotor information
if rotor_number:

    is_existing = rotor_number in rotor_dict
    
    if is_existing:
        target_rotor_data = rotor_dict[rotor_number]
        target_id = int(target_rotor_data["id"])
    else:
        target_rotor = None
        target_rotor_data = None
        target_id = None
        st.info(f"Rotor number does not exist. You are creating a new one...")

    st.divider()

    with st.form("rotor_form"):
        init_status = target_rotor_data.get("Status", "") if target_rotor_data else FORM_FIELDS["status"]
        init_owner = target_rotor_data.get("Owner", "") if target_rotor_data else FORM_FIELDS["owner"]
        init_date = FORM_FIELDS["date"]
        init_location = target_rotor_data.get("Location", "") if target_rotor_data else FORM_FIELDS["location"]
        init_sample = target_rotor_data.get("Sample name", "") if target_rotor_data else FORM_FIELDS["sample_name"]
        init_note = target_rotor_data.get("Note", "") if target_rotor_data else FORM_FIELDS["note"]

        st.subheader(f"Rotor #{rotor_number}")

        try:
            status_idx = STATUS_OPTIONS.index(st.session_state.status)
        except ValueError:
            status_idx = 1

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Status", options=STATUS_OPTIONS, index=status_idx, key="status")
            st.date_input("Date", value=init_date, key="date")
            st.text_input("Owner", value=init_owner, key="owner", help="Mandatory")
        with col2:
            st.text_input("Sample name", value=init_sample, key="sample_name")
            st.text_input("Location", value=init_location, key="location")
            st.text_area("Note", value=init_note, key="note")

        submit_btn = st.form_submit_button("Submit to eLabFTW")

    if submit_btn:
        date_str = st.session_state.date.strftime("%Y-%m-%d")

        errors = []
        if not st.session_state.owner:
            errors.append("Owner cannot be empty. ")
        if errors:
            for error in errors:
                st.error(error)

        else:
            form_data: dict[str, dict[Literal["value", "type", "options"], str | list]] = {
                "Rotor number": {"value": st.session_state.rotor_num, "type": "text"},
                "Status": {"value": st.session_state.status, "type": "select", "options": STATUS_OPTIONS},
                "Date": {"value": date_str, "type": "date"},
                "Owner": {"value": st.session_state.owner, "type": "text"},
                "Location": {"value": st.session_state.location, "type": "text"},
                "Sample name": {"value": st.session_state.sample_name, "type": "text"},
                "Note": {"value": st.session_state.note, "type": "text"}, 
            }
            
            with st.spinner("Synchronizing..."):
                if is_existing:
                    assert target_id is not None
                    rotor = Rotor(target_id)
                    res = rotor.update(form_data)
                else:
                    res = Rotor.create(form_data, st.secrets["ELAB_RESOURCE_CATEGORY_ID"]) 
                    
            if res["success"]:
                st.success(f"Success! Rotor #{rotor_number} has been updated. ")
                st.balloons()
                
                time.sleep(1.5)
                st.cache_data.clear()
                st.session_state.needs_reset = True
                st.rerun()

            else:
                st.error(f"Failed: {res['message']}")