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

ROLE_SKILLS = {
    "Data Scientist": [
        ["python", "sql", "machine learning", "statistics", "pandas", "scikit-learn"],
        ["python", "sql", "deep learning", "tensorflow", "nlp", "spark"],
        ["python", "r", "machine learning", "statistics", "tableau", "a/b testing"],
        ["python", "sql", "pytorch", "deep learning", "statistics", "databricks"],
        ["python", "sql", "machine learning", "pandas", "azure", "power bi"]
    ],
    "ML Engineer": [
        ["python", "pytorch", "tensorflow", "docker", "kubernetes", "mlflow"],
        ["python", "pytorch", "transformers", "llm", "aws", "docker"],
        ["python", "tensorflow", "kubernetes", "spark", "mlflow", "git"],
        ["python", "pytorch", "deep learning", "kubeflow", "ci/cd", "docker"],
        ["python", "tensorflow", "generative ai", "mlflow", "azure", "kubernetes"]
    ],
    "Data Analyst": [
        ["sql", "excel", "tableau", "power bi", "python", "statistics"],
        ["sql", "excel", "power bi", "python", "communication", "looker"],
        ["sql", "excel", "tableau", "statistics", "r", "a/b testing"],
        ["sql", "excel", "tableau", "python", "collaboration", "dbt"],
        ["sql", "power bi", "python", "statistics", "excel", "databricks"]
    ],
    "Data Engineer": [
        ["python", "sql", "spark", "kafka", "airflow", "aws"],
        ["python", "sql", "dbt", "snowflake", "airflow", "docker"],
        ["python", "sql", "spark", "bigquery", "kafka", "terraform"],
        ["python", "sql", "databricks", "airflow", "kafka", "git"],
        ["python", "sql", "spark", "redshift", "dbt", "postgresql"]
    ],
    "Software Engineer": [
        ["python", "java", "docker", "kubernetes", "git", "aws"],
        ["python", "javascript", "docker", "git", "ci/cd", "redis"],
        ["java", "python", "kubernetes", "git", "terraform", "go"],
        ["python", "java", "aws", "docker", "postgresql", "agile"],
        ["python", "typescript", "docker", "git", "aws", "mongodb"]
    ],
    "Product Manager": [
        ["communication", "agile", "scrum", "sql", "excel", "leadership"],
        ["communication", "agile", "sql", "tableau", "leadership", "a/b testing"],
        ["communication", "scrum", "excel", "project management", "collaboration"],
        ["communication", "agile", "sql", "leadership", "problem solving"],
        ["communication", "scrum", "sql", "excel", "agile", "statistics"]
    ],
    "Financial Analyst": [
        ["excel", "financial modeling", "sql", "python", "tableau", "statistics"],
        ["excel", "financial modeling", "bloomberg", "valuation", "risk analysis", "sql"],
        ["excel", "financial modeling", "python", "accounting", "statistics", "tableau"],
        ["excel", "sql", "financial modeling", "tableau", "portfolio management", "python"],
        ["excel", "financial modeling", "risk analysis", "python", "valuation", "statistics"]
    ],
    "Cloud/DevOps": [
        ["aws", "azure", "docker", "kubernetes", "terraform", "python"],
        ["aws", "docker", "kubernetes", "terraform", "ansible", "ci/cd"],
        ["azure", "gcp", "docker", "kubernetes", "jenkins", "python"],
        ["aws", "terraform", "docker", "kubernetes", "python", "monitoring"],
        ["gcp", "kubernetes", "docker", "terraform", "ci/cd", "bash"]
    ],
    "AI Engineer": [
        ["python", "pytorch", "llm", "transformers", "generative ai", "docker"],
        ["python", "pytorch", "llm", "aws", "mlflow", "deep learning"],
        ["python", "transformers", "generative ai", "nlp", "docker", "kubernetes"],
        ["python", "pytorch", "computer vision", "deep learning", "tensorflow", "mlflow"],
        ["python", "llm", "generative ai", "transformers", "azure", "mlflow"]
    ],
    "Research Scientist": [
        ["python", "pytorch", "deep learning", "statistics", "nlp", "tensorflow"],
        ["python", "pytorch", "statistics", "nlp", "r", "bayesian"],
        ["python", "tensorflow", "deep learning", "statistics", "computer vision", "spark"],
        ["python", "pytorch", "transformers", "nlp", "statistics", "deep learning"],
        ["python", "tensorflow", "bayesian", "statistics", "r", "nlp"]
    ],
    "Cybersecurity": [
        ["python", "bash", "networking", "aws", "linux", "risk analysis"],
        ["python", "networking", "linux", "risk analysis", "elasticsearch", "git"],
        ["bash", "networking", "aws", "linux", "communication", "problem solving"],
        ["python", "linux", "networking", "risk analysis", "git", "bash"],
        ["python", "aws", "networking", "linux", "elasticsearch", "bash"]
    ],
    "Other": [
        ["communication", "excel", "sql", "project management", "python"],
        ["communication", "excel", "collaboration", "problem solving", "sql"],
        ["excel", "sql", "python", "communication", "project management"],
        ["communication", "project management", "excel", "sql", "agile"],
        ["python", "sql", "excel", "communication", "collaboration"]
    ]
}

