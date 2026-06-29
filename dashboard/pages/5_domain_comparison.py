import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from dashboard.utils import apply_theme, format_salary, get_display_salary
try:
    from dashboard.data_loader import load_jobs
except:
    from data_loader import load_jobs

def load_data():
    return load_jobs()

def apply_filter(df):
    country = st.session_state.get("country_filter", "All")
    if country != "All":
        df = df[df["country"] == country]
    return df

st.title("Domain Comparison")
apply_theme()
st.markdown("Compare Technology, Finance, and Security sectors across key metrics.")
st.markdown("---")

df = load_data()
df = apply_filter(df)
symbol, df = get_display_salary(df)

domains = ["Technology", "Finance", "Security"]
domain_df = df[df["domain"].isin(domains)]

col1, col2, col3 = st.columns(3)
for col, domain in zip([col1, col2, col3], domains):
    d = domain_df[domain_df["domain"] == domain]
    col.metric(f"{domain} jobs", len(d))
    avg = d["display_salary"].mean() if len(d) > 0 else 0
    col.metric("Avg salary", format_salary(avg, symbol))
    remote_pct = (d["work_mode"] == "remote").mean() * 100 if len(d) > 0 else 0
    col.metric("Remote %", f"{remote_pct:.1f}%")

st.markdown("---")
st.subheader("Salary comparison across domains")

fig1 = px.box(
    domain_df, x="domain", y="display_salary",
    color="domain",
    color_discrete_map={
        "Technology": "#185FA5",
        "Finance":    "#1D9E75",
        "Security":   "#D85A30"
    },
    labels={"domain": "Domain", "display_salary": f"Salary ({symbol})"}
)
fig1.update_layout(
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    height=340
)
if symbol == "₹":
    fig1.update_yaxes(
        tickvals=[500000,1000000,1500000,2000000,2500000,3000000],
        ticktext=["₹5L","₹10L","₹15L","₹20L","₹25L","₹30L"]
    )
else:
    fig1.update_yaxes(tickprefix="$", tickformat=",")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("Domain radar — multi-metric comparison")

max_salary = domain_df["display_salary"].max()
if max_salary == 0:
    max_salary = 1

metrics = {}
for domain in domains:
    d = domain_df[domain_df["domain"] == domain]
    if len(d) == 0:
        metrics[domain] = {k: 0 for k in ["Avg salary (normalized)", "Job volume", "Remote %", "Senior %", "Hybrid %"]}
        continue
    metrics[domain] = {
        "Avg salary (normalized)": d["display_salary"].mean() / max_salary * 100,
        "Job volume":              len(d) / max(len(domain_df), 1) * 100,
        "Remote %":                (d["work_mode"] == "remote").mean() * 100,
        "Senior %":                (d["experience_level"] == "Senior").mean() * 100,
        "Hybrid %":                (d["work_mode"] == "hybrid").mean() * 100,
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
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=30, b=10),
    height=420
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Work mode by domain")
wm = domain_df.groupby(["domain", "work_mode"]).size().reset_index(name="count")
fig3 = px.bar(
    wm, x="domain", y="count", color="work_mode",
    barmode="group",
    color_discrete_map={
        "remote": "#1D9E75",
        "hybrid": "#378ADD",
        "onsite": "#534AB7"
    },
    labels={"domain": "Domain", "count": "Job Count", "work_mode": "Work Mode"}
)
fig3.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    height=320
)
st.plotly_chart(fig3, use_container_width=True)