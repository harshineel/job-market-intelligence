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
st.title("🏢 Domain Comparison")
st.markdown("Compare Technology, Finance, and Security sectors across key metrics.")
st.markdown("---")

df = load_data()
df = apply_filter(df)
domains = ["Technology","Finance","Security"]
domain_df = df[df["domain"].isin(domains)]

col1, col2, col3 = st.columns(3)
for col, domain, color in zip(
    [col1, col2, col3], domains, ["#185FA5","#1D9E75","#D85A30"]
):
    d = domain_df[domain_df["domain"] == domain]
    col.metric(f"{domain} jobs",  len(d))
    col.metric("Avg salary", f"${d['salary_mid'].mean():,.0f}")
    remote_pct = (d["work_mode"] == "remote").mean() * 100
    col.metric("Remote %", f"{remote_pct:.1f}%")

st.markdown("---")
st.subheader("Salary comparison across domains")
fig1 = px.box(
    domain_df, x="domain", y="salary_mid",
    color="domain",
    color_discrete_map={
        "Technology":"#185FA5",
        "Finance":"#1D9E75",
        "Security":"#D85A30"
    },
    labels={"domain":"Domain","salary_mid":"Salary (USD)"}
)
fig1.update_layout(
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=10,b=10),
    height=340
)
fig1.update_yaxes(tickprefix="$", tickformat=",")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("Domain radar — multi-metric comparison")

metrics = {}
for domain in domains:
    d = domain_df[domain_df["domain"] == domain]
    metrics[domain] = {
        "Avg salary (normalized)": d["salary_mid"].mean() / 200000 * 100,
        "Job volume":              len(d) / len(domain_df) * 100,
        "Remote %":                (d["work_mode"]=="remote").mean() * 100,
        "Senior %":                (d["experience_level"]=="Senior").mean() * 100,
        "Hybrid %":                (d["work_mode"]=="hybrid").mean() * 100,
    }

categories = list(list(metrics.values())[0].keys())
colors = {
    "Technology": {"line": "#185FA5", "fill": "rgba(24,95,165,0.15)"},
    "Finance":    {"line": "#1D9E75", "fill": "rgba(29,158,117,0.15)"},
    "Security":   {"line": "#D85A30", "fill": "rgba(216,90,48,0.15)"}
}

fig2 = go.Figure()
for domain, vals in metrics.items():
    values = list(vals.values())
    fig2.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=domain,
        line_color=colors[domain]["line"],
        fillcolor=colors[domain]["fill"]
    ))

fig2.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0,100])),
    showlegend=True,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=30,b=10),
    height=420
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Work mode by domain")
wm = domain_df.groupby(["domain","work_mode"]).size().reset_index(name="count")
fig3 = px.bar(
    wm, x="domain", y="count", color="work_mode",
    barmode="group",
    color_discrete_map={"remote":"#1D9E75","hybrid":"#378ADD","onsite":"#534AB7"},
    labels={"domain":"Domain","count":"Job Count","work_mode":"Work Mode"}
)
fig3.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=10,b=10),
    height=320
)
st.plotly_chart(fig3, use_container_width=True)