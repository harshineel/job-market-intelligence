import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from dashboard.utils import apply_theme, apply_filter, format_salary, get_display_salary

sys.path.insert(0, "/mount/src/job-market-intelligence")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

country = st.session_state.get("country_filter", "All")
st.title("Market Overview")
if country != "All":
    st.info(f"Showing jobs from: **{country}**")
    st.markdown("A snapshot of the current global job market across all roles and geographies.")
st.markdown("---")

df = load_data()
df = apply_filter(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total jobs",        len(df))
col2.metric("Unique companies",  df["company"].nunique())
col3.metric("Avg salary",        f"${df['display_salary'].mean():,.0f}")
col4.metric("Domains tracked",   df["domain"].nunique())

st.markdown("---")
st.subheader("Job demand by role")

role_counts = (
    df[df["canonical_title"] != "Other"]["canonical_title"]
    .value_counts().reset_index()
)
role_counts.columns = ["Role", "Count"]

fig1 = px.bar(
    role_counts, x="Count", y="Role", orientation="h",
    color="Count",
    color_continuous_scale=["#E6F1FB","#378ADD","#0C447C"],
    text="Count"
)
fig1.update_traces(textposition="outside")
fig1.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=30, t=10, b=10),
    height=380
)
fig1.update_xaxes(showgrid=False, zeroline=False)
fig1.update_yaxes(showgrid=False)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Work mode split")
    wm = df["work_mode"].value_counts().reset_index()
    wm.columns = ["Mode", "Count"]
    fig2 = px.pie(
        wm, values="Count", names="Mode", hole=0.5,
        color_discrete_sequence=["#185FA5","#1D9E75","#D85A30"]
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    fig2.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=10),
        height=280
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Experience level split")
    exp = df["experience_level"].value_counts().reset_index()
    exp.columns = ["Level", "Count"]
    fig3 = px.pie(
        exp, values="Count", names="Level", hole=0.5,
        color_discrete_sequence=["#534AB7","#1D9E75","#D85A30"]
    )
    fig3.update_traces(textposition="inside", textinfo="percent+label")
    fig3.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=10),
        height=280
    )
    st.plotly_chart(fig3, use_container_width=True)
apply_theme()
st.markdown("---")
st.subheader("Salary distribution by role")

box_df = df[df["canonical_title"] != "Other"].sort_values("display_salary", ascending=False)
fig4 = px.box(
    box_df, x="canonical_title", y="display_salary",
    color="canonical_title",
    color_discrete_sequence=px.colors.qualitative.Set2,
    labels={"canonical_title": "Role", "display_salary": "Salary (USD)"}
)
fig4.update_layout(
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=10,b=10),
    height=380,
    xaxis_tickangle=-30
)
fig4.update_yaxes(tickprefix="$", tickformat=",")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("Data explorer")
role_filter = st.selectbox("Filter by role", ["All"] + sorted(df["canonical_title"].unique().tolist()))
filtered = df if role_filter == "All" else df[df["canonical_title"] == role_filter]
st.dataframe(
    filtered[["canonical_title","company","location","domain","experience_level","work_mode","display_salary"]]
    .rename(columns={
        "canonical_title":"Role","company":"Company","location":"Location",
        "domain":"Domain","experience_level":"Level",
        "work_mode":"Work Mode","display_salary":"Salary (USD)"
    }).head(50),
    use_container_width=True
)