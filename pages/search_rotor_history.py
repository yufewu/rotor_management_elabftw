import streamlit as st
import pandas as pd
import io
import json
from api_services.rotor_manager import get_all_rotors, get_single_rotor
from utils.supporting_data import HEADER, END_TAG


@st.cache_data(ttl=60)
def fetch_rotors_cached(category_id):
    return get_all_rotors(category_id)


st.set_page_config(page_title="Rotor history", page_icon="🕰️")
st.title("🕰️ Search history by rotor number")
RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]


# Fetch all existing rotors
try:
    with st.spinner("Fetching existing rotor information..."):
        if 'all_rotors' in st.session_state:
            all_rotors = st.session_state.all_rotors
        else:
            all_rotors = fetch_rotors_cached(RESOURCE_CATEGORY_ID)

    rotor_dict = {
        str(r.get("Rotor number")).strip(): r 
        for r in all_rotors if r.get("Rotor number") and r.get("Rotor number") != "N/A"
    }
    
except Exception as e:
    st.error(f"Failed to fetch existing rotor information: {e}")
    st.stop()


# Input a rotor number
input = st.text_input(
    "Write one rotor number", 
    key="rotor_num",
)
rotor_number = input.strip()


# Pull rotor history and parse
if rotor_number:    
    if rotor_number in rotor_dict:
        target_id = rotor_dict[rotor_number]["id"]

        with st.spinner("Getting history..."):
            rotor_data = get_single_rotor(target_id)
            body = rotor_data.get("body", "")
        
        st.divider()
        
        if HEADER in body and END_TAG in body:
            csv_raw_text = f"{HEADER}\n" + body.split(HEADER)[1].split(END_TAG)[0]
            
            clean_csv_text = csv_raw_text.replace("<pre>", "").replace("</pre>", "").strip()
            
            try:
                df_history = pd.read_csv(io.StringIO(clean_csv_text))
                if "Timestamp" in df_history.columns:
                    df_history = df_history.sort_values(by="Timestamp", ascending=False)
                
                st.success(f"Obtained {len(df_history)} history entries. ")
                
                st.dataframe(
                    df_history, 
                    width='stretch', 
                    hide_index=True
                )
                
                csv_export = df_history.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as csv",
                    data=csv_export,
                    file_name=f"Rotor_{target_id}_History.csv",
                    mime="text/csv",
                )
                
            except Exception as e:
                st.error(f"An error occurred while parsing the history log: {e}")
                with st.expander("Check the unparsed history"):
                    st.code(clean_csv_text)
        else: 
            st.info(f"No history found")
    else:
        st.info(f"Rotor number does not exist, please check your input.")