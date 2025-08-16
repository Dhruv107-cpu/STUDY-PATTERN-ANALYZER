import os
import random
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face API setup
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

# ----------------- AI ADVICE FUNCTION -----------------
def get_ai_advice(prompt: str) -> str:
    """Fetch AI advice using Hugging Face API, with debug logging."""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": f"Give personalized study advice for this student: {prompt}"}

        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)

        # 🔎 Debug info (check in terminal)
        print("DEBUG STATUS:", response.status_code)
        print("DEBUG RESPONSE:", response.text[:500])  # show first 500 chars
        print("DEBUG URL:", HF_API_URL)

        response.raise_for_status()  # raise error if status not 200 OK

        output = response.json()

        # Hugging Face returns [{"generated_text": "..."}]
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].strip()
        else:
            return "⚠️ AI advice unavailable. Try again later."

    except Exception as e:
        # Fallback system
        fallback_tips = [
            "Break big tasks into smaller, achievable goals.",
            "Stick to a consistent daily routine.",
            "Use the Pomodoro technique: 25 mins study, 5 mins break.",
            "Revise what you studied yesterday before learning new topics.",
            "Avoid multitasking — focus on one subject at a time.",
            "Test yourself with quizzes instead of passive reading.",
            "Get proper sleep — memory strengthens during rest."
        ]
        return (
            f"🤖 ⚠️ AI error: {e}\n\nHere are some fallback tips:\n- "
            + "\n- ".join(random.sample(fallback_tips, 3))
        )

# ----------------- STREAMLIT UI -----------------
st.set_page_config(
    page_title="📊 Study Pattern Analyzer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
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

# ----------------- User Inputs -----------------
hours_studied = st.slider("📚 Hours Studied Today", 0.0, 12.0, 4.0, step=0.5)
breaks_taken = st.slider("☕ Breaks Taken", 0, 10, 2, step=1)
revision_done = st.selectbox("🔁 Did you revise today?", options=["Yes", "No"])
mood = st.selectbox("😊 Mood Today", options=["Happy", "Neutral", "Stressed", "Tired"])
energy_level = st.selectbox("⚡ Energy Level", options=["High", "Medium", "Low"])

revision_bool = revision_done == "Yes"

# ----------------- Chat & Gamification -----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "xp" not in st.session_state:
    st.session_state.xp = 0

# Build AI prompt
prompt_text = (
    f"Hours studied: {hours_studied}, "
    f"Breaks: {breaks_taken}, "
    f"Revision: {revision_done}, "
    f"Mood: {mood}, "
    f"Energy: {energy_level}"
)

if st.button("🔍 Get Personalized Advice"):
    advice = get_ai_advice(prompt_text)
    st.session_state.chat_history.append(("user", prompt_text))
    st.session_state.chat_history.append(("bot", advice))

# Display chat
st.markdown("### 💬 Study Insights")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>{text}</div>", unsafe_allow_html=True)

# Gamification
st.sidebar.header("🎯 Gamification Progress")
if st.button("✅ I followed today's advice!"):
    st.session_state.xp += 10
    st.success("🔥 Great! You earned +10 XP")

st.sidebar.progress(min(st.session_state.xp, 100))
st.sidebar.write(f"XP: {st.session_state.xp}/100")
if st.session_state.xp >= 100:
    st.sidebar.success("🏆 Congrats! You reached Level 1 🎉")
