import pandas as pd
import os
import streamlit as st

def get_data_dir():
    # Works both locally and on Streamlit Cloud
    current = os.path.dirname(os.path.abspath(__file__))
    # Try going up one level to find data/
    parent = os.path.dirname(current)
    data_path = os.path.join(parent, "data")
    if os.path.exists(data_path):
        return data_path
    # Fallback — same directory
    return os.path.join(current, "data")

DATA_DIR = get_data_dir()

@st.cache_data
def load_jobs():
    return pd.read_csv(os.path.join(DATA_DIR, "jobs_master.csv"))

@st.cache_data
def load_skill_demand():
    return pd.read_csv(os.path.join(DATA_DIR, "skill_demand.csv"))

@st.cache_data
def load_skills_exploded():
    return pd.read_csv(os.path.join(DATA_DIR, "skills_exploded.csv"))