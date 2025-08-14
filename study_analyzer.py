import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------
# Load or create dataset
# -------------------------------
def load_data():
    try:
        df = pd.read_csv("study_data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "hours_studied", "breaks_taken", "revision", "mood", "score"])
    return df

# -------------------------------
# Save dataset
# -------------------------------
def save_data(df):
    df.to_csv("study_data.csv", index=False)

# -------------------------------
# Generate advice
# -------------------------------
def generate_advice(df):
    if df.empty:
        return ["You haven't added any study data yet. Start logging your habits to get personalized advice!"]

    latest = df.iloc[-1]  # Last entry
    advice = []

    if latest["hours_studied"] < 2:
        advice.append("📖 Try to study at least 2–3 hours a day for consistent progress.")
    else:
        advice.append("✅ Great! Your study hours look consistent. Keep it up!")

    if latest["breaks_taken"] == 0:
        advice.append("💡 You didn’t take any breaks. Short breaks improve focus and memory.")
    elif latest["breaks_taken"] > 5:
        advice.append("⏳ Too many breaks might be reducing your productivity. Try to limit them.")
    else:
        advice.append("👍 Your break schedule seems healthy.")

    if latest["revision"] == 0:
        advice.append("🔁 Add some revision time. Revising helps strengthen memory retention.")
    else:
        advice.append("📚 Good job revising! Keep reviewing older topics regularly.")

    if latest["mood"] == "Stressed":
        advice.append("😟 You seem stressed. Try meditation, light exercise, or talking with a friend.")
    elif latest["mood"] == "Tired":
        advice.append("😴 You’re tired. Ensure proper sleep and stay hydrated for better focus.")
    elif latest["mood"] == "Happy":
        advice.append("😊 Being happy boosts learning efficiency. Stay positive!")
    else:
        advice.append("😐 A neutral mood is okay, but try to add small motivators like music or rewards.")

    if latest["score"] < 50:
        advice.append("📉 Your performance is low. Focus on weak subjects and revise more often.")
    elif latest["score"] < 75:
        advice.append("📊 You’re doing decent. A little more practice can push you higher.")
    else:
        advice.append("🏆 Excellent performance! Keep following your current strategy.")

    return advice

# -------------------------------
# Streamlit App
# -------------------------------
def run_app():
    st.set_page_config(page_title="Study Analyzer AI", page_icon="🤖", layout="wide")

    # -------------------------------
    # Custom CSS for professional look
    # -------------------------------
    st.markdown(
        """
        <style>
        /* Background image */
        body {
            background-image: url("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-attachment: fixed;
        }
        /* Transparent container effect */
        .stApp {
            background-color: rgba(0,0,0,0.65);
        }
        /* Chat bubble styling */
        .chat-bubble {
            background: rgba(255, 255, 255, 0.1);
            color: #f2f2f2;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 8px 0;
            font-size: 16px;
            backdrop-filter: blur(8px);
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        }
        /* Dark/light mode adaptive text */
        @media (prefers-color-scheme: light) {
            .chat-bubble { color: #111; background: rgba(255,255,255,0.7); }
            .stApp { background-color: rgba(255,255,255,0.6); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------
    # Header
    # -------------------------------
    st.markdown("<h1 style='text-align: center; color: white;'>🤖 Study Coach Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ddd;'>Track your daily habits and receive smart advice to improve performance.</p>", unsafe_allow_html=True)

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
    # Advice in chat bubbles
    # -------------------------------
    st.subheader("💬 Your Personalized Advice")
    advice_list = generate_advice(df)

    for msg in advice_list:
        st.markdown(f"<div class='chat-bubble'>{msg}</div>", unsafe_allow_html=True)

# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    run_app()
