import streamlit as st
from datetime import datetime, timedelta
import random
import pandas as pd
from fpdf import FPDF
import time

# ----------------- STREAMLIT CONFIG -----------------
st.set_page_config(
    page_title="📘 Study Pattern Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE -----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

if "study_logs" not in st.session_state:
    st.session_state.study_logs = []

if "goal" not in st.session_state:
    st.session_state.goal = 4  # default target

# ----------------- UI STYLING -----------------
st.markdown(
    """
    <style>
    body {background: linear-gradient(to right, #1f1f2e, #2c2c54); color: #f8f8f2;}
    .stApp {background-image: url("https://images.unsplash.com/photo-1519389950473-47ba0277781c"); background-size: cover; background-attachment: fixed;}
    .chat-bubble {padding: 1rem; margin: 0.5rem 0; border-radius: 12px; max-width: 70%;}
    .user-bubble {background-color: #4a69bd; color: white; margin-left: auto; text-align: right;}
    .bot-bubble {background-color: #2c3e50; color: #ecf0f1; margin-right: auto; text-align: left;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📘 Study Pattern Analyzer")
st.markdown("### ✨ Track your study habits and get personalized insights")

# ----------------- USER INPUTS -----------------
st.subheader("📚 Log Today’s Study")
subject = st.selectbox("Choose Subject", ["Math", "DSA", "AI/ML", "Web Dev", "OS", "DBMS", "Other"])
hours_studied = st.slider("⏰ Hours Studied", 0, 12, 2)

# Productivity & Mood
productivity = st.radio("📊 Productivity Level", ["🔥 High", "⚡ Medium", "😴 Low"], horizontal=True)
mood = st.radio("🧠 Mood Today", ["😀 Happy", "😐 Neutral", "🥱 Tired", "😫 Stressed"], horizontal=True)
mood_intensity = st.slider("💡 Mood Intensity (1=Low, 10=High)", 1, 10, 5)

# NEW SLIDERS FOR INTERACTION
focus_level = st.slider("🎯 Focus Level (1-10)", 1, 10, 7)
distractions = st.slider("📱 Distractions (1-10)", 1, 10, 3)
sleep_quality = st.slider("😴 Sleep Quality Last Night (1-10)", 1, 10, 6)
energy_level = st.slider("⚡ Energy During Study (1-10)", 1, 10, 7)
satisfaction = st.slider("✅ Satisfaction With Progress (1-10)", 1, 10, 8)

revision_done = st.selectbox("🔁 Did you revise today?", ["Yes", "No"])
revision_bool = revision_done == "Yes"

# ----------------- DAILY GOAL -----------------
with st.sidebar:
    st.header("🎯 Daily Goal")
    st.session_state.goal = st.number_input("Set your daily study target (hours)", 1, 12, st.session_state.goal)

# ----------------- RULE-BASED ADVICE -----------------
def generate_advice(hours, breaks, revision, mood, energy, goal):
    tips = []

    # Hours studied
    if hours < goal:
        tips.append(f"📌 Try to reach your target of {goal} hours. You studied {hours} today.")
    else:
        tips.append(f"✅ Great! You achieved your study goal of {goal} hours today.")

    # Revision
    if not revision:
        tips.append("🔁 Add 15 minutes of revision to strengthen memory.")

    # Mood/Energy
    if mood == "😫 Stressed" and energy <= 4:
        tips.append("🧘 Try relaxation or a walk to recharge your mind.")
    elif mood == "😀 Happy" and energy >= 7:
        tips.append("🚀 Perfect state to push your limits today!")

    # Random motivational message
    motivation = random.choice([
        "🌟 Keep pushing, you’re building your future!",
        "🔥 Small steps daily lead to big success.",
        "💡 Focus on progress, not perfection.",
        "⏳ Consistency beats intensity every time.",
        "📖 Knowledge is compounding — keep going!"
    ])
    tips.append(motivation)

    return tips

# ----------------- BUTTON TO GET ADVICE -----------------
if st.button("🔍 Get Personalized Advice"):
    advice_list = generate_advice(hours_studied, 0, revision_bool, mood, energy_level, st.session_state.goal)

    # Store chat
    st.session_state.chat_history.append(("user", f"Studied {hours_studied}h, Mood: {mood}, Focus: {focus_level}, Energy: {energy_level}"))
    for tip in advice_list:
        st.session_state.chat_history.append(("bot", tip))

    # Track streaks
    if hours_studied >= st.session_state.goal:
        st.session_state.streak += 1
        st.session_state.xp += 20
    else:
        st.session_state.streak = 0

    # Track mood history
    st.session_state.mood_history.append(mood)

    # Store full log
    st.session_state.study_logs.append({
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Subject": subject,
        "Hours Studied": hours_studied,
        "Mood": mood,
        "Focus Level": focus_level,
        "Distractions": distractions,
        "Sleep Quality": sleep_quality,
        "Energy Level": energy_level,
        "Satisfaction": satisfaction,
        "Revision": revision_done
    })

# ----------------- DISPLAY CHAT -----------------
st.markdown("### 💬 Study Insights")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>{text}</div>", unsafe_allow_html=True)

# ----------------- GAMIFICATION -----------------
st.sidebar.header("🔥 Progress Tracker")
st.sidebar.progress(min(st.session_state.xp, 100))
st.sidebar.write(f"XP: {st.session_state.xp}/100")

if st.session_state.xp >= 50 and st.session_state.xp < 100:
    st.sidebar.success("🥉 Bronze Badge Unlocked!")
elif st.session_state.xp >= 100:
    st.sidebar.success("🥈 Silver Badge Unlocked!")

st.sidebar.write(f"🔥 Current Streak: {st.session_state.streak} days")

# ----------------- LEADERBOARD -----------------
st.sidebar.header("🏆 Leaderboard (Simulation)")
fake_scores = {
    "You": st.session_state.xp,
    "Alice": 70,
    "Bob": 40,
    "Charlie": 90
}
sorted_scores = sorted(fake_scores.items(), key=lambda x: x[1], reverse=True)
for name, score in sorted_scores:
    st.sidebar.write(f"{name}: {score} XP")

# ----------------- MOOD TRACKER -----------------
if len(st.session_state.mood_history) > 1:
    st.markdown("### 📊 Mood Tracker")
    st.line_chart(pd.DataFrame({"Mood Intensity": [mood_intensity]*len(st.session_state.mood_history)}))

# ----------------- POMODORO TIMER -----------------
st.subheader("⏱ Pomodoro Timer")
pomodoro_minutes = 25
pomodoro_seconds = st.session_state.get("pomodoro_seconds", pomodoro_minutes*60)

if st.button("Start Pomodoro"):
    st.session_state.pomodoro_seconds = pomodoro_minutes*60
    for i in range(st.session_state.pomodoro_seconds, -1, -1):
        mins, secs = divmod(i, 60)
        timer_display = f"{mins:02d}:{secs:02d}"
        st.markdown(f"**Time Remaining: {timer_display}**")
        time.sleep(1)
        st.rerun()

# ----------------- PDF EXPORT -----------------
def export_pdf(logs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "📘 Study Pattern Report\n\n")
    for log in logs:
        pdf.multi_cell(0, 8, str(log))
    pdf.output("study_report.pdf")
    st.success("✅ PDF exported as study_report.pdf")

if st.button("📄 Export PDF Report"):
    if st.session_state.study_logs:
        export_pdf(st.session_state.study_logs)
    else:
        st.warning("⚠️ No study logs to export yet!")
