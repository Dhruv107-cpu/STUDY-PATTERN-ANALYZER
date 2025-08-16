import streamlit as st
import time
from datetime import datetime
from fpdf import FPDF

# ==============================
# Utility Functions
# ==============================
def clean_text(text):
    """Remove unsupported characters for PDF export"""
    return text.encode("latin-1", "ignore").decode("latin-1")

def export_to_pdf(study_data):
    """Export study summary to PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=clean_text("Study Pattern Analyzer Report"), ln=True, align="C")
    pdf.ln(10)

    for key, value in study_data.items():
        pdf.multi_cell(0, 10, clean_text(f"{key}: {value}"))

    pdf.output("study_report.pdf")
    return "study_report.pdf"

def pomodoro_timer():
    """25-min Pomodoro Timer"""
    st.subheader("⏳ Pomodoro Timer (25 minutes)")
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
        st.session_state.time_left = 25 * 60  # 25 mins in seconds

    start = st.button("▶️ Start 25 min Timer")
    reset = st.button("🔄 Reset Timer")

    if start:
        st.session_state.timer_running = True

    if reset:
        st.session_state.timer_running = False
        st.session_state.time_left = 25 * 60

    placeholder = st.empty()

    if st.session_state.timer_running:
        while st.session_state.time_left > 0:
            mins, secs = divmod(st.session_state.time_left, 60)
            timer_display = f"{mins:02}:{secs:02}"
            placeholder.markdown(f"### ⏱ Time Left: **{timer_display}**")
            time.sleep(1)
            st.session_state.time_left -= 1
            st.experimental_rerun()

        st.success("✅ Time’s up! Take a short break.")
        st.session_state.timer_running = False

# ==============================
# Main Streamlit App
# ==============================
def main():
    st.title("📘 Study Pattern Analyzer")
    st.write("Track your study habits and improve productivity!")

    # Live clock
    clock_placeholder = st.empty()
    clock_placeholder.markdown(f"🕒 Current Time: **{datetime.now().strftime('%H:%M:%S')}**")

    # User input
    subject = st.text_input("📚 Subject you studied today:")
    hours_studied = st.slider("⏰ Hours Studied", 0, 12, 1)
    productivity = st.selectbox("📊 Productivity Level", ["Low", "Medium", "High"])

    notes = st.text_area("📝 Any notes about today’s study session:")

    if st.button("💾 Save Study Data"):
        st.session_state.study_data = {
            "Subject": subject,
            "Hours Studied": hours_studied,
            "Productivity": productivity,
            "Notes": notes,
            "Date": datetime.now().strftime("%Y-%m-%d"),
        }
        st.success("✅ Study data saved successfully!")

    # Show data if saved
    if "study_data" in st.session_state:
        st.subheader("📊 Today’s Summary")
        for k, v in st.session_state.study_data.items():
            st.write(f"**{k}:** {v}")

        if st.button("📄 Export Report as PDF"):
            file_path = export_to_pdf(st.session_state.study_data)
            st.success(f"📁 Report saved as {file_path}")

    # Sidebar with Pomodoro
    with st.sidebar:
        pomodoro_timer()

# Run app
if __name__ == "__main__":
    main()
