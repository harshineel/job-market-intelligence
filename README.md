
# Global Job Market Intelligence Dashboard

An end-to-end data science project that scrapes real job postings from Indeed and LinkedIn, trains ML models, and visualizes insights through an interactive Streamlit dashboard.

**Live demo:** [JobMarketIntelligence.streamlit.app](https://job-market-intelligence-kbf3veappj5kug5bidrdgfb.streamlit.app/)

---

## What it does

- Scrapes 1,481+ job postings from **Indeed** and **LinkedIn** across USA and India
- Stores data in **PostgreSQL** with a full cleaning and feature engineering pipeline
- Trains **3 ML models** for salary prediction, demand forecasting, and skill gap analysis
- Displays insights in a **7-page Streamlit dashboard** with country filter and INR/USD switching

---

## Dashboard pages

| Page | Description |
|---|---|
| Market Overview | Job demand by role, salary distribution, work mode split |
| Salary Intelligence | Salary benchmarks and GBM-powered salary predictor |
| Skills Radar | Top skills heatmap and must-have vs emerging skill gap |
| Trend Forecast | 60-day demand forecast using Facebook Prophet |
| Domain Comparison | Technology vs Finance vs Security radar chart |
| Resume Matcher | Paste your skills → get role fit scores + salary prediction |
| Company Intelligence | Top hiring companies, salary and flexibility rankings |

---

## ML Models

| Model | Algorithm | Purpose |
|---|---|---|
| Salary Predictor | Gradient Boosting (R² 0.65) | Predict salary from role + skills + location |
| Demand Forecaster | Facebook Prophet | 60-day job posting volume forecast |
| Skill Gap Classifier | Frequency-based clustering | Classify skills as must-have / nice-to-have / emerging |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Scraping | Playwright, BeautifulSoup4 |
| Storage | PostgreSQL, pgAdmin 4 |
| Processing | Pandas, SQLAlchemy, spaCy |
| ML | Scikit-learn, Prophet, Joblib |
| Dashboard | Streamlit, Plotly |
| Language | Python 3.13 |

---

## Project Structure
---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/harshinee/job-market-intelligence.git
cd job-market-intelligence
```

### 2. Create virtual environment
```bash
python -m venv jobmarket_env
jobmarket_env\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
- Create database: `job_market_db`
- Run schema SQL from `pipeline/schema.sql`

### 4. Configure environment
Create `.env` file:
DB_USER=postgres
DB_PASSWORD=123456789
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_market_db

### 5. Run the pipeline
```bash
python scrapers/indeed_scraper.py
python pipeline/cleaner.py
python pipeline/enrich_jobs.py
python pipeline/feature_engineering.py
python models/salary_predictor.py
python models/demand_forecaster.py
python models/skill_gap.py
```

### 6. Launch dashboard
```bash
streamlit run dashboard/app.py
```

---

## Data Sources

- **Indeed** — US and India job listings (Playwright scraper)
- **LinkedIn** — US and India job listings (cookie-based session scraper)

---

## Author

**Harshinee** — Data Science, SRM University  
Second-year undergraduate | Intern at Arinox AI, Bangalore
=======
# job-market-intelligence
>>>>>>> bd923588cd6f8dafa9418d05987384613a074b46
