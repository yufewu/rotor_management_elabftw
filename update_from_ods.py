import pandas as pd
import streamlit as st
import time
import argparse
from pandas._libs.tslibs.parsing import DateParseError
from api_services.rotor_manager import Rotor
from utils.supporting_data import STATUS_OPTIONS
from typing import Literal


def parse_args():
    parser = argparse.ArgumentParser(description="Migrate Rotor data from ODS/Excel to eLabFTW.")
    parser.add_argument(
         "-f",  "--filename", 
        help="Path to the .ods file (e.g., ./data/test.ods)", 
    )

    return parser.parse_args()


RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]

ODS_FILE = parse_args().filename
df = pd.read_excel(ODS_FILE, engine="odf", dtype={"Rotor number": str})

df['Date_str'] = df['Date'].dt.strftime("%Y-%m-%d").fillna("")
#df = df.sort_values(by='Date', ascending=True)

df['Status'] = df['Status'].fillna("Borrowed")
for field_to_fill_with_empty_string in ['Owner', 'Sample name', 'Location', 'Note']: 
    df[field_to_fill_with_empty_string] = df[field_to_fill_with_empty_string].fillna("")


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


print(f"Start migrating {len(df)} records...")

success_count = 0
fail_count = 0

for index, row in df.iterrows():
    rotor_number = str(row['Rotor number']).strip()

    form_data: dict[str, dict[Literal["value", "type", "options"], str | list]] = {
                "Rotor number": {"value": rotor_number, "type": "text"},
                "Status": {"value": str(row.get("Status", "Borrowed")), "type": "select", "options": STATUS_OPTIONS},
                "Date": {"value": row['Date_str'], "type": "date"},
                "Owner": {"value": str(row.get("Owner", "")), "type": "text"},
                "Location": {"value": str(row.get("Location", "")), "type": "text"},
                "Sample name": {"value": str(row.get("Sample name", "")), "type": "text"},
                "Note": {"value": str(row.get("Note", "")), "type": "text"}, 
            }
    
    print(f"Migrating [{index}/{len(df)}] Rotor {rotor_number}...")
    if rotor_number in rotor_dict:
        target_rotor = rotor_dict[rotor_number]
        target_id = target_rotor["id"]

        res = Rotor(target_id).update(form_data)
        if res["success"]:
            success_count += 1
        else:
            print(f"Falied: {res['message']}")
            fail_count += 1

    else:
        res = Rotor.create(form_data, st.secrets["ELAB_RESOURCE_CATEGORY_ID"])
        if res["success"]:
            success_count += 1
            rotor_dict[rotor_number] = {"id": res["new_id"], "Rotor number": rotor_number}
        else:
            print(f"Falied: {res['message']}")
            fail_count += 1
    
    time.sleep(1)

print(f"""
--- Migration completed ---
Successful: {success_count} entries
Failed: {fail_count} entries
----------------
""")