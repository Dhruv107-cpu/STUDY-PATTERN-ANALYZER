import streamlit as st
import time
from datetime import datetime, timedelta
from fpdf import FPDF
import matplotlib.pyplot as plt

# ==============================
# Utility Functions
# ==============================
def clean_text(text):
    """Remove unsupported characters for PDF export"""
    return text.encode("latin-1", "ignore").decode("latin-1")

def export_to_pdf(study_logs, streak, total_hours):
    """Export all study logs to PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="📘 Study & Mood Analyzer Report", ln=True, align="C")
    pdf.ln(10)

    # Summary
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=clean_text(f"🔥 Current Streak: {streak} days"), ln=True)
    pdf.cell(0, 10, txt=clean_text(f"⏱ Total Hours Studied: {total_hours} hrs"), ln=True)
    pdf.ln(5)

    # Daily Logs
    for idx, log in enumerate(study_logs, 1):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=clean_text(f"Day {idx} - {log['Date']}"), ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in log.items():
            if k != "Date":
                pdf.multi_cell(0, 8, clean_text(f"{k}: {v}"))
        pdf.ln(5)

    pdf.output("study_report.pdf")
    return "study_report.pdf"

def calculate_streak(study_logs):
    """Calculate study streak in days"""
    if not study_logs:
        return 0
    dates = [datetime.strptime(log["Date"], "%Y-%m-%d") for log in study_logs]
    dates = sorted(list(set(dates)))
    streak = 1
    max_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1
    return max_streak

def pomodoro_timer():
    """Pomodoro Timer with work & break cycles"""
    st.subheader("⏳ Pomodoro Productivity Timer")

    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
        st.session_state.time_left = 25 * 60
        st.session_state.current_phase = "Work"
        st.session_state.cycle_count = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        start = st.button("▶️ Start")
    with col2:
        pause = st.button("⏸ Pause")
    with col3:
        reset = st.button("🔄 Reset")

    if start:
        st.session_state.timer_running = True
    if pause:
        st.session_state.timer_running = False
    if reset:
        st.session_state.timer_running = False
        st.session_state.time_left = 25 * 60
        st.session_state.current_phase = "Work"
        st.session_state.cycle_count = 0

    placeholder = st.empty()

    if st.session_state.timer_running:
        mins, secs = divmod(st.session_state.time_left, 60)
        timer_display = f"{mins:02}:{secs:02}"
        placeholder.markdown(f"### ⏱ Phase: **{st.session_state.current_phase}**  |  Time Left: **{timer_display}**")

        if st.session_state.time_left > 0:
            time.sleep(1)
            st.session_state.time_left -= 1
            st.rerun()
        else:
            if st.session_state.current_phase == "Work":
                st.session_state.current_phase = "Break"
                st.session_state.time_left = 5 * 60
                st.session_state.cycle_count += 1
                st.success("✅ Work session complete! Time for a 5 min break.")
            else:
                if st.session_state.cycle_count % 4 == 0:
                    st.session_state.time_left = 15 * 60
                    st.session_state.current_phase = "Long Break"
                    st.success("😌 Take a long 15-min break!")
                else:
                    st.session_state.time_left = 25 * 60
                    st.session_state.current_phase = "Work"
            st.rerun()

# ==============================
# Main App
# ==============================
def main():
    st.set_page_config(page_title="Study & Mood Analyzer", page_icon="📘", layout="wide")
    st.title("📘 Study & Mood Analyzer")
    st.write("Track your study habits, productivity & mood with professional insights.")

    # Sidebar clock
    with st.sidebar:
        st.markdown("### 🕒 Live Clock")
        st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")
        pomodoro_timer()

    # Initialize study log
    if "study_logs" not in st.session_state:
        st.session_state.study_logs = []

    st.subheader("📚 Log Today’s Study")

    subject = st.selectbox("Choose Subject", ["Math", "DSA", "AI/ML", "Web Dev", "OS", "DBMS", "Other"])
    hours_studied = st.slider("⏰ Hours Studied", 0, 12, 2)
    productivity = st.radio("📊 Productivity Level", ["🔥 High", "⚡ Medium", "😴 Low"], horizontal=True)

    # New Mood Tracker
    mood = st.radio("🧠 Mood Today", ["😀 Happy", "😐 Neutral", "🥱 Tired", "😫 Stressed"], horizontal=True)
    mood_intensity = st.slider("💡 Mood Intensity (1=Low, 10=High)", 1, 10, 5)

    if st.button("💾 Save Today’s Data"):
        study_data = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Subject": subject,
            "Hours Studied": hours_studied,
            "Productivity": productivity,
            "Mood": mood,
            "Mood Intensity": mood_intensity,
        }
        st.session_state.study_logs.append(study_data)
        st.success("✅ Study data saved successfully!")

    # Dashboard view
    if st.session_state.study_logs:
        st.subheader("📊 Study Dashboard")

        total_hours = sum(log["Hours Studied"] for log in st.session_state.study_logs)
        streak = calculate_streak(st.session_state.study_logs)

        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Streak", f"{streak} days")
        col2.metric("⏱ Total Hours", f"{total_hours} hrs")
        col3.metric("📅 Days Logged", len(st.session_state.study_logs))

        # Show trends
        st.write("### 📈 Study & Mood Trends")
        dates = [log["Date"] for log in st.session_state.study_logs]
        hours = [log["Hours Studied"] for log in st.session_state.study_logs]
        mood_intensity = [log["Mood Intensity"] for log in st.session_state.study_logs]

        fig, ax1 = plt.subplots()
        ax1.plot(dates, hours, label="Hours Studied", marker="o")
        ax1.set_ylabel("Hours Studied")
        ax1.set_xlabel("Date")

        ax2 = ax1.twinx()
        ax2.plot(dates, mood_intensity, color="orange", label="Mood Intensity", marker="s")
        ax2.set_ylabel("Mood Intensity")

        fig.autofmt_xdate()
        st.pyplot(fig)

        # Export
        if st.button("📄 Export Full Report as PDF"):
            file_path = export_to_pdf(st.session_state.study_logs, streak, total_hours)
            st.success(f"📁 Report saved as {file_path}")

# Run app
if __name__ == "__main__":
    main()
