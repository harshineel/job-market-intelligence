import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import re

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

def load_raw():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM jobs_raw", engine)
    print(f"Loaded {len(df)} raw records")
    return df

def clean_location(loc):
    if not loc:
        return None, None
    loc = str(loc)
    # Extract state
    state_match = re.search(r',\s*([A-Z]{2})', loc)
    state = state_match.group(1) if state_match else None
    # Clean up zip codes and area descriptions
    loc = re.sub(r'\d{5}', '', loc)
    loc = re.sub(r'\(.*?\)', '', loc)
    loc = loc.strip().strip(',').strip()
    return loc, state

def normalize_title(title):
    if not title:
        return "Other"
    title_lower = title.lower()
    if re.search(r'data scien', title_lower):
        return "Data Scientist"
    elif re.search(r'machine learning|ml engineer|mlops', title_lower):
        return "ML Engineer"
    elif re.search(r'data analyst|analytics engineer|bi analyst|business intelligence', title_lower):
        return "Data Analyst"
    elif re.search(r'data engineer', title_lower):
        return "Data Engineer"
    elif re.search(r'software engineer|swe|backend|frontend|full.?stack', title_lower):
        return "Software Engineer"
    elif re.search(r'product manager|program manager', title_lower):
        return "Product Manager"
    elif re.search(r'financial analyst|finance|investment|portfolio', title_lower):
        return "Financial Analyst"
    elif re.search(r'cloud|devops|platform engineer|site reliability|sre', title_lower):
        return "Cloud/DevOps"
    elif re.search(r'ai engineer|artificial intelligence|nlp engineer|computer vision', title_lower):
        return "AI Engineer"
    elif re.search(r'research scientist|applied scientist', title_lower):
        return "Research Scientist"
    elif re.search(r'cybersecurity|security analyst|infosec', title_lower):
        return "Cybersecurity"
    else:
        return "Other"

def detect_experience(title):
    title_lower = str(title).lower()
    if re.search(r'\bsenior\b|\bsr\b|\blead\b|\bstaff\b|\bprincipal\b', title_lower):
        return "Senior"
    elif re.search(r'\bjunior\b|\bjr\b|\bentry\b|\bintern\b', title_lower):
        return "Junior"
    elif re.search(r'\bii\b|\biii\b|\biv\b|\b2\b|\b3\b', title_lower):
        return "Mid"
    else:
        return "Mid"

def assign_domain(canonical_title):
    tech = ["Data Scientist", "ML Engineer", "Data Analyst", "Data Engineer",
            "Software Engineer", "Cloud/DevOps", "AI Engineer", "Research Scientist"]
    finance = ["Financial Analyst"]
    security = ["Cybersecurity"]
    if canonical_title in tech:
        return "Technology"
    elif canonical_title in finance:
        return "Finance"
    elif canonical_title in security:
        return "Security"
    else:
        return "Other"

def clean(df):
    print("Cleaning...")

    # Drop rows with no title
    df = df.dropna(subset=["title"])

    # Clean location
    df[["location_clean", "state"]] = df["location"].apply(
        lambda x: pd.Series(clean_location(x))
    )

    # Normalize titles
    df["canonical_title"] = df["title"].apply(normalize_title)

    # Experience level
    df["experience_level"] = df["title"].apply(detect_experience)

    # Domain
    df["domain"] = df["canonical_title"].apply(assign_domain)

    # Fill nulls
    df["work_mode"] = df["work_mode"].fillna("onsite")
    df["salary_text"] = df["salary_text"].fillna("")

    print(f"Cleaned {len(df)} records")
    print("\nCanonical title distribution:")
    print(df["canonical_title"].value_counts())
    return df

def save_clean(df):
    engine = get_engine()
    # Select and rename columns to match jobs_master
    out = df[[
        "canonical_title", "company", "location_clean", "salary_text",
        "experience_level", "work_mode", "domain", "source","country", "posted_date", "scraped_at"
    ]].rename(columns={"location_clean": "location"})

    out.to_sql("jobs_master", engine, if_exists="replace", index=False)
    print(f"\nSaved {len(out)} records to jobs_master")

if __name__ == "__main__":
    df = load_raw()
    df = clean(df)
    save_clean(df)