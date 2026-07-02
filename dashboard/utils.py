import streamlit as st

USD_TO_INR = 83.5

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

def get_display_salary(df):
    show_inr       = st.session_state.get("show_inr", False)
    country_filter = st.session_state.get("country_filter", "All")
    df = df.copy()

    def convert(row):
        is_india = str(row.get("country", "")).strip() == "India"
        salary   = row["salary_mid"]
        if is_india:
            if show_inr or country_filter == "India":
                return salary
            else:
                return salary / USD_TO_INR
        else:
            if show_inr:
                return salary * USD_TO_INR
            else:
                return salary

    df["display_salary"] = df.apply(convert, axis=1)

    if country_filter == "India" and not st.session_state.get("show_usd", False):
        symbol = "₹"
    elif show_inr:
        symbol = "₹"
    else:
        symbol = "$"

    return symbol, df