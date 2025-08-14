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
# Streamlit app
# -------------------------------
def run_app():
    st.title("📊 Study Pattern Analyzer")
    st.write("Track your study habits and analyze how they impact your performance!")

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
        # Correlation Heatmap (numeric only)
        # -------------------------------
        st.subheader("📈 Correlation Heatmap")
        numeric_df = df.drop(columns=["date", "mood"], errors="ignore")
        numeric_df = numeric_df.select_dtypes(include=['number'])

        if not numeric_df.empty:
            fig, ax = plt.subplots()
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.info("No numeric data available for correlation.")

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

    else:
        st.info("No data available yet. Add your first study entry from the sidebar!")


# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    run_app()
