from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pandas as pd
import time, random, json, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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

def save_jobs(jobs, country):
    if not jobs:
        print("  No jobs to save.")
        return
    df = pd.DataFrame(jobs)
    df["country"]     = country
    df["source"]      = "linkedin"
    df["scraped_at"]  = datetime.now()
    df["posted_date"] = datetime.today().date()
    engine = get_engine()
    df.to_sql("jobs_raw", engine, if_exists="append", index=False)
    print(f"  Saved {len(df)} jobs to jobs_raw.")

def parse_jobs(html, location):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    cards = soup.find_all("div", class_=lambda x: x and "job-search-card" in x)

    for card in cards:
        try:
            title_el = card.find("h3", class_=lambda x: x and "base-search-card__title" in x)
            title = title_el.get_text(strip=True) if title_el else None

            company_el = card.find("h4", class_=lambda x: x and "base-search-card__subtitle" in x)
            company = company_el.get_text(strip=True) if company_el else None

            location_el = card.find("span", class_=lambda x: x and "job-search-card__location" in x)
            job_location = location_el.get_text(strip=True) if location_el else location

            salary_el = card.find("span", class_=lambda x: x and "job-search-card__salary-info" in x)
            salary = salary_el.get_text(strip=True) if salary_el else None

            work_mode = "onsite"
            if job_location:
                loc_lower = job_location.lower()
                if "remote" in loc_lower:
                    work_mode = "remote"
                elif "hybrid" in loc_lower:
                    work_mode = "hybrid"

            if title:
                jobs.append({
                    "title":            title,
                    "company":          company,
                    "location":         job_location,
                    "salary_text":      salary,
                    "skills_text":      None,
                    "experience_level": None,
                    "work_mode":        work_mode,
                    "domain":           None,
                })
        except Exception as e:
            continue

    return jobs

def load_session(context):
    print("Loading LinkedIn session from cookies...")
    cookie_path = "scrapers/linkedin_cookies.json"

    with open(cookie_path, "r") as f:
        cookies = json.load(f)

    # Clean cookies to fix sameSite values
    cleaned = []
    for cookie in cookies:
        # Fix sameSite field
        same_site = cookie.get("sameSite", "None")
        if same_site not in ("Strict", "Lax", "None"):
            same_site = "None"
        
        cleaned_cookie = {
            "name":     cookie["name"],
            "value":    cookie["value"],
            "domain":   cookie.get("domain", ".linkedin.com"),
            "path":     cookie.get("path", "/"),
            "secure":   cookie.get("secure", False),
            "httpOnly": cookie.get("httpOnly", False),
            "sameSite": same_site,
        }

        # Add expiry only if it exists and is valid
        if "expirationDate" in cookie:
            cleaned_cookie["expires"] = int(cookie["expirationDate"])

        cleaned.append(cleaned_cookie)

    context.add_cookies(cleaned)
    print(f"  Loaded {len(cleaned)} cookies.")

def verify_session(page):
    print("Verifying LinkedIn session...")
    page.goto("https://www.linkedin.com/feed/", timeout=30000)
    time.sleep(random.uniform(3, 5))

    if "feed" in page.url:
        print("  Session active — logged in successfully!")
        return True
    elif "login" in page.url or "authwall" in page.url:
        print("  Session expired — cookies are invalid. Please re-export from browser.")
        return False
    else:
        print(f"  Unknown state: {page.url}")
        return False

def scrape_linkedin(page, query, location, max_pages=3):
    all_jobs = []

    for i in range(max_pages):
        start = i * 25
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={query.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&start={start}"
            f"&trk=public_jobs_jobs-search-bar_search-submit"
        )
        print(f"  Page {i+1}: {query} in {location}")
        try:
            # Navigate with longer timeout and wait until networkidle
            page.goto(url, timeout=60000, wait_until="networkidle")
            time.sleep(random.uniform(5, 9))

            # Check if page is still open
            if page.is_closed():
                print("    Page was closed by LinkedIn — waiting and retrying...")
                time.sleep(15)
                continue

            # Check for auth wall
            if "authwall" in page.url or "login" in page.url:
                print("    Hit auth wall — session may have expired.")
                break

            # Scroll slowly to simulate human behavior
            for _ in range(5):
                page.evaluate("window.scrollBy(0, 500)")
                time.sleep(random.uniform(1.5, 2.5))

            html = page.content()
            jobs = parse_jobs(html, location)
            print(f"    Found {len(jobs)} jobs")
            all_jobs.extend(jobs)

        except Exception as e:
            print(f"    Error on page {i+1}: {e}")
            time.sleep(10)
            continue

        time.sleep(random.uniform(10, 15))

    return all_jobs

if __name__ == "__main__":
    us_queries = [
        "data scientist", "data analyst", "machine learning engineer",
        "data engineer", "software engineer", "product manager",
        "financial analyst", "AI engineer", "cloud engineer",
        "cybersecurity analyst", "devops engineer", "research scientist"
    ]

    india_queries = [
        "data scientist", "data analyst", "machine learning engineer",
        "data engineer", "software engineer", "AI engineer",
        "cloud engineer", "devops engineer", "product manager",
        "financial analyst", "cybersecurity analyst", "research scientist"
    ]

    india_locations = [
        "Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York"
        )
        page = context.new_page()

        load_session(context)

        if not verify_session(page):
            print("Cannot proceed — session invalid.")
            browser.close()
            exit()

        # Scrape US jobs
        print("\n=== Scraping LinkedIn US Jobs ===")
        for q in us_queries:
            print(f"\nQuery: {q}")
            jobs = scrape_linkedin(page, q, "United States", max_pages=3)
            save_jobs(jobs, "United States")
            time.sleep(random.uniform(8, 12))

        # Scrape India jobs
        print("\n=== Scraping LinkedIn India Jobs ===")
        for location in india_locations:
            for q in india_queries:
                print(f"\nQuery: {q} in {location}")
                jobs = scrape_linkedin(page, q, location, max_pages=2)
                save_jobs(jobs, "India")
                time.sleep(random.uniform(8, 12))

        browser.close()

    print("\nDone! Run the pipeline next:")
    print("  python pipeline/cleaner.py")
    print("  python pipeline/enrich_jobs.py")
    print("  python pipeline/feature_engineering.py")