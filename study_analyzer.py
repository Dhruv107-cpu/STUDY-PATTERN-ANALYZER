import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
# Function to generate advice
# -------------------------------
def generate_advice(df):
    advice = []

    # Average values
    avg_hours = df["hours_studied"].mean()
    avg_score = df["score"].mean()
    avg_breaks = df["breaks_taken"].mean()
    avg_revision = df["revision"].mean()

    # Hours studied vs score
    if avg_hours < 2:
        advice.append("📌 Try to study at least 2-3 hours daily. Your current average is too low.")
    elif avg_hours > 6:
        advice.append("📌 You are studying a lot (6+ hrs). Ensure you get enough rest.")
    else:
        advice.append("✅ Your study hours look balanced. Keep it up!")

    # Breaks
    if avg_breaks > 5:
        advice.append("⚠️ Too many breaks may reduce focus. Try limiting breaks.")
    elif avg_breaks < 2:
        advice.append("💡 Fewer breaks can cause fatigue. Short breaks improve efficiency.")
    else:
        advice.append("✅ Your break frequency is healthy.")

    # Revision
    if avg_revision < 1:
        advice.append("📖 Add more revision sessions. Revision strengthens memory.")
    else:
        advice.append("✅ You are revising well.")

    # Mood analysis
    if "mood" in df.columns:
        best_mood = df.groupby("mood")["score"].mean().idxmax()
        advice.append(f"😊 You perform best when you are **{best_mood}**. Try to maintain this mindset.")

    # Score check
    if avg_score < 50:
        advice.append("⚠️ Your average score is low. Focus on consistent study and revision.")
    elif avg_score >= 75:
        advice.append("🌟 Great! Your performance is strong. Keep pushing towards excellence.")

    return advice


# -------------------------------
# Streamlit app
# -------------------------------
def run_app():
    st.title("📊 Study Pattern Analyzer + Smart Advice")
    st.write("Track your study habits, analyze performance, and get **personalized advice**!")

    df = load_data()

    # -------------------------------
    # Data entry form
    # -------------------------------
    st.sidebar.header("➕ Add New Study Entry")
    with st.sidebar.form("entry_form"):
        date = st.date_input("Date")
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
            st.success("✅ Entry Saved!")

    # -------------------------------
    # Show dataset
    # -------------------------------
    if not df.empty:
        st.subheader("📂 Study Data")
        st.dataframe(df)

        # -------------------------------
        # Correlation Heatmap
        # -------------------------------
        st.subheader("📈 Correlation Heatmap")
        numeric_df = df.drop(columns=["date", "mood"], errors="ignore")
        numeric_df = numeric_df.select_dtypes(include=['number'])

        if not numeric_df.empty:
            fig, ax = plt.subplots()
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

        # -------------------------------
        # Line chart: Hours studied over time
        # -------------------------------
        st.subheader("📊 Study Hours Over Time")
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df_sorted = df.sort_values(by="date")
        st.line_chart(df_sorted.set_index("date")["hours_studied"])

        # -------------------------------
        # Extra: Average Score by Mood
        # -------------------------------
        st.subheader("😊 Average Score by Mood")
        if "mood" in df.columns:
            mood_avg = df.groupby("mood")["score"].mean()
            st.bar_chart(mood_avg)

        # -------------------------------
        # AI-Style Advice
        # -------------------------------
        st.subheader("💡 Personalized Study Advice")
        advice_list = generate_advice(df)
        for tip in advice_list:
            st.write("- " + tip)

    else:
        st.info("No data available yet. Add your first study entry from the sidebar!")


# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    run_app()
