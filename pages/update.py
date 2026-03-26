import time
import streamlit as st
from datetime import datetime
from api_services.rotor_manager import get_all_rotors, update_rotor, create_rotor
from utils.supporting_data import status_list


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
        if 'all_rotors' in st.session_state:
            all_rotors = st.session_state.all_rotors
        else:
            all_rotors = get_all_rotors(RESOURCE_CATEGORY_ID)

    rotor_dict = {
        str(r.get("Rotor number")).strip(): r 
        for r in all_rotors if r.get("Rotor number") and r.get("Rotor number") != "N/A"
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
        target_rotor = rotor_dict[rotor_number]
        target_id = target_rotor["id"]

    else:
        target_rotor = None
        target_id = None
        st.info(f"Rotor number does not exist. You are creating a new one...")

    st.divider()

    with st.form("rotor_form"):
        init_status = target_rotor.get("Status", "") if target_rotor else FORM_FIELDS["status"]
        init_owner = target_rotor.get("Owner", "") if target_rotor else FORM_FIELDS["owner"]
        init_date = FORM_FIELDS["date"]
        init_location = target_rotor.get("Location", "") if target_rotor else FORM_FIELDS["location"]
        init_sample = target_rotor.get("Sample name", "") if target_rotor else FORM_FIELDS["sample_name"]
        init_note = target_rotor.get("Note", "") if target_rotor else FORM_FIELDS["note"]

        st.subheader(f"Rotor #{rotor_number}")

        try:
            status_idx = status_list.index(st.session_state.status)
        except ValueError:
            status_idx = 1

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Status", options=status_list, index=status_idx, key="status")
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
            form_data = {
                "Rotor number": st.session_state.rotor_num,
                "Status": st.session_state.status,
                "Date": date_str,
                "Owner": st.session_state.owner,
                "Location": st.session_state.location,
                "Sample name": st.session_state.sample_name,
                "Note": st.session_state.note, 
            }
            
            with st.spinner("Synchronizing..."):
                if is_existing:
                    assert target_id is not None
                    res = update_rotor(target_id, form_data)
                else:
                    res = create_rotor(form_data, category_id = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]) 
                    
            if res["success"]:
                st.success(f"Success! Rotor #{rotor_number} has been updated. ")
                st.balloons()
                
                time.sleep(1.5)
                st.cache_data.clear()
                st.session_state.needs_reset = True
                st.rerun()

            else:
                st.error(f"Failed: {res['message']}")