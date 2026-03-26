import streamlit as st
import pandas as pd

st.set_page_config(page_title="Search by Owner", page_icon="🔍")

st.title("🔍 Search by Owner")

if 'all_rotors_df' not in st.session_state:
    st.warning("Please fetch the data from the homepage first!")

if 'all_rotors_df' in st.session_state: 
    df = st.session_state.all_rotors_df

    user_names = sorted(df['Owner'].unique().tolist())

    selected_owner = st.selectbox(
        "Filter by Owner: ",
        options=["all"] + user_names
    )

    if selected_owner == "all":
        filtered_df = df
    else:
        filtered_df = df[df['Owner'] == selected_owner]

    st.write(f"### Found {len(filtered_df)} rotors. ")
    st.dataframe(filtered_df, width='stretch', hide_index=True)