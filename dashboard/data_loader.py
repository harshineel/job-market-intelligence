import pandas as pd
import os
import streamlit as st

def get_data_dir():
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"),
        os.path.join("/mount/src/job-market-intelligence", "data"),
        os.path.join(os.getcwd(), "data"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    return os.path.join(os.getcwd(), "data")

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