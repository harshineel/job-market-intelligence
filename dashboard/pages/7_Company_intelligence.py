import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import scipy.sparse as sp
import os, sys

# Path fix for Streamlit Cloud
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from dashboard.data_loader import load_jobs

@st.cache_resource
def load_model():
    model    = joblib.load(os.path.join(ROOT, "models", "salary_model.pkl"))
    encoders = joblib.load(os.path.join(ROOT, "models", "salary_encoders.pkl"))
    return model, encoders

def load_data():
    return load_jobs()

def apply_filter(df):
    country = st.session_state.get("country_filter", "All")
    if country != "All":
        df = df[df["country"] == country]
    return df

def format_salary(value, symbol):
    if symbol == "₹":
        if value >= 10000000:
            return f"₹{value/10000000:.2f} Cr"
        elif value >= 100000:
            return f"₹{value/100000:.2f} L"
        else:
            return f"₹{value:,.0f}"
    else:
        return f"${value:,.0f}"

st.title("Company Intelligence")
st.markdown("Discover which companies are hiring the most, paying the best, and offering the most flexibility.")
st.markdown("---")

df = load_data()
df = apply_filter(df)

country = st.session_state.get("country_filter", "All")
symbol  = "₹" if country == "India" else "$"

# Company stats
company_stats = df.groupby("company").agg(
    openings    =("canonical_title", "count"),
    avg_salary  =("salary_mid", "mean"),
    remote_pct  =("work_mode", lambda x: (x == "remote").mean() * 100),
    hybrid_pct  =("work_mode", lambda x: (x == "hybrid").mean() * 100),
    senior_pct  =("experience_level", lambda x: (x == "Senior").mean() * 100),
).reset_index()

company_stats["flexibility_score"] = (
    company_stats["remote_pct"] * 0.6 +
    company_stats["hybrid_pct"] * 0.4
).round(1)

company_stats["avg_salary_fmt"] = company_stats["avg_salary"].apply(
    lambda x: format_salary(x, symbol)
)

top_companies = company_stats.sort_values("openings", ascending=False).head(20)

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies tracked", df["company"].nunique())
col2.metric("Most openings",     top_companies.iloc[0]["company"])
col3.metric("Best avg salary",
    company_stats.sort_values("avg_salary", ascending=False).iloc[0]["company"])
col4.metric("Most flexible",
    company_stats.sort_values("flexibility_score", ascending=False).iloc[0]["company"])

st.markdown("---")
st.subheader("Top 15 hiring companies")

top15 = top_companies.head(15).sort_values("openings", ascending=True)
fig1 = px.bar(
    top15, x="openings", y="company", orientation="h",
    color="openings",
    color_continuous_scale=["#1a2744","#185FA5","#63B3ED"],
    text="openings"
)
fig1.update_traces(textposition="outside", marker_line_width=0)
fig1.update_layout(
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=50, t=10, b=10),
    height=420
)
fig1.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
fig1.update_yaxes(showgrid=False, tickfont=dict(size=12))
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top paying companies")
    top_pay = company_stats[company_stats["openings"] >= 2].sort_values(
        "avg_salary", ascending=False
    ).head(12)
    top_pay = top_pay.sort_values("avg_salary", ascending=True)
    top_pay["label"] = top_pay["avg_salary"].apply(lambda x: format_salary(x, symbol))

    fig2 = px.bar(
        top_pay, x="avg_salary", y="company", orientation="h",
        color="avg_salary",
        color_continuous_scale=["#1a2744","#534AB7","#9F7AEA"],
        text="label"
    )
    fig2.update_traces(textposition="outside", marker_line_width=0)
    fig2.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=80, t=10, b=10),
        height=380
    )
    fig2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig2.update_yaxes(showgrid=False, tickfont=dict(size=12))
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Most flexible companies")
    top_flex = company_stats[company_stats["openings"] >= 2].sort_values(
        "flexibility_score", ascending=False
    ).head(12)
    top_flex = top_flex.sort_values("flexibility_score", ascending=True)

    fig3 = px.bar(
        top_flex, x="flexibility_score", y="company", orientation="h",
        color="flexibility_score",
        color_continuous_scale=["#1a2744","#1D9E75","#68D391"],
        text=top_flex["flexibility_score"].apply(lambda x: f"{x:.1f}%")
    )
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=60, t=10, b=10),
        height=380
    )
    fig3.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig3.update_yaxes(showgrid=False, tickfont=dict(size=12))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("Company deep dive")
st.markdown("Select a company to see detailed hiring breakdown.")
if country == "All":
    st.warning("Set the country filter to USA or India for accurate salary data in the company deep dive.")
selected_company = st.selectbox(
    "Choose a company",
    sorted(df["company"].dropna().unique().tolist())
)

company_df = df[df["company"] == selected_company]
stats = company_stats[company_stats["company"] == selected_company].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total openings",    int(stats["openings"]))
c2.metric("Avg salary", format_salary(stats["avg_salary"], symbol),
          "USD" if symbol == "$" else "INR")
c3.metric("Remote %",          f"{stats['remote_pct']:.1f}%")
c4.metric("Senior roles %",    f"{stats['senior_pct']:.1f}%")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Roles being hired**")
    role_counts = company_df["canonical_title"].value_counts().reset_index()
    role_counts.columns = ["Role", "Count"]
    fig4 = px.pie(
        role_counts, values="Count", names="Role", hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=280
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("**Work mode breakdown**")
    wm_counts = company_df["work_mode"].value_counts().reset_index()
    wm_counts.columns = ["Mode", "Count"]
    fig5 = px.pie(
        wm_counts, values="Count", names="Mode", hole=0.5,
        color_discrete_map={
            "remote": "#1D9E75",
            "hybrid": "#378ADD",
            "onsite": "#534AB7"
        }
    )
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=280
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("All companies overview")

display_cols = ["company", "openings", "avg_salary_fmt",
                "remote_pct", "hybrid_pct", "senior_pct", "flexibility_score"]

display = company_stats[display_cols].sort_values("openings", ascending=False).rename(columns={
    "company":           "Company",
    "openings":          "Openings",
    "avg_salary_fmt":    "Avg Salary",
    "remote_pct":        "Remote %",
    "hybrid_pct":        "Hybrid %",
    "senior_pct":        "Senior %",
    "flexibility_score": "Flexibility Score"
})

display["Remote %"]        = display["Remote %"].round(1)
display["Hybrid %"]        = display["Hybrid %"].round(1)
display["Senior %"]        = display["Senior %"].round(1)
display["Flexibility Score"] = display["Flexibility Score"].round(1)

st.dataframe(display.reset_index(drop=True), use_container_width=True, height=400)