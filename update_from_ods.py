import pandas as pd
import streamlit as st
import time
import argparse
from datetime import datetime
from pandas._libs.tslibs.parsing import DateParseError
from api_services.rotor_manager import update_rotor, create_rotor, get_all_rotors


def parse_args():
    parser = argparse.ArgumentParser(description="Migrate Rotor data from ODS/Excel to eLabFTW.")
    parser.add_argument(
         "-f",  "--filename", 
        help="Path to the .ods file (e.g., ./data/test.ods)", 
    )

    return parser.parse_args()


RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]

ODS_FILE = parse_args().filename
df = pd.read_excel(ODS_FILE, engine="odf")

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Date'] = df['Date'].fillna("")
df = df.sort_values(by='Date', ascending=True)

df['Status'] = df['Status'].fillna("Borrowed")
df['Note'] = df['Note'].fillna("")

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


print(f"Start migrating {len(df)} records...")

success_count = 0
fail_count = 0

for index, row in df.iterrows():
    rotor_number = str(row['Rotor number']).strip()

    form_data = {
                "Rotor number":rotor_number, 
                "Status": str(row.get("Status", "Borrowed")),
                "Owner": str(row.get("Owner", "")),
                "Location": str(row.get("Location", "")),
                "Sample name": str(row.get("Sample name", "")),
                "Note": str(row.get("Note", "")),
                "Date": row['Date'].strftime("%Y-%m-%d")
            }
    
    print(f"Migrating [{index}/{len(df)}] Rotor {rotor_number}...")
    if rotor_number in rotor_dict:
        target_rotor = rotor_dict[rotor_number]
        target_id = target_rotor["id"]

        res = update_rotor(target_id, form_data)
        if res["success"]:
            success_count += 1
        else:
            print(f"Falied: {res['message']}")
            fail_count += 1

    else:
        res = create_rotor(form_data, category_id = st.secrets["ELAB_RESOURCE_CATEGORY_ID"])
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