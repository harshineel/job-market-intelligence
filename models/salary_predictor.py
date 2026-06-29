import pandas as pd
import numpy as np
import json
import joblib
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error, r2_score
from scipy.sparse import hstack
import scipy.sparse as sp

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

def prepare_features(df):
    le_title  = LabelEncoder()
    le_exp    = LabelEncoder()
    le_mode   = LabelEncoder()
    le_domain = LabelEncoder()

    df["title_enc"]  = le_title.fit_transform(df["canonical_title"].fillna("Other"))
    df["exp_enc"]    = le_exp.fit_transform(df["experience_level"].fillna("Mid"))
    df["mode_enc"]   = le_mode.fit_transform(df["work_mode"].fillna("onsite"))
    df["domain_enc"] = le_domain.fit_transform(df["domain"].fillna("Other"))

    tfidf = TfidfVectorizer(max_features=50)
    skills_strings = df["skills_list"].apply(
        lambda x: " ".join(json.loads(x)) if x else ""
    )
    skills_matrix = tfidf.fit_transform(skills_strings)

    cat_features = sp.csr_matrix(df[["title_enc","exp_enc","mode_enc","domain_enc"]].values)
    X = hstack([cat_features, skills_matrix])
    y = df["salary_mid"].values

    encoders = {
        "title": le_title,
        "exp":   le_exp,
        "mode":  le_mode,
        "domain":le_domain,
        "tfidf": tfidf
    }
    return X, y, encoders

def train():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM jobs_master WHERE salary_mid IS NOT NULL", engine)
    print(f"Training on {len(df)} records")

    X, y, encoders = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print(f"\nModel Performance:")
    print(f"  RMSE : ${rmse:,.0f}")
    print(f"  R²   : {r2:.4f}")

    print("\nSample predictions vs actual:")
    sample = pd.DataFrame({
        "role":      df["canonical_title"].values[:8],
        "actual":    y_test[:8].astype(int),
        "predicted": y_pred[:8].astype(int)
    })
    print(sample.to_string(index=False))

    joblib.dump(model,    "models/salary_model.pkl")
    joblib.dump(encoders, "models/salary_encoders.pkl")
    print("\nSaved: models/salary_model.pkl")
    print("Saved: models/salary_encoders.pkl")

if __name__ == "__main__":
    train()