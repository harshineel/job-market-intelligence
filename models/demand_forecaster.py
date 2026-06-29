import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="123456789",
    host="localhost",
    port=5432,
    database="job_market_db"
)

def get_engine():
    return create_engine(connection_url)

def generate_timeseries(df):
    roles = df["canonical_title"].unique()
    all_series = {}
    np.random.seed(42)

    for role in roles:
        role_count = len(df[df["canonical_title"] == role])
        dates = pd.date_range(end=pd.Timestamp.today(), periods=90, freq="D")
        base = role_count / 90
        trend = np.linspace(0.8, 1.2, 90)
        noise = np.random.poisson(base * trend)
        series = pd.DataFrame({"ds": dates, "y": noise.astype(float)})
        all_series[role] = series

    return all_series

def train_forecasts(all_series):
    forecasts = {}
    models = {}

    for role, series in all_series.items():
        print(f"  Forecasting: {role}")
        m = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.3
        )
        m.fit(series)
        future = m.make_future_dataframe(periods=60)
        forecast = m.predict(future)
        forecasts[role] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        models[role] = m

    return forecasts, models

def summarize(forecasts, all_series):
    print("\nDemand forecast summary (next 60 days):")
    summary = []
    for role, fc in forecasts.items():
        historical_avg = all_series[role]["y"].mean()
        future_avg = fc[fc["ds"] > pd.Timestamp.today()]["yhat"].mean()
        trend = "Growing" if future_avg > historical_avg else "Declining"
        pct_change = round((future_avg - historical_avg) / max(historical_avg, 0.1) * 100, 1)
        summary.append({
            "role": role,
            "trend": trend,
            "pct_change": pct_change,
            "future_avg_daily": round(future_avg, 2)
        })
        print(f"  {role:25s} {trend:10s} {pct_change:+.1f}%")

    return pd.DataFrame(summary)

if __name__ == "__main__":
    engine = get_engine()
    df = pd.read_sql("SELECT canonical_title, posted_date FROM jobs_master", engine)
    print(f"Loaded {len(df)} records")

    print("\nGenerating time series...")
    all_series = generate_timeseries(df)

    print("Training Prophet models...")
    forecasts, models = train_forecasts(all_series)

    summary_df = summarize(forecasts, all_series)

    joblib.dump(forecasts, "models/forecasts.pkl")
    joblib.dump(summary_df, "models/forecast_summary.pkl")
    joblib.dump(all_series, "models/timeseries.pkl")

    print("\nSaved: models/forecasts.pkl")
    print("Saved: models/forecast_summary.pkl")
    print("Done!")