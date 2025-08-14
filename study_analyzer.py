import streamlit as st
import pandas as pd
import random
from datetime import datetime

# -------------------------------
# Function to load or create dataset
# -------------------------------
def load_data():
    try:
        df = pd.read_csv("study_data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "hours_studied", "breaks_taken", "revision", "mood", "score"])
    return df

# -------------------------------
# Function to save dataset
# -------------------------------
def save_data(df):
    df.to_csv("study_data.csv", index=False)

# -------------------------------
# Function to analyze and generate advice
# -------------------------------
def generate_advice(df):
    if df.empty:
        return ["You haven't added any study data yet. Start logging your habits to get personalized advice!"]

    latest = df.iloc[-1]  # Last entry
    advice = []

    # Hours studied
    if latest["hours_studied"] < 2:
        advice.append("📖 Try to study at least 2–3 hours a day for consistent progress.")
    else:
        advice.append("✅ Great! Your study hours look consistent. Keep it up!")

    # Breaks taken
    if latest["breaks_taken"] == 0:
        advice.append("💡 You didn’t take any breaks. Short breaks improve focus and memory.")
    elif latest["breaks_taken"] > 5:
        advice.append("⏳ Too many breaks might be reducing your productivity. Try to limit them.")
    else:
        advice.append("👍 Your break schedule seems healthy.")

    # Revision
    if latest["revision"] == 0:
        advice.append("🔁 Add some revision time. Revising helps strengthen memory retention.")
    else:
        advice.append("📚 Good job revising! Keep reviewing older topics regularly.")

    # Mood
    if latest["mood"] == "Stressed":
        advice.append("😟 You seem stressed. Try meditation, light exercise, or talking with a friend.")
    elif latest["mood"] == "Tired":
        advice.append("😴 You’re tired. Ensure proper sleep and stay hydrated for better focus.")
    elif latest["mood"] == "Happy":
        advice.append("😊 Being happy boosts learning efficiency. Stay positive!")
    else:
        advice.append("😐 A neutral mood is okay, but try to add small motivators like music or rewards.")

    # Score
    if latest["score"] < 50:
        advice.append("📉 Your performance is low. Focus on weak subjects and revise more often.")
    elif latest["score"] < 75:
        advice.append("📊 You’re doing decent. A little more practice can push you higher.")
    else:
        advice.append("🏆 Excellent performance! Keep following your current strategy.")

    return advice


# -------------------------------
# Chatbot-style UI
# -------------------------------
def run_app():
    st.set_page_config(page_title="Study Analyzer AI", page_icon="📊", layout="centered")
    st.markdown("<h1 style='text-align: center;'>🤖 Study Coach Assistant</h1>", unsafe_allow_html=True)
    st.write("Log your daily study habits and get **personalized AI advice** for better performance.")

    df = load_data()

    # Sidebar input
    st.sidebar.header("➕ Add New Study Entry")
    with st.sidebar.form("entry_form"):
        date = st.date_input("Date", datetime.today())
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)
        breaks = st.number_input("Breaks Taken", min_value=0, step=1)
        revision = st.number_input("Revision Time (hrs)", min_value=0.0, step=0.5)
        mood = st.selectbox("Mood", ["Happy", "Stressed", "Neutral", "Tired"])
        score = st.number_input("Score (0-100)", min_value=0, max_value=100, step=1)

        submitted = st.form_submit_button("Save Entry")
        if submitted:
            new_entry = pd.DataFrame(
                [[date, hours, breaks, revision, mood, score]],
                columns=["date", "hours_studied", "breaks_taken", "revision", "mood", "score"]
            )
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.sidebar.success("✅ Entry Saved!")

    # -------------------------------
    # Chatbot output (Advice)
    # -------------------------------
    st.subheader("💬 Your Study Assistant's Advice")
    advice_list = generate_advice(df)

    if advice_list:
        for msg in advice_list:
            st.markdown(f"""
                <div style='background-color:#f0f2f6;
                            padding:10px;
                            border-radius:12px;
                            margin:5px 0;
                            font-size:16px;'>
                    {msg}
                </div>
                """, unsafe_allow_html=True)


# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    run_app()
