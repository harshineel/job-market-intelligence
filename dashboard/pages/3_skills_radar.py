import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="123456789",
    host="localhost",
    port=5432,
    database="job_market_db"
)

@st.cache_data
def load_data():
    engine = create_engine(connection_url)
    df = pd.read_sql("SELECT * FROM jobs_master", engine)
    sd = pd.read_sql("SELECT * FROM skill_demand", engine)
    return df, sd
def apply_filter(df):
    country = st.session_state.get("country_filter", "All")
    if country != "All":
        df = df[df["country"] == country]
    return df
@st.cache_resource
def load_skill_gap():
    return joblib.load("models/skill_gap.pkl")

st.title("🛠 Skills Radar")
st.markdown("Discover which skills dominate the market and what you need for any role.")
st.markdown("---")

df, skill_demand = load_data()
df = apply_filter(df)
skill_gap = load_skill_gap()

st.subheader("Top 15 most in-demand skills")
top_skills = skill_demand.head(15).sort_values("demand_pct", ascending=True)
fig1 = px.bar(
    top_skills, x="demand_pct", y="skill", orientation="h",
    color="demand_pct",
    color_continuous_scale=["#E1F5EE","#1D9E75","#085041"],
    text=top_skills["demand_pct"].apply(lambda x: f"{x:.1f}%")
)
fig1.update_traces(textposition="outside")
fig1.update_layout(
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=50,t=10,b=10),
    height=420,
    xaxis_title="% of jobs requiring this skill"
)
fig1.update_xaxes(showgrid=False)
fig1.update_yaxes(showgrid=False)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("Skill gap analysis by role")
st.markdown("Select a role to see which skills are essential vs emerging.")

selected_role = st.selectbox("Choose a role", sorted(skill_gap.keys()))
gap = skill_gap[selected_role]

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Must-have skills**")
    for s in gap["must_have"]:
        st.markdown(f"🔵 {s}")
with col2:
    st.markdown("**Nice-to-have skills**")
    if gap["nice_to_have"]:
        for s in gap["nice_to_have"]:
            st.markdown(f"🟡 {s}")
    else:
        st.markdown("*None identified*")
with col3:
    st.markdown("**Emerging skills**")
    if gap["emerging"]:
        for s in gap["emerging"]:
            st.markdown(f"🟢 {s}")
    else:
        st.markdown("*None identified*")

st.markdown("---")
st.subheader("Skills heatmap — role vs skill")

import json
import numpy as np

roles = [r for r in df["canonical_title"].unique() if r != "Other"]
top_skill_names = skill_demand.head(12)["skill"].tolist()

matrix = []
for role in roles:
    role_df = df[df["canonical_title"] == role]
    row = []
    for skill in top_skill_names:
        count = role_df["skills_list"].apply(
            lambda x: skill in json.loads(x) if x else False
        ).sum()
        row.append(round(count / max(len(role_df), 1) * 100, 1))
    matrix.append(row)

fig2 = go.Figure(data=go.Heatmap(
    z=matrix,
    x=top_skill_names,
    y=roles,
    colorscale=[[0,"#E6F1FB"],[0.5,"#378ADD"],[1,"#0C447C"]],
    text=[[f"{v}%" for v in row] for row in matrix],
    texttemplate="%{text}",
    textfont={"size":11}
))
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=10,b=10),
    height=400,
    xaxis_tickangle=-30
)
st.plotly_chart(fig2, use_container_width=True)