ROLE_SALARY = {
    "Data Scientist":    (90000,  160000),
    "ML Engineer":       (110000, 185000),
    "Data Analyst":      (60000,  110000),
    "Data Engineer":     (95000,  165000),
    "Software Engineer": (95000,  175000),
    "Product Manager":   (100000, 170000),
    "Financial Analyst": (65000,  120000),
    "Cloud/DevOps":      (100000, 170000),
    "AI Engineer":       (120000, 200000),
    "Research Scientist":(110000, 180000),
    "Cybersecurity":     (85000,  150000),
    "Other":             (55000,  100000),
}

SENIORITY_MULTIPLIER = {
    "Junior": 0.80,
    "Mid":    1.00,
    "Senior": 1.30,
}

def assign_skills(role, idx):
    pool = ROLE_SKILLS.get(role, ROLE_SKILLS["Other"])
    return json.dumps(pool[idx % len(pool)])

INDIA_SALARY_INR = {
    "Data Scientist":    (800000,  2500000),
    "ML Engineer":       (1000000, 3000000),
    "Data Analyst":      (400000,  1200000),
    "Data Engineer":     (800000,  2200000),
    "Software Engineer": (600000,  2500000),
    "Product Manager":   (1000000, 2800000),
    "Financial Analyst": (500000,  1500000),
    "Cloud/DevOps":      (700000,  2000000),
    "AI Engineer":       (1200000, 3500000),
    "Research Scientist":(900000,  2800000),
    "Cybersecurity":     (600000,  1800000),
    "Other":             (350000,  900000),
}

def assign_salary(role, experience_level, country=None):
    multiplier = SENIORITY_MULTIPLIER.get(experience_level, 1.0)
    if country == "India":
        low, high = INDIA_SALARY_INR.get(role, (350000, 900000))
    else:
        low, high = ROLE_SALARY.get(role, (55000, 100000))
    mid = np.random.randint(int(low * multiplier), int(high * multiplier))
    salary_min = int(mid * 0.9)
    salary_max = int(mid * 1.1)
    return salary_min, salary_max, mid

def enrich():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM jobs_master", engine)
    print(f"Loaded {len(df)} records")

    np.random.seed(42)

    # Assign skills with variation using row index
    df["skills_list"] = [
        assign_skills(row["canonical_title"], idx)
        for idx, (_, row) in enumerate(df.iterrows())
    ]

    # Assign salary
    df[["salary_min", "salary_max", "salary_mid"]] = df.apply(
        lambda row: pd.Series(assign_salary(
            row["canonical_title"],
            row["experience_level"],
            row.get("country", "United States")
        )),
        axis=1
    )

    # Salary index vs market median per role
    df["currency"] = df["country"].apply(lambda x: "INR" if x == "India" else "USD")
    medians = df.groupby("canonical_title")["salary_mid"].median()
    df["salary_index"] = df.apply(
        lambda row: round(row["salary_mid"] / medians[row["canonical_title"]], 2), axis=1
    )

    print("\nSample enriched records:")
    print(df[["canonical_title", "experience_level", "salary_mid", "skills_list"]].head(5).to_string())

    print(f"\nAvg salary by role:")
    print(df.groupby("canonical_title")["salary_mid"].mean().round(0).sort_values(ascending=False))

    # Bulk save using temp table
    temp_df = df[[
        "canonical_title", "company", "posted_date",
        "skills_list", "salary_min", "salary_max", "salary_mid", "salary_index", "currency"
    ]].copy()

    temp_df.to_sql("enrich_temp", engine, if_exists="replace", index=False)

    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE jobs_master jm
            SET
                skills_list  = et.skills_list,
                salary_min   = et.salary_min,
                salary_max   = et.salary_max,
                salary_mid   = et.salary_mid,
                salary_index = et.salary_index
            FROM enrich_temp et
            WHERE jm.canonical_title = et.canonical_title
            AND   jm.company         = et.company
            AND   jm.posted_date     = et.posted_date
        """))
        conn.execute(text("DROP TABLE IF EXISTS enrich_temp"))
        conn.commit()

    print(f"\nSaved {len(df)} records to jobs_master")
    print("Enrichment complete!")

if __name__ == "__main__":
    enrich()