import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import scipy.sparse as sp
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

@st.cache_resource
def load_model():
    model    = joblib.load(os.path.join(ROOT, "models", "salary_model.pkl"))
    encoders = joblib.load(os.path.join(ROOT, "models", "salary_encoders.pkl"))
    return model, encoders

@st.cache_resource
def load_skill_gap():
    return joblib.load(os.path.join(ROOT, "models", "skill_gap.pkl"))

ALL_SKILLS = [
    "python", "r", "sql", "java", "scala", "javascript", "typescript",
    "c++", "go", "bash", "matlab",
    "machine learning", "deep learning", "nlp", "computer vision",
    "reinforcement learning", "transformers", "llm", "generative ai",
    "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost",
    "pandas", "numpy", "spark", "hadoop", "kafka", "airflow",
    "dbt", "databricks", "snowflake", "redshift", "bigquery",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "mlflow",
    "kubeflow", "ci/cd", "git", "terraform", "ansible",
    "tableau", "power bi", "looker", "matplotlib", "plotly",
    "statistics", "probability", "a/b testing", "hypothesis testing",
    "bayesian", "time series", "forecasting",
    "excel", "financial modeling", "valuation", "risk analysis",
    "bloomberg", "accounting", "portfolio management",
    "communication", "leadership", "agile", "scrum",
    "project management", "collaboration", "problem solving",
    "networking", "linux", "cybersecurity"
]

st.title("Resume Skill Matcher")
apply_theme()
st.markdown("Enter your skills and discover which roles you're best suited for — with salary predictions and skill gap analysis.")
st.markdown("---")

df = load_data()
df = apply_filter(df)
model, encoders = load_model()
skill_gap = load_skill_gap()
symbol, df = get_display_salary(df)

USD_TO_INR = 83.5

st.subheader("Your skills")
st.markdown("Select all the skills you currently have:")

selected_skills = st.multiselect(
    "Search and select your skills",
    options=sorted(ALL_SKILLS),
    default=["python", "sql", "machine learning"]
)

exp_level = st.selectbox("Your experience level", ["Junior", "Mid", "Senior"])
work_pref = st.selectbox("Preferred work mode", ["onsite", "hybrid", "remote"])

st.markdown("---")

if st.button("Find my best roles", type="primary"):
    if not selected_skills:
        st.warning("Please select at least one skill.")
    else:
        selected_set = set(selected_skills)
        roles = [r for r in skill_gap.keys() if r != "Other"]
        scores = []

        for role in roles:
            gap          = skill_gap[role]
            must_have    = set(gap.get("must_have", []))
            nice_to_have = set(gap.get("nice_to_have", []))
            emerging     = set(gap.get("emerging", []))

            must_match     = len(selected_set & must_have)
            nice_match     = len(selected_set & nice_to_have)
            emerging_match = len(selected_set & emerging)

            score = (
                (must_match / max(len(must_have), 1)) * 60 +
                (nice_match / max(len(nice_to_have), 1)) * 30 +
                (emerging_match / max(len(emerging), 1)) * 10
            )

            scores.append({
                "role":             role,
                "score":            round(score, 1),
                "must_match":       must_match,
                "total_must":       len(must_have),
                "missing_must":     must_have - selected_set,
                "missing_nice":     nice_to_have - selected_set,
                "missing_emerging": emerging - selected_set
            })

        scores_df = pd.DataFrame(scores).sort_values("score", ascending=False)

        st.subheader("Your best role matches")
        top3   = scores_df.head(3)
        cols   = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, (col, (_, row)) in enumerate(zip(cols, top3.iterrows())):
            with col:
                st.markdown(f"### {medals[i]} {row['role']}")
                st.metric("Match score", f"{row['score']:.1f}%")
                st.markdown(f"**Skills matched:** {row['must_match']} / {row['total_must']} must-have")

        st.markdown("---")
        st.subheader("Role fit scores")
        fig1 = px.bar(
            scores_df, x="score", y="role", orientation="h",
            color="score",
            color_continuous_scale=["#1a2744","#185FA5","#63B3ED"],
            text=scores_df["score"].apply(lambda x: f"{x:.1f}%")
        )
        fig1.update_traces(textposition="outside", marker_line_width=0)
        fig1.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=60, t=10, b=10),
            height=380,
            yaxis=dict(autorange="reversed")
        )
        fig1.update_xaxes(showgrid=False, showticklabels=False, range=[0, 110])
        fig1.update_yaxes(showgrid=False)
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")
        st.subheader("Predicted salary for your best match")
        best_role = scores_df.iloc[0]["role"]

        try:
            title_enc  = encoders["title"].transform([best_role])[0]
            exp_enc    = encoders["exp"].transform([exp_level])[0]
            mode_enc   = encoders["mode"].transform([work_pref])[0]
            domain_enc = encoders["domain"].transform(
                [df[df["canonical_title"] == best_role]["domain"].iloc[0]]
            )[0]

            skills_str = " ".join(selected_skills)
            skills_vec = encoders["tfidf"].transform([skills_str])
            cat  = sp.csr_matrix([[title_enc, exp_enc, mode_enc, domain_enc]])
            X    = sp.hstack([cat, skills_vec])
            pred = model.predict(X)[0]
            low  = pred * 0.9
            high = pred * 1.1

            # Convert if needed — model trained on USD
            show_inr = st.session_state.get("show_inr", False)
            country  = st.session_state.get("country_filter", "All")
            if country == "India" or show_inr:
                pred = pred * USD_TO_INR
                low  = low  * USD_TO_INR
                high = high * USD_TO_INR

            c1, c2, c3 = st.columns(3)
            c1.metric("Role",            best_role)
            c2.metric("Predicted salary", format_salary(pred, symbol))
            c3.metric("Experience",      exp_level)

            st.success(f"Salary range: {format_salary(low, symbol)} — {format_salary(high, symbol)}")

        except Exception as e:
            st.warning(f"Could not predict salary: {e}")

        st.markdown("---")
        st.subheader(f"Skill gap analysis — {best_role}")
        best_gap = skill_gap.get(best_role, {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Must-have skills**")
            for s in best_gap.get("must_have", []):
                st.markdown(f"{'✅' if s in selected_set else '❌'} {s}")
        with col2:
            st.markdown("**Nice-to-have skills**")
            for s in best_gap.get("nice_to_have", []):
                st.markdown(f"{'✅' if s in selected_set else '⬜'} {s}")
        with col3:
            st.markdown("**Emerging skills**")
            for s in best_gap.get("emerging", []):
                st.markdown(f"{'✅' if s in selected_set else '🔮'} {s}")

        st.markdown("---")
        st.subheader("Skills to learn next")
        missing_must = scores_df.iloc[0]["missing_must"]
        missing_nice = scores_df.iloc[0]["missing_nice"]

        if missing_must:
            st.error(f"**Critical gaps (must-have):** {', '.join(missing_must)}")
        if missing_nice:
            st.warning(f"**Recommended (nice-to-have):** {', '.join(missing_nice)}")
        if not missing_must and not missing_nice:
            st.success("You have all the key skills for this role! Focus on emerging skills to stay ahead.")