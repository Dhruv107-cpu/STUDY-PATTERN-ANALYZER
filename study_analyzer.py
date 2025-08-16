import os
import random
import requests
import streamlit as st
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Hugging Face API setup
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"


# ----------------- AI ADVICE FUNCTION -----------------
def get_ai_advice(prompt: str) -> str:
    """Fetch AI advice using Hugging Face API, with retries if model is loading."""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": f"Give personalized study advice for this student: {prompt}"}

        # Retry up to 3 times in case model is still loading
        for attempt in range(3):
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            output = response.json()

            # Handle different output formats
            if isinstance(output, list) and len(output) > 0:
                if "generated_text" in output[0]:
                    return output[0]["generated_text"].strip()
                elif "summary_text" in output[0]:
                    return output[0]["summary_text"].strip()

            # Model still loading
            if "error" in output and "loading" in output["error"].lower():
                time.sleep(10)  # wait and retry
                continue

            return "⚠️ AI advice unavailable. Try again later."

        return "⚠️ AI advice unavailable after multiple retries."

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
            f"⚠️ AI error: {str(e)}\n\nHere are some fallback tips:\n- "
            + "\n- ".join(random.sample(fallback_tips, 3))
        )

# ----------------- STREAMLIT UI -----------------
st.set_page_config(
    page_title="📊 Study Pattern Analyzer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Combine input data into a prompt for AI
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

# Display chat history
st.markdown("### 💬 Study Insights")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.success(f"👤 {text}")
    else:
        st.info(f"🤖 {text}")

# Gamification - XP
st.sidebar.header("🎯 Gamification Progress")
if st.button("✅ I followed today's advice!"):
    st.session_state.xp += 10
    st.success("🔥 Great! You earned +10 XP")

st.sidebar.progress(min(st.session_state.xp, 100))
st.sidebar.write(f"XP: {st.session_state.xp}/100")
if st.session_state.xp >= 100:
    st.sidebar.success("🏆 Congrats! You reached Level 1 🎉")
