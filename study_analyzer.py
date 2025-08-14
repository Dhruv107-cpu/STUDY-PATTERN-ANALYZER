import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import streamlit as st

# =====================
# DATA LOADING
# =====================
def load_data():
    df = pd.read_csv("study_logs.csv")
    return df

# =====================
# DATA PREPROCESSING
# =====================
def preprocess_data(df):
    df = df.copy()
    le = LabelEncoder()
    df["Mood"] = le.fit_transform(df["Mood"])
    X = df[["Study_Hours", "Sleep_Hours", "Distractions", "Breaks", "Mood"]]
    y = df["Score"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y, le, scaler

# =====================
# MODEL TRAINING
# =====================
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return model, mse, r2

# =====================
# SAVE MODEL
# =====================
def save_model(model, le, scaler):
    joblib.dump(model, "model.pkl")
    joblib.dump(le, "label_encoder.pkl")
    joblib.dump(scaler, "scaler.pkl")

# =====================
# STREAMLIT APP
# =====================
def run_app():
    st.title("📊 Study Pattern Analyzer")
    st.write("Predict your performance based on study habits")

    study_hours = st.slider("Study Hours", 0.0, 12.0, 5.0)
    sleep_hours = st.slider("Sleep Hours", 0.0, 12.0, 7.0)
    distractions = st.slider("Distractions", 0, 10, 2)
    breaks = st.slider("Breaks", 0, 10, 3)
    mood = st.selectbox("Mood", ["Focused", "Motivated", "Neutral", "Tired", "Stressed"])

    if st.button("Predict Performance"):
        model = joblib.load("model.pkl")
        le = joblib.load("label_encoder.pkl")
        scaler = joblib.load("scaler.pkl")

        mood_encoded = le.transform([mood])[0]
        input_data = np.array([[study_hours, sleep_hours, distractions, breaks, mood_encoded]])
        input_scaled = scaler.transform(input_data)

        prediction = model.predict(input_scaled)[0]
        st.success(f"Predicted Score: {prediction:.2f} / 100")

    # Show dataset insights
    st.subheader("📈 Dataset Insights")
    df = load_data()
    st.dataframe(df.head())

    fig, ax = plt.subplots()
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    df = load_data()
    X, y, le, scaler = preprocess_data(df)
    model, mse, r2 = train_model(X, y)
    save_model(model, le, scaler)
    print(f"Model trained. MSE: {mse:.2f}, R2: {r2:.2f}")
    run_app()
