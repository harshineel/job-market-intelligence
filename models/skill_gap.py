import pandas as pd
import json
import joblib
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="123456789",
    host="localhost",
    port=5432,
    database="job_market_db"
)

def get_engine():
    return create_engine(connection_url)

def classify_skills_for_role(role, df):
    role_df = df[df["canonical_title"] == role]
    total = len(role_df)
    if total == 0:
        return {}

    skill_freq = {}
    for skills_json in role_df["skills_list"]:
        try:
            skills = json.loads(skills_json)
            for skill in skills:
                skill_freq[skill] = skill_freq.get(skill, 0) + 1
        except:
            continue

    result = {"must_have": [], "nice_to_have": [], "emerging": []}
    for skill, count in skill_freq.items():
        pct = count / total
        if pct >= 0.6:
            result["must_have"].append(skill)
        elif pct >= 0.25:
            result["nice_to_have"].append(skill)
        else:
            result["emerging"].append(skill)

    return result

def run():
    engine = get_engine()
    df = pd.read_sql(
        "SELECT canonical_title, skills_list FROM jobs_master WHERE skills_list IS NOT NULL",
        engine
    )
    print(f"Loaded {len(df)} records")

    roles = df["canonical_title"].unique()
    skill_gap_map = {}

    print("\nSkill gap classification:")
    for role in sorted(roles):
        result = classify_skills_for_role(role, df)
        skill_gap_map[role] = result
        print(f"\n{role}")
        print(f"  Must-have    : {result['must_have']}")
        print(f"  Nice-to-have : {result['nice_to_have']}")
        print(f"  Emerging     : {result['emerging']}")

    joblib.dump(skill_gap_map, "models/skill_gap.pkl")
    print("\nSaved: models/skill_gap.pkl")
    print("\nDone!")

if __name__ == "__main__":
    run()