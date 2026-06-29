import pandas as pd
import os
import streamlit as st

def get_data_dir():
    # __file__ is dashboard/data_loader.py
    # data/ is at the project root, one level up from dashboard/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

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