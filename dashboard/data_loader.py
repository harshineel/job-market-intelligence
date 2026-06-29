import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_jobs():
    return pd.read_csv(os.path.join(DATA_DIR, "jobs_master.csv"))

def load_skill_demand():
    return pd.read_csv(os.path.join(DATA_DIR, "skill_demand.csv"))

def load_skills_exploded():
    return pd.read_csv(os.path.join(DATA_DIR, "skills_exploded.csv"))