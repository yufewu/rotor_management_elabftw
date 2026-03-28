import streamlit as st
import pandas as pd
from api_services.rotor_manager import Rotor


RESOURCE_CATEGORY_ID = st.secrets["ELAB_RESOURCE_CATEGORY_ID"]
st.set_page_config(page_title="Rotor catalogue", page_icon="🧪", layout="wide")
st.title("Rotor catalogue")

@st.cache_data(ttl=60)
def refresh_database(category_id: int) -> pd.DataFrame:
    try:
        with st.spinner("Fetching data from eLabFTW..."):
            all_rotors = Rotor.get_all(category_id)
            st.session_state.all_rotors = all_rotors

            all_rotors_list = [r.information for r in all_rotors]
            st.session_state.all_rotors_list = all_rotors_list

        if not all_rotors_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_rotors_list)
        
        cols = ["Rotor number", "Status", "Owner", "Sample name", "Location", "Note", "Date"]
        df = df[cols]
        
        return df
        
    except Exception as e:
        st.error(f"Unable to load data: {e}")
        return pd.DataFrame()


col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Force refresh"):
        refresh_database.clear()
        st.rerun()

df = refresh_database(category_id=RESOURCE_CATEGORY_ID)
st.session_state.all_rotors_df = df

user_names = sorted(df['Owner'].unique().tolist())

selected_owner = st.selectbox(
    "Filter by Owner: ",
    options=["all"] + user_names
)

if selected_owner == "all":
    filtered_df = df
else:
    filtered_df = df[df['Owner'] == selected_owner]

if len(filtered_df) <= 1:
    st.write(f"### Found {len(filtered_df)} rotor. ")
else:
    st.write(f"### Found {len(filtered_df)} rotors. ")
st.dataframe(filtered_df, width='stretch', hide_index=True)