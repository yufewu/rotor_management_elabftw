import elabapi_python
import streamlit as st
import sys


def get_items_api_client():
    """
    Initializes an eLabFTW API client.
    Rreads credentials from Streamlit Secrets or a local configuration file.
    """
    try:
        API_KEY = st.secrets["ELAB_API_KEY"]
        API_HOST = st.secrets["ELAB_API_HOST"]
        
        configuration = elabapi_python.Configuration()
        #configuration.api_key['api_key'] = API_KEY
        configuration.api_key['Authorization'] = API_KEY
        configuration.host = API_HOST
        configuration.debug = True
        
        api_client = elabapi_python.ApiClient(configuration)
        #api_client.set_default_header(header_name="Authorization", header_value=API_KEY)
        
        return elabapi_python.ItemsApi(api_client)

    except KeyError:
        st.error("API configuration not found! Please check .streamlit/secrets.toml or your cloud-based Secrets settings.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize the API client: {e}")
        st.stop()


@st.cache_resource
def get_shared_items_api_client():
    return get_items_api_client()