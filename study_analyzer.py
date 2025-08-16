import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import matplotlib.pyplot as plt
import datetime

# -----------------------------
# PDF Export Function
# -----------------------------
def export_to_pdf(notes_dict, filename="study_notes.pdf"):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 40, "📚 Study Notes Export")
    y = height - 70

    c.setFont("Helvetica", 12)
    for category, notes in notes_dict.items():
        if notes.strip():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"📂 {category}")
            y -= 20

            c.setFont("Helvetica", 11)
            for line in notes.strip().split("\n"):
                c.drawString(70, y, line)
                y -= 18
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 11)

            y -= 10

    c.save()
    return temp_file.name

# -----------------------------
# Streamlit Page Setup
# -----------------------------
st.set_page_config(page_title="📚 Study Pattern Analyzer", layout="wide")

st.title("📚 Study Pattern Analyzer")
st.write("Track your study patterns, take categorized notes, view progress, get reminders, and export them as PDF.")

# -----------------------------
# Session State Initialization
# -----------------------------
if "study_notes" not in st.session_state:
    st.session_state.study_notes = {"Math": "", "AI": "", "Daily Plan": "", "Others": ""}

if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_entry_date" not in st.session_state:
    st.session_state.last_entry_date = None

# -----------------------------
# Daily Reminder Check
# -----------------------------
today = datetime.date.today()
if st.session_state.last_entry_date != today:
    st.warning("⏰ Reminder: You haven’t added any notes today. Stay consistent! 💪")

# -----------------------------
# Category Selector
# -----------------------------
category = st.selectbox("📂 Choose Category", ["Math", "AI", "Daily Plan", "Others"])

# -----------------------------
# Text Note Input
# -----------------------------
note = st.text_area("✍️ Write a study note:")
if st.button("➕ Add Note"):
    if note.strip():
        st.session_state.study_notes[category] += f"- {note.strip()}\n"
        st.success(f"✅ Note added to {category}!")

        # Update streak
        if st.session_state.last_entry_date == today - datetime.timedelta(days=1):
            st.session_state.streak += 1
        elif st.session_state.last_entry_date != today:
            st.session_state.streak = 1
        st.session_state.last_entry_date = today

# -----------------------------
# Display Notes by Category
# -----------------------------
st.subheader("🗒️ Your Notes by Category")
for cat, notes in st.session_state.study_notes.items():
    if notes.strip():
        st.text_area(f"{cat} Notes", notes, height=150)

# -----------------------------
# Progress Dashboard
# -----------------------------
st.subheader("📊 Progress Dashboard")

category_counts = {cat: len(notes.strip().split("\n")) if notes.strip() else 0 
                   for cat, notes in st.session_state.study_notes.items()}
total_notes = sum(category_counts.values())

col1, col2 = st.columns(2)

with col1:
    st.metric("📌 Total Notes", total_notes)
    st.metric("🔥 Streak", f"{st.session_state.streak} days")
    for cat, count in category_counts.items():
        st.write(f"✅ {cat}: {count} notes")

with col2:
    if total_notes > 0:
        fig, ax = plt.subplots()
        ax.bar(category_counts.keys(), category_counts.values())
        ax.set_ylabel("Number of Notes")
        ax.set_title("Notes per Category")
        st.pyplot(fig)

# -----------------------------
# Export PDF Button
# -----------------------------
if st.button("📤 Export Notes as PDF"):
    pdf_path = export_to_pdf(st.session_state.study_notes)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Download PDF", f, file_name="study_notes.pdf")
