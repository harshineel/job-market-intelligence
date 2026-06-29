import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import numpy as np
import scipy.sparse as sp
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.data_loader import load_jobs

def load_data():
    return load_jobs()

@st.cache_resource
def load_model():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model    = joblib.load(os.path.join(base, "models", "salary_model.pkl"))
    encoders = joblib.load(os.path.join(base, "models", "salary_encoders.pkl"))
    return model, encoders

@st.cache_resource
def load_skill_gap():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    joblib.load(os.path.join(base, "models", "skill_gap.pkl"))
    
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
st.markdown("Enter your skills and discover which roles you're best suited for — with salary predictions and skill gap analysis.")
st.markdown("---")

df = load_data()
model, encoders = load_model()
skill_gap = load_skill_gap()

country = st.session_state.get("country_filter", "All")
symbol  = "₹" if country == "India" else "$"

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

        # Score each role based on skill match
        roles = [r for r in skill_gap.keys() if r != "Other"]
        scores = []

        for role in roles:
            gap = skill_gap[role]
            must_have    = set(gap.get("must_have", []))
            nice_to_have = set(gap.get("nice_to_have", []))
            emerging     = set(gap.get("emerging", []))

            must_match    = len(selected_set & must_have)
            nice_match    = len(selected_set & nice_to_have)
            emerging_match= len(selected_set & emerging)

            total_must    = max(len(must_have), 1)
            total_nice    = max(len(nice_to_have), 1)

            # Weighted score
            score = (
                (must_match / total_must) * 60 +
                (nice_match / total_nice) * 30 +
                (emerging_match / max(len(emerging), 1)) * 10
            )

            missing_must    = must_have - selected_set
            missing_nice    = nice_to_have - selected_set
            missing_emerging= emerging - selected_set

            scores.append({
                "role":             role,
                "score":            round(score, 1),
                "must_match":       must_match,
                "total_must":       len(must_have),
                "missing_must":     missing_must,
                "missing_nice":     missing_nice,
                "missing_emerging": missing_emerging
            })

        scores_df = pd.DataFrame(scores).sort_values("score", ascending=False)

        # Top 3 roles
        st.subheader("Your best role matches")
        top3 = scores_df.head(3)

        cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, (col, (_, row)) in enumerate(zip(cols, top3.iterrows())):
            with col:
                st.markdown(f"### {medals[i]} {row['role']}")
                st.metric("Match score", f"{row['score']:.1f}%")
                st.markdown(f"**Skills matched:** {row['must_match']} / {row['total_must']} must-have")

        st.markdown("---")

        # Full role match bar chart
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

        # Salary prediction for top role
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
            cat = sp.csr_matrix([[title_enc, exp_enc, mode_enc, domain_enc]])
            X   = sp.hstack([cat, skills_vec])
            pred = model.predict(X)[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("Role",           best_role)
            c2.metric("Predicted salary", format_salary(pred, symbol))
            c3.metric("Experience",     exp_level)
        except Exception as e:
            st.warning(f"Could not predict salary: {e}")

        st.markdown("---")

        # Skill gap for top role
        st.subheader(f"Skill gap analysis — {best_role}")
        best_gap = skill_gap.get(best_role, {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Must-have skills**")
            for s in best_gap.get("must_have", []):
                if s in selected_set:
                    st.markdown(f"✅ {s}")
                else:
                    st.markdown(f"❌ {s}")
        with col2:
            st.markdown("**Nice-to-have skills**")
            for s in best_gap.get("nice_to_have", []):
                if s in selected_set:
                    st.markdown(f"✅ {s}")
                else:
                    st.markdown(f"⬜ {s}")
        with col3:
            st.markdown("**Emerging skills**")
            for s in best_gap.get("emerging", []):
                if s in selected_set:
                    st.markdown(f"✅ {s}")
                else:
                    st.markdown(f"🔮 {s}")

        st.markdown("---")

        # Skills to learn next
        missing_must = scores_df.iloc[0]["missing_must"]
        missing_nice = scores_df.iloc[0]["missing_nice"]

        st.subheader("Skills to learn next")
        if missing_must:
            st.error(f"**Critical gaps (must-have):** {', '.join(missing_must)}")
        if missing_nice:
            st.warning(f"**Recommended (nice-to-have):** {', '.join(missing_nice)}")
        if not missing_must and not missing_nice:
            st.success("You have all the key skills for this role! Focus on emerging skills to stay ahead.")