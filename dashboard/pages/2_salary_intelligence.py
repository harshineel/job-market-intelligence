import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import scipy.sparse as sp
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.data_loader import load_jobs

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
        if value >= 1000000:
            return f"${value/1000000:.2f}M"
        else:
            return f"${value:,.0f}"

@st.cache_resource
def load_model():
    model    = joblib.load("models/salary_model.pkl")
    encoders = joblib.load("models/salary_encoders.pkl")
    return model, encoders

st.title("Salary Intelligence")
st.markdown("Benchmark salaries by role, experience, and location — and predict your market value.")
st.markdown("---")

df = load_data()
df = apply_filter(df)
model, encoders = load_model()

country = st.session_state.get("country_filter", "All")
symbol  = "₹" if country == "India" else "$"

top_role    = df.groupby("canonical_title")["salary_mid"].mean().idxmax()
top_sal     = df.groupby("canonical_title")["salary_mid"].mean().max()
bottom_role = df.groupby("canonical_title")["salary_mid"].mean().idxmin()
bottom_sal  = df.groupby("canonical_title")["salary_mid"].mean().min()
avg_all     = df["salary_mid"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Highest avg salary", top_role,    format_salary(top_sal, symbol))
col2.metric("Lowest avg salary",  bottom_role, format_salary(bottom_sal, symbol))
col3.metric("Overall avg salary", format_salary(avg_all, symbol), "all roles")

st.markdown("---")
st.subheader("Average salary by role")

avg_sal = (
    df[df["canonical_title"] != "Other"]
    .groupby("canonical_title")["salary_mid"]
    .mean().reset_index()
)
avg_sal.columns = ["Role", "Avg Salary"]
avg_sal = avg_sal.sort_values("Avg Salary", ascending=True)
avg_sal["Label"] = avg_sal["Avg Salary"].apply(lambda x: format_salary(x, symbol))

fig1 = px.bar(
    avg_sal, x="Avg Salary", y="Role", orientation="h",
    color="Avg Salary",
    color_continuous_scale=["#EEEDFE","#7F77DD","#3C3489"],
    text="Label"
)
fig1.update_traces(textposition="outside", marker_line_width=0)
fig1.update_layout(
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=100, t=10, b=10),
    height=400
)
fig1.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
fig1.update_yaxes(showgrid=False, tickfont=dict(size=13))
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Salary by experience level")
    exp_sal = (
        df[df["canonical_title"] != "Other"]
        .groupby(["canonical_title", "experience_level"])["salary_mid"]
        .mean().reset_index()
    )
    fig2 = px.bar(
        exp_sal, x="canonical_title", y="salary_mid",
        color="experience_level",
        barmode="group",
        color_discrete_map={
            "Junior": "#B5D4F4",
            "Mid":    "#378ADD",
            "Senior": "#0C447C"
        },
        labels={
            "canonical_title":  "Role",
            "salary_mid":       "Avg Salary",
            "experience_level": "Level"
        }
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=340,
        xaxis_tickangle=-30
    )
    if symbol == "₹":
        fig2.update_yaxes(
            tickvals=[500000, 1000000, 1500000, 2000000, 2500000, 3000000],
            ticktext=["₹5L", "₹10L", "₹15L", "₹20L", "₹25L", "₹30L"]
        )
    else:
        fig2.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Salary by work mode")
    mode_sal = (
        df[df["canonical_title"] != "Other"]
        .groupby("work_mode")["salary_mid"]
        .mean().reset_index()
    )
    mode_sal["Label"] = mode_sal["salary_mid"].apply(lambda x: format_salary(x, symbol))
    fig3 = px.bar(
        mode_sal, x="work_mode", y="salary_mid",
        color="work_mode",
        text="Label",
        color_discrete_map={
            "remote": "#1D9E75",
            "hybrid": "#378ADD",
            "onsite": "#534AB7"
        },
        labels={"work_mode": "Work Mode", "salary_mid": "Avg Salary"}
    )
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=40),
        height=340
    )
    if symbol == "₹":
        fig3.update_yaxes(
            tickvals=[500000, 1000000, 1500000, 2000000, 2500000],
            ticktext=["₹5L", "₹10L", "₹15L", "₹20L", "₹25L"]
        )
    else:
        fig3.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("Salary predictor")
st.markdown("Enter your profile to get a predicted market salary.")

col1, col2, col3 = st.columns(3)
with col1:
    role = st.selectbox("Job role", sorted(df["canonical_title"].unique().tolist()))
with col2:
    exp = st.selectbox("Experience level", ["Junior", "Mid", "Senior"])
with col3:
    mode = st.selectbox("Work mode", ["onsite", "hybrid", "remote"])

skills_map = {
    "Data Scientist":    ["python","sql","machine learning","statistics","pandas","scikit-learn"],
    "ML Engineer":       ["python","pytorch","tensorflow","docker","kubernetes","mlflow"],
    "Data Analyst":      ["sql","excel","tableau","power bi","python","statistics"],
    "Data Engineer":     ["python","sql","spark","kafka","airflow","aws"],
    "Software Engineer": ["python","java","docker","kubernetes","git","aws"],
    "Product Manager":   ["communication","agile","scrum","sql","excel","leadership"],
    "Financial Analyst": ["excel","financial modeling","sql","python","tableau","statistics"],
    "Cloud/DevOps":      ["aws","azure","docker","kubernetes","terraform","python"],
    "AI Engineer":       ["python","pytorch","llm","transformers","generative ai","docker"],
    "Research Scientist":["python","pytorch","deep learning","statistics","nlp","tensorflow"],
    "Cybersecurity":     ["python","bash","networking","aws","linux","risk analysis"],
    "Other":             ["communication","excel","sql","project management","python"]
}

if st.button("Predict my salary"):
    try:
        title_enc  = encoders["title"].transform([role])[0]
        exp_enc    = encoders["exp"].transform([exp])[0]
        mode_enc   = encoders["mode"].transform([mode])[0]
        domain_enc = encoders["domain"].transform(
            [df[df["canonical_title"] == role]["domain"].iloc[0]]
        )[0]

        skills_str = " ".join(skills_map.get(role, []))
        skills_vec = encoders["tfidf"].transform([skills_str])
        cat = sp.csr_matrix([[title_enc, exp_enc, mode_enc, domain_enc]])
        X   = sp.hstack([cat, skills_vec])

        pred = model.predict(X)[0]
        low  = pred * 0.9
        high = pred * 1.1

        st.success(f"Predicted salary: **{format_salary(pred, symbol)}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Low estimate",  format_salary(low, symbol))
        c2.metric("Mid estimate",  format_salary(pred, symbol))
        c3.metric("High estimate", format_salary(high, symbol))

    except Exception as e:
        st.error(f"Prediction error: {e}")