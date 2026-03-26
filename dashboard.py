import streamlit as st
import pandas as pd
from api_services.rotor_manager import get_all_rotors


@st.cache_data(ttl=60)
def fetch_rotors_cached(category_id):
    return get_all_rotors(category_id)


def refresh_database(category_id):
    try:
        with st.spinner("Fetching data from eLabFTW..."):
            all_rotors = fetch_rotors_cached(category_id)
            st.session_state.all_rotors = all_rotors

        if all_rotors:
            df = pd.DataFrame(all_rotors)
            
            cols = ["Rotor number", "Status", "Owner", "Sample name", "Location", "Note", "Date"]
            df = df[cols]
            st.session_state.all_rotors_df = df
            
            st.dataframe(df, width='stretch', hide_index=True)

        else:
            st.info("There is currently no data in the database.")

    except Exception as e:
        st.error(f"Unable to load data: {e}")

RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]

st.set_page_config(page_title="Rotor catalogue", page_icon="🧪", layout="wide")
st.title("Rotor catalogue")

col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Force refresh"):
        fetch_rotors_cached.clear()
        st.rerun()

refresh_database(category_id=RESOURCE_CATEGORY_ID)
