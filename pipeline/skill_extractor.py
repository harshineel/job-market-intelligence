import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import json

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

SKILLS = [
    # Programming languages
    "python", "r", "sql", "java", "scala", "javascript", "typescript",
    "c++", "c#", "go", "rust", "bash", "matlab", "julia",
    # ML / AI
    "machine learning", "deep learning", "neural network", "nlp",
    "computer vision", "reinforcement learning", "transformers",
    "large language models", "llm", "generative ai", "scikit-learn",
    "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
    # Data tools
    "pandas", "numpy", "spark", "hadoop", "hive", "kafka",
    "airflow", "dbt", "databricks", "snowflake", "redshift",
    "bigquery", "dask", "polars",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "neo4j",
    # Cloud
    "aws", "azure", "gcp", "google cloud", "lambda", "s3",
    "ec2", "sagemaker", "vertex ai", "azure ml",
    # DevOps / MLOps
    "docker", "kubernetes", "mlflow", "kubeflow", "ci/cd",
    "git", "github", "jenkins", "terraform", "ansible",
    # Visualization
    "tableau", "power bi", "looker", "matplotlib", "seaborn",
    "plotly", "d3", "grafana",
    # Statistics
    "statistics", "probability", "regression", "classification",
    "clustering", "time series", "forecasting", "a/b testing",
    "hypothesis testing", "bayesian",
    # Finance specific
    "excel", "vba", "financial modeling", "valuation", "risk analysis",
    "bloomberg", "accounting", "derivatives", "portfolio management",
    # Soft skills
    "communication", "leadership", "collaboration", "problem solving",
    "project management", "agile", "scrum"
]

def extract_skills(text):
    if not text or pd.isna(text):
        return []
    text_lower = str(text).lower()
    return [skill for skill in SKILLS if skill in text_lower]

def run_extraction():
    engine = get_engine()

    # Load jobs_master with title + skills_text from jobs_raw
    query = """
        SELECT jm.id, jm.canonical_title, jm.domain, jr.skills_text, jr.title as raw_title
        FROM jobs_master jm
        JOIN jobs_raw jr ON jm.company = jr.company
            AND jm.posted_date = jr.posted_date
        WHERE jm.skills_list IS NULL
        LIMIT 968
    """
    df = pd.read_sql(query, engine)
    print(f"Loaded {len(df)} records for skill extraction")

    # Extract skills from both raw title and skills_text
    df["extracted_skills"] = df.apply(
        lambda row: list(set(
            extract_skills(str(row["raw_title"])) +
            extract_skills(str(row["skills_text"]))
        )), axis=1
    )

    # Convert to JSON string for storage
    df["skills_json"] = df["extracted_skills"].apply(json.dumps)

    print("\nSample extractions:")
    for _, row in df.head(5).iterrows():
        print(f"  {row['canonical_title']}: {row['extracted_skills']}")

    print(f"\nAvg skills per job: {df['extracted_skills'].apply(len).mean():.1f}")
    print(f"Jobs with 0 skills: {(df['extracted_skills'].apply(len) == 0).sum()}")

    return df

def save_skills(df):
    engine = get_engine()
    # Add skills_list column if not exists
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE jobs_master
            ADD COLUMN IF NOT EXISTS skills_list TEXT
        """))
        conn.commit()

    # Update each row
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                UPDATE jobs_master
                SET skills_list = :skills
                WHERE id = :id
            """), {"skills": row["skills_json"], "id": row["id"]})
        conn.commit()
    print(f"Saved skills for {len(df)} records")

if __name__ == "__main__":
    df = run_extraction()
    save_skills(df)
    print("\nSkill extraction complete!")