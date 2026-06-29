import streamlit as st

def apply_theme():
    dark_mode = st.session_state.get("dark_mode", True)
    if dark_mode:
        st.markdown("""<style>
        [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; }
        [data-testid="stSidebar"] { background-color: #161B27 !important; border-right: 1px solid #252D3D !important; }
        h1,h2,h3 { color: #F0F2F6 !important; }
        p, li { color: #B0B8CC !important; }
        [data-testid="stMetricValue"] { color: #F0F2F6 !important; }
        [data-testid="stMetricLabel"] { color: #8892A4 !important; }
        div[data-testid="metric-container"] { background-color: #161B27 !important; border: 1px solid #252D3D; border-radius: 12px; padding: 1rem; }
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
        [data-testid="stAppViewContainer"] { background-color: #F7F8FA !important; }
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E8E9EB !important; }
        h1,h2,h3 { color: #0F1117 !important; }
        p, li { color: #3D4151 !important; }
        [data-testid="stMetricValue"] { color: #0F1117 !important; }
        [data-testid="stMetricLabel"] { color: #6B7280 !important; }
        div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E8E9EB; border-radius: 12px; padding: 1rem; }
        </style>""", unsafe_allow_html=True)

def apply_font():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"], [data-testid="stMarkdownContainer"],
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], button {
        font-family: 'Inter', sans-serif !important;
    }
    h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; letter-spacing: -0.5px; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 600 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.72rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

def get_currency_settings(df):
    """
    Returns symbol and conversion info based on country filter and currency toggle.
    Also converts salary columns in df to display currency.
    """
    country = st.session_state.get("country_filter", "All")
    show_inr = st.session_state.get("show_inr", False)

    USD_TO_INR = 83.5

    df = df.copy()

    if country == "India":
        # India jobs — salaries already in INR
        symbol = "₹"
        df["display_salary"] = df["salary_mid"]
    elif country == "United States":
        if show_inr:
            # Convert USD to INR
            symbol = "₹"
            df["display_salary"] = df["salary_mid"] * USD_TO_INR
        else:
            symbol = "$"
            df["display_salary"] = df["salary_mid"]
    else:
        # All countries mixed
        if show_inr:
            symbol = "₹"
            df["display_salary"] = df.apply(
                lambda r: r["salary_mid"] if r.get("currency") == "INR"
                else r["salary_mid"] * USD_TO_INR, axis=1
            )
        else:
            # Show USD for US jobs, convert INR to USD for India jobs
            symbol = "$"
            df["display_salary"] = df.apply(
                lambda r: r["salary_mid"] if r.get("currency") != "INR"
                else r["salary_mid"] / USD_TO_INR, axis=1
            )

    return symbol, df

def format_salary(value, symbol):
    if symbol == "₹":
        if value >= 10000000:
            return f"₹{value/10000000:.2f} Cr"
        elif value >= 100000:
            return f"₹{value/100000:.2f} L"
        else:
            return f"₹{value:,.0f}"
    else:
        if value >= 1000000:
            return f"${value/1000000:.2f}M"
        else:
            return f"${value:,.0f}"

def apply_filter(df):
    country = st.session_state.get("country_filter", "All")
    if country != "All":
        df = df[df["country"] == country]
    return df

def render_currency_toggle():
    country = st.session_state.get("country_filter", "All")
    if country == "United States":
        st.toggle("Show in ₹ (INR)", key="show_inr")
    elif country == "India":
        st.toggle("Show in $ (USD)", key="show_usd")
        if st.session_state.get("show_usd"):
            st.session_state["show_inr"] = False
    else:
        st.toggle("Convert all to ₹ (INR)", key="show_inr")