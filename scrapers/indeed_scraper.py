from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
import time, random, re
from datetime import datetime

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

def parse_jobs(html, country="United States"):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    cards = soup.find_all("div", class_=re.compile("job_seen_beacon|cardOutline"))
    for card in cards:
        try:
            title = card.find("span", attrs={"title": True})
            title = title["title"].strip() if title else None

            company = card.find("span", attrs={"data-testid": "company-name"})
            company = company.get_text(strip=True) if company else None

            location = card.find("div", attrs={"data-testid": "text-location"})
            location = location.get_text(strip=True) if location else None

            salary = card.find("div", attrs={"data-testid": "attribute_snippet_testid"})
            salary = salary.get_text(strip=True) if salary else None

            snippet = card.find("div", class_=re.compile("underShelfFooter|snippet"))
            skills_text = snippet.get_text(strip=True) if snippet else None

            if title:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_text": salary,
                    "skills_text": skills_text,
                    "experience_level": None,
                    "work_mode": detect_work_mode(location, skills_text),
                    "domain": None,
                    "source": "indeed",
                    "country": country,
                    "posted_date": datetime.today().date(),
                    "scraped_at": datetime.now()
                })
        except Exception as e:
            continue
    return jobs

def detect_work_mode(location, text):
    combined = f"{location or ''} {text or ''}".lower()
    if "remote" in combined:
        return "remote"
    elif "hybrid" in combined:
        return "hybrid"
    else:
        return "onsite"

def save_jobs(jobs):
    if not jobs:
        print("No jobs to save.")
        return
    df = pd.DataFrame(jobs)
    engine = get_engine()
    df.to_sql("jobs_raw", engine, if_exists="append", index=False)
    print(f"Saved {len(df)} jobs to jobs_raw.")

def scrape_indeed(query="data scientist", location="United States", max_pages=3):
    all_jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        for i in range(max_pages):
            start = i * 10
            url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}&start={start}"
            print(f"Scraping page {i+1}: {url}")
            try:
                page.goto(url, timeout=30000)
                time.sleep(random.uniform(3, 5))
                html = page.content()
                jobs = parse_jobs(html, country=location)
                print(f"  Found {len(jobs)} jobs on page {i+1}")
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  Error on page {i+1}: {e}")
                continue
        browser.close()
    return all_jobs

if __name__ == "__main__":
    us_queries = [
        "data scientist", "data analyst", "machine learning engineer",
        "data engineer", "software engineer", "product manager",
        "financial analyst", "cloud engineer", "AI engineer",
        "cybersecurity analyst", "devops engineer", "business analyst"
    ]

    india_queries = [
        "data scientist", "data analyst", "machine learning engineer",
        "data engineer", "software engineer", "product manager",
        "financial analyst", "cloud engineer", "AI engineer",
        "cybersecurity analyst", "devops engineer", "business analyst"
    ]

    # Scrape US jobs
    print("=== Scraping US Jobs ===")
    for q in us_queries:
        print(f"\nScraping US: {q}")
        jobs = scrape_indeed(query=q, location="United States", max_pages=3)
        save_jobs(jobs)

    # Scrape India jobs
    print("\n=== Scraping India Jobs ===")
    for q in india_queries:
        print(f"\nScraping India: {q}")
        jobs = scrape_indeed(query=q, location="India", max_pages=3)
        save_jobs(jobs)

    print("\nDone!")