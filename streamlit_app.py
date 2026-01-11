import streamlit as st
from app.main import main
from scripts.sample_data_generation import upload_data
from app.logger import logger

logger.info("Starting Streamlit Application...")


@st.cache_resource
def init_data():
    logger.info("Uploading sample data to the database...")
    upload_data()


init_data()
try:
    logger.info("Sample data upload complete. Launching main application...")
    main()
except Exception as e:
    logger.critical(f"Error in main application: {e}")
