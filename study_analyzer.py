import os
import random
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face API setup
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# --------------- AI ADVICE FUNCTION ----------------
def get_ai_advice(prompt: str) -> str:
    """Fetch AI advice using Hugging Face API, with fallback tips if unavailable."""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": f"Give personalized study advice for this student: {prompt}"}

        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        output = response.json()
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"].strip()
        else:
            return "⚠️ AI advice unavailable. Try again later."

    except Exception:
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
            "⚠️ AI advice not available right now.\n\nHere are some fallback tips:\n- "
            + "\n- ".join(random.sample(fallback_tips, 3))
        )

# --------------- STREAMLIT UI ----------------
st.set_page_config(
    page_title="📊 Study Pattern Analyzer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background Styling (Dark theme friendly)
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #1f1f2e, #2c2c54);
        color: #f8f8f2;
    }
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1519389950473-47ba0277781c");
        background-size: cover;
        background-attachment: fixed;
    }
    .chat-bubble {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        max-width: 70%;
    }
    .user-bubble {
        background-color: #4a69bd;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .bot-bubble {
        background-color: #2c3e50;
        color: #ecf0f1;
        margin-right: auto;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📘 Study Pattern Analyzer")
st.markdown("### ✨ Get personalized study advice with AI + fallback tips")

# Chat-like interface
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User Input
user_input = st.text_area("✍️ Describe your current study pattern:", height=120)

if st.button("🔍 Analyze & Get Advice"):
    if user_input.strip():
        with st.spinner("Analyzing your study habits..."):
            advice = get_ai_advice(user_input)

        # Save to chat history
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", advice))
    else:
        st.warning("⚠️ Please enter your study pattern first.")

# Display chat history
st.markdown("### 💬 Your Study Insights")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>{text}</div>", unsafe_allow_html=True)

# Gamification - XP System
st.sidebar.header("🎯 Gamification Progress")
if "xp" not in st.session_state:
    st.session_state.xp = 0

if st.button("✅ I followed today's advice!"):
    st.session_state.xp += 10
    st.success("🔥 Great! You earned +10 XP")

st.sidebar.progress(min(st.session_state.xp, 100))
st.sidebar.write(f"XP: {st.session_state.xp}/100")
if st.session_state.xp >= 100:
    st.sidebar.success("🏆 Congrats! You reached Level 1 🎉")
