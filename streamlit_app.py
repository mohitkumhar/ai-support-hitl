import streamlit as st
from app.main import main
from scripts.sample_data_generation import upload_data

@st.cache_resource
def init_data():
    upload_data()

init_data()
main()
