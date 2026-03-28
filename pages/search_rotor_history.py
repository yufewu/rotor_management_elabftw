import streamlit as st
import pandas as pd
import io
from api_services.rotor_manager import Rotor
from utils.supporting_data import HEADER, END_TAG


@st.cache_data(ttl=60)
def fetch_rotors_cached(category_id):
    rotor_instances = Rotor.get_all(category_id)
    return [rotor.get_rotor() for rotor in rotor_instances]


st.set_page_config(page_title="Rotor history", page_icon="🕰️")
st.title("🕰️ Search history by rotor number")
RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]


# Fetch all existing rotors
try:
    with st.spinner("Fetching existing rotor information..."):
        if 'rotor_instances' in st.session_state:
            rotor_instances = st.session_state.rotor_instances
        else:
            rotor_instances = Rotor.get_all(RESOURCE_CATEGORY_ID)
            st.session_state.rotor_instances = rotor_instances

    rotor_dict = {
        str(r.get_rotor().get("Rotor number")).strip(): r for r in rotor_instances
        if r.get_rotor().get("Rotor number") and r.get_rotor().get("Rotor number") != "N/A"
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
        target_rotor = rotor_dict[rotor_number]
        target_id = int(target_rotor.get_rotor()["id"])

        with st.spinner("Getting history..."):
            rotor_data = target_rotor.get_raw_data()
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