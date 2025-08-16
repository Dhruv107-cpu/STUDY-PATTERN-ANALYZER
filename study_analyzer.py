import streamlit as st
import random
import time
from fpdf import FPDF

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
if "goal" not in st.session_state:
    st.session_state.goal = 4  # default target
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "study_time" not in st.session_state:
    st.session_state.study_time = 0.0  # in hours

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
st.markdown("### ✨ Select your study habits to get personalized advice")

# ----------------- USER INPUTS -----------------
hours_studied = st.slider("📚 Hours Studied Today", 0.0, 12.0, 4.0, 0.5)
breaks_taken = st.slider("☕ Breaks Taken", 0, 10, 2, 1)
revision_done = st.selectbox("🔁 Did you revise today?", ["Yes", "No"])
mood = st.selectbox("😊 Mood Today", ["Happy", "Neutral", "Stressed", "Tired"])
energy_level = st.selectbox("⚡ Energy Level", ["High", "Medium", "Low"])

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

    # Breaks
    if breaks == 0:
        tips.append("⚠️ No breaks? Take short breaks to stay fresh.")
    elif breaks > 5:
        tips.append("☕ Too many breaks may reduce focus. Try balancing.")

    # Revision
    if not revision:
        tips.append("🔁 Add 15 minutes of revision to strengthen memory.")

    # Mood/Energy
    if mood == "Stressed" and energy == "Low":
        tips.append("🧘 Try relaxation or a walk to recharge your mind.")
    elif mood == "Happy" and energy == "High":
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
    advice_list = generate_advice(hours_studied, breaks_taken, revision_bool, mood, energy_level, st.session_state.goal)

    # Store chat
    st.session_state.chat_history.append(("user", f"Studied {hours_studied}h, Breaks {breaks_taken}, Revision {revision_done}, Mood {mood}, Energy {energy_level}"))
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
    st.line_chart(st.session_state.mood_history)

# ----------------- WORK CLOCK -----------------
st.sidebar.header("🕒 Work Clock")

if st.sidebar.button("▶️ Start"):
    if not st.session_state.clock_running:
        st.session_state.start_time = time.time()
        st.session_state.clock_running = True

if st.sidebar.button("⏹ Stop"):
    if st.session_state.clock_running:
        elapsed = time.time() - st.session_state.start_time
        st.session_state.study_time += elapsed / 3600
        st.session_state.clock_running = False
        st.session_state.start_time = None

# Live Clock Display
placeholder = st.sidebar.empty()
if st.session_state.clock_running:
    elapsed = time.time() - st.session_state.start_time
    total_time = st.session_state.study_time + elapsed / 3600
    placeholder.write(f"⏳ Total Study Time: {total_time:.2f} hrs")
    st.rerun()
else:
    total_time = st.session_state.study_time
    placeholder.write(f"⏳ Total Study Time: {total_time:.2f} hrs")

# ----------------- EXPORT TO PDF -----------------
def export_to_pdf(chat_history, total_time, xp, streak):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="📘 Study Report", ln=True, align="C")

    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Study Time: {total_time:.2f} hrs", ln=True)
    pdf.cell(200, 10, txt=f"XP: {xp}", ln=True)
    pdf.cell(200, 10, txt=f"Streak: {streak} days", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Study Insights:", ln=True)
    for role, text in chat_history:
        pdf.multi_cell(0, 10, f"{role.capitalize()}: {text}")

    return pdf

if st.button("📄 Export Report to PDF"):
    pdf = export_to_pdf(st.session_state.chat_history, total_time, st.session_state.xp, st.session_state.streak)
    pdf.output("study_report.pdf")
    st.success("✅ Report saved as study_report.pdf")
