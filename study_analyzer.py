import streamlit as st
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

# ----------------- SESSION STATE INIT -----------------
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "goal" not in st.session_state:
    st.session_state.goal = 2
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "study_time" not in st.session_state:
    st.session_state.study_time = 0.0

# ----------------- APP HEADER -----------------
st.title("📘 Study Pattern Analyzer")
st.markdown("Track your study habits, analyze progress, and stay motivated!")

# ----------------- INPUT SECTION -----------------
st.header("✍️ Daily Study Log")

hours_studied = st.slider("📚 Hours Studied Today", min_value=0, max_value=12, value=2)
breaks_taken = st.slider("☕ Number of Breaks", min_value=0, max_value=10, value=2)
revision_done = st.radio("📖 Revision Completed?", ["Yes", "No"])
mood = st.selectbox("😊 Mood Today", ["Happy", "Neutral", "Stressed", "Tired"])
energy_level = st.slider("⚡ Energy Level", 1, 10, 5)

# ----------------- GOAL SETTING -----------------
st.sidebar.header("🎯 Goal Setting")
goal = st.sidebar.number_input("Set daily study goal (hrs)", min_value=1, max_value=12, value=st.session_state.goal)
st.session_state.goal = goal

# ----------------- WORK CLOCK -----------------
st.sidebar.header("🕒 Work Clock")

if st.sidebar.button("▶️ Start"):
    if not st.session_state.clock_running:
        st.session_state.start_time = time.time()
        st.session_state.clock_running = True

if st.sidebar.button("⏹ Stop"):
    if st.session_state.clock_running:
        elapsed = time.time() - st.session_state.start_time
        st.session_state.study_time += elapsed / 3600  # sec → hrs
        st.session_state.clock_running = False

# Show timer
if st.session_state.clock_running:
    elapsed = time.time() - st.session_state.start_time
    total_time = st.session_state.study_time + elapsed / 3600
else:
    total_time = st.session_state.study_time

st.sidebar.write(f"⏳ Total Study Time: {total_time:.2f} hrs")

# ----------------- FEEDBACK ENGINE -----------------
feedback = []
if hours_studied < st.session_state.goal:
    feedback.append("📌 Try to reach your study goal for today!")
else:
    feedback.append("✅ Great! You met your study goal.")

if breaks_taken > 5:
    feedback.append("⚠️ Too many breaks! Try to stay focused.")
else:
    feedback.append("👌 Breaks are well balanced.")

if revision_done == "No":
    feedback.append("📖 Don’t forget to revise what you studied.")

if energy_level < 4:
    feedback.append("💤 Energy is low, consider proper rest and diet.")

if mood == "Stressed":
    feedback.append("🧘 Try relaxation or breathing exercises to reduce stress.")

# Update XP and Streak
if hours_studied >= st.session_state.goal:
    st.session_state.xp += 10
    st.session_state.streak += 1
else:
    st.session_state.streak = 0

# ----------------- DISPLAY RESULTS -----------------
st.header("📊 Progress Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Hours Studied", f"{hours_studied} hrs")
col2.metric("XP Earned", st.session_state.xp)
col3.metric("🔥 Streak", f"{st.session_state.streak} days")

st.subheader("📌 Personalized Advice")
for f in feedback:
    st.info(f)
    st.session_state.chat_history.append(("bot", f))

# ----------------- PROGRESS CHART -----------------
st.subheader("📈 Study vs Goal")
fig, ax = plt.subplots()
ax.bar(["Studied", "Goal"], [hours_studied, st.session_state.goal])
st.pyplot(fig)

# ----------------- CHAT SECTION -----------------
st.subheader("💬 Ask for Study Tips")
user_input = st.text_input("Type your question here:")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    if "motivation" in user_input.lower():
        bot_reply = "🚀 Stay positive! Small consistent steps lead to big success."
    elif "focus" in user_input.lower():
        bot_reply = "🎯 Use the Pomodoro technique (25 min study, 5 min break)."
    else:
        bot_reply = "📚 Keep a regular schedule and avoid distractions."
    st.session_state.chat_history.append(("bot", bot_reply))

for role, msg in st.session_state.chat_history[-6:]:
    if role == "user":
        st.write(f"🧑‍🎓 **You:** {msg}")
    else:
        st.write(f"🤖 **Bot:** {msg}")

# ----------------- PDF EXPORT -----------------
def create_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "📘 Study Report")

    c.setFont("Helvetica", 12)
    y = 700
    c.drawString(50, y, f"Hours Studied: {hours_studied}")
    y -= 20
    c.drawString(50, y, f"Breaks Taken: {breaks_taken}")
    y -= 20
    c.drawString(50, y, f"Revision Done: {revision_done}")
    y -= 20
    c.drawString(50, y, f"Mood: {mood}, Energy: {energy_level}")
    y -= 20
    c.drawString(50, y, f"Goal: {st.session_state.goal} hrs")
    y -= 20
    c.drawString(50, y, f"XP: {st.session_state.xp}, Streak: {st.session_state.streak} days")
    y -= 40
    c.drawString(50, y, "Advice:")

    for tip in st.session_state.chat_history[-5:]:
        if tip[0] == "bot":
            y -= 20
            c.drawString(70, y, f"- {tip[1]}")

    c.save()
    buffer.seek(0)
    return buffer

pdf_buffer = create_pdf()
st.sidebar.download_button(
    label="📄 Download PDF Report",
    data=pdf_buffer,
    file_name="study_report.pdf",
    mime="application/pdf"
)
