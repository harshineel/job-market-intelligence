import streamlit as st

st.set_page_config(
    page_title="Global Job Market Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"], [data-testid="stMarkdownContainer"],
[data-testid="stText"], button,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; letter-spacing: -0.5px; }
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 600 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
div[data-testid="metric-container"] { border-radius: 12px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

col_title, col_toggle = st.columns([8, 1])
with col_toggle:
    dark_mode = st.toggle("Dark", value=True)

if dark_mode:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; }
    [data-testid="stSidebar"] { background-color: #161B27 !important; border-right: 1px solid #252D3D !important; }
    h1,h2,h3 { color: #F0F2F6 !important; }
    p, li { color: #B0B8CC !important; }
    [data-testid="stMetricValue"] { color: #F0F2F6 !important; }
    [data-testid="stMetricLabel"] { color: #8892A4 !important; }
    div[data-testid="metric-container"] { background-color: #161B27 !important; border: 1px solid #252D3D; }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background-color: #F7F8FA !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E8E9EB !important; }
    h1,h2,h3 { color: #0F1117 !important; }
    p, li { color: #3D4151 !important; }
    [data-testid="stMetricValue"] { color: #0F1117 !important; }
    [data-testid="stMetricLabel"] { color: #6B7280 !important; }
    div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E8E9EB; }
    </style>""", unsafe_allow_html=True)

st.sidebar.markdown("## Job Market Intel")
st.sidebar.markdown("---")
st.sidebar.markdown("**Data source:** Indeed")
st.sidebar.markdown("**Records:** 1,481 jobs")
st.sidebar.markdown("**Countries:** USA · India")
st.sidebar.markdown("**Sources:** Indeed · LinkedIn")
st.sidebar.markdown("---")
country_filter = st.sidebar.radio(
    "Country filter",
    ["All", "United States", "India"],
    horizontal=False
)
st.session_state["country_filter"] = country_filter
st.sidebar.markdown("**Roles tracked:** 12")
st.sidebar.markdown("**Skills indexed:** 67")
st.sidebar.markdown("**Last updated:** June 2026")
st.sidebar.markdown("---")
st.sidebar.markdown("**Models trained:**")
st.sidebar.markdown("- Salary predictor (GBM)")
st.sidebar.markdown("- Demand forecast (Prophet)")
st.sidebar.markdown("- Skill gap classifier")

with col_title:
    st.markdown("<p style='font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:#185FA5;font-weight:500;margin-bottom:4px;'>Data Science Project · SRM University</p>", unsafe_allow_html=True)
    st.title("Global Job Market Intelligence")
    st.markdown("End-to-end intelligence across 1,481 live-scraped job postings from Indeed and LinkedIn — salary benchmarks, skill demand, hiring trends, and ML-powered forecasts across USA and India.")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jobs scraped",    "1,481",   "Indeed + LinkedIn")
col2.metric("Avg salary",      "$134K", "AI roles leading")
col3.metric("Skills indexed",  "67",    "across all roles")
col4.metric("ML models built", "3",     "GBM · Prophet · KMeans")

st.markdown("---")
st.markdown("### Explore the dashboard")

c1, c2 = st.columns(2)
with c1:
    st.info("**Market Overview**\n\nJob demand by role, work mode distribution, salary box plots, and top hiring companies.")
    st.success("**Skills Radar**\n\nTop skills by market demand, role vs skill heatmap, and must-have vs emerging skill gap analysis.")

with c2:
    st.info("**Salary Intelligence**\n\nBenchmark salaries by role and experience. Predict your market value using a trained GBM model.")
    st.warning("**Trend Forecast**\n\n60-day demand forecast per role with confidence intervals using Facebook Prophet.")

st.error("**Domain Comparison**\n\nSide-by-side comparison of Technology, Finance, and Security sectors across key metrics.")

st.markdown("---")
st.markdown("### Data pipeline")
p1, p2, p3, p4, p5 = st.columns(5)
p1.markdown("**Scraping**\n\nPlaywright + BS4")
p2.markdown("**Storage**\n\nPostgreSQL")
p3.markdown("**Cleaning**\n\nPandas + spaCy")
p4.markdown("**ML Models**\n\nScikit-learn")
p5.markdown("**Dashboard**\n\nStreamlit + Plotly")

st.markdown("---")
st.caption("Live data · Indeed · June 2026 · Built by Harshinee · SRM University · Data Science")