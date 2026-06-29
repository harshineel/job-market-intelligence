import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

@st.cache_resource
def load_forecasts():
    forecasts = joblib.load(os.path.join(ROOT, "models", "forecasts.pkl"))
    summary   = joblib.load(os.path.join(ROOT, "models", "forecast_summary.pkl"))
    history   = joblib.load(os.path.join(ROOT, "models", "timeseries.pkl"))
    return forecasts, summary, history

st.title("Trend Forecast")
st.markdown("60-day demand forecast for each role using Facebook Prophet.")
st.markdown("---")

forecasts, summary, history = load_forecasts()

st.subheader("Role demand outlook — next 60 days")
growing   = summary[summary["trend"] == "Growing"].sort_values("pct_change", ascending=False)
declining = summary[summary["trend"] == "Declining"].sort_values("pct_change")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Growing roles**")
    for _, row in growing.iterrows():
        st.success(f"↑ {row['role']}   +{row['pct_change']:.1f}%")
with col2:
    st.markdown("**Declining roles**")
    for _, row in declining.iterrows():
        st.error(f"↓ {row['role']}   {row['pct_change']:.1f}%")

st.markdown("---")
st.subheader("Forecast detail by role")
selected = st.selectbox("Select a role to inspect", sorted(forecasts.keys()))

fc    = forecasts[selected]
hist  = history[selected]
today = pd.Timestamp.today()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=hist["ds"], y=hist["y"],
    name="Historical",
    line=dict(color="#378ADD", width=2)
))

future_fc = fc[fc["ds"] > today]
fig.add_trace(go.Scatter(
    x=future_fc["ds"], y=future_fc["yhat"],
    name="Forecast",
    line=dict(color="#1D9E75", width=2, dash="dash")
))

fig.add_trace(go.Scatter(
    x=pd.concat([future_fc["ds"], future_fc["ds"][::-1]]),
    y=pd.concat([future_fc["yhat_upper"], future_fc["yhat_lower"][::-1]]),
    fill="toself",
    fillcolor="rgba(29,158,117,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="Confidence interval"
))

fig.add_vline(
    x=str(today.date()),
    line_dash="dot",
    line_color="#888",
    annotation_text="Today"
)

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    xaxis_title="Date",
    yaxis_title="Daily job postings"
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
st.plotly_chart(fig, use_container_width=True)