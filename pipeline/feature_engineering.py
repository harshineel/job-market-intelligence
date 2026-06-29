import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine, text
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

def compute_features():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM jobs_master", engine)
    print(f"Loaded {len(df)} records")

    # --- Feature 1: skill demand score per skill ---
    # --- Feature 1: skill demand score per skill ---
    skills_df = pd.read_sql("SELECT * FROM skills_exploded", engine)
    print(f"Loaded {len(skills_df)} rows from skills_exploded")
    total_jobs = len(df)
    skill_demand = (
        skills_df.groupby("skill").size() / total_jobs * 100
    ).round(2).reset_index()
    skill_demand.columns = ["skill", "demand_pct"]
    skill_demand = skill_demand.sort_values("demand_pct", ascending=False)

    print("\nTop 15 most in-demand skills:")
    print(skill_demand.head(15).to_string(index=False))

    # --- Feature 2: job velocity per role (simulated over 7 days) ---
    np.random.seed(42)
    roles = df["canonical_title"].unique()
    velocity_data = []
    for role in roles:
        role_count = len(df[df["canonical_title"] == role])
        # Simulate daily counts for past 7 days
        daily = np.random.poisson(role_count / 7, size=7)
        velocity = round((daily[-1] - daily[0]) / max(daily[0], 1) * 100, 2)
        velocity_data.append({"canonical_title": role, "job_velocity": velocity})

    velocity_df = pd.DataFrame(velocity_data)
    print("\nJob velocity by role (% change):")
    print(velocity_df.sort_values("job_velocity", ascending=False).to_string(index=False))

    # --- Feature 3: work mode distribution per role ---
    work_mode_dist = df.groupby(["canonical_title", "work_mode"]).size().unstack(fill_value=0)
    work_mode_dist["remote_pct"] = (
        work_mode_dist.get("remote", 0) /
        work_mode_dist.sum(axis=1) * 100
    ).round(2)
    print("\nRemote % by role:")
    print(work_mode_dist["remote_pct"].sort_values(ascending=False))

    # --- Save velocity back to jobs_master ---
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE jobs_master ADD COLUMN IF NOT EXISTS job_velocity NUMERIC"))
        conn.commit()

    velocity_map = dict(zip(velocity_df["canonical_title"], velocity_df["job_velocity"]))
    with engine.connect() as conn:
        for role, vel in velocity_map.items():
            conn.execute(text("""
                UPDATE jobs_master SET job_velocity = :vel
                WHERE canonical_title = :role
            """), {"vel": vel, "role": role})
        conn.commit()

    # --- Save skill demand as separate table ---
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS skill_demand"))
        conn.commit()

    skill_demand.to_sql("skill_demand", engine, if_exists="replace", index=False)
    print(f"\nSaved skill_demand table with {len(skill_demand)} skills")

    # --- Save skills_df for skill gap model ---
    skills_df.to_sql("skills_exploded", engine, if_exists="replace", index=False)
    print(f"Saved skills_exploded table with {len(skills_df)} rows")

    print("\nFeature engineering complete!")
    return df, skill_demand, skills_df

if __name__ == "__main__":
    compute_features()