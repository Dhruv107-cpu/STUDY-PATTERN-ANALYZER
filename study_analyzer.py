# app.py
import math
import random
import datetime as dt
import streamlit as st

# --------------------------- CONFIG ---------------------------
st.set_page_config(
    page_title="📘 Study Pattern Analyzer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- STYLES ---------------------------
st.markdown(
    """
    <style>
      :root {
        --bg1: #0f1220;
        --bg2: #171a2e;
        --card: #1f2442;
        --text: #e6e9f5;
        --muted: #b8c1ec;
        --accent: #7c9cff;
        --success: #61d095;
        --warn: #ffb84d;
        --danger: #ff6b6b;
      }
      .stApp {
        background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
      }
      .glass {
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
      }
      .metric {
        display:flex; align-items:center; gap:12px; padding:10px 12px; border-radius:14px;
        background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07);
      }
      .chip {
        display:inline-block; padding:6px 10px; border-radius:20px; font-size:0.9rem;
        background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1);
      }
      .bubbles {padding: 4px 0;}
      .bubble {
        padding: 12px 14px; margin: 8px 0; border-radius: 14px; max-width: 90%;
        border:1px solid rgba(255,255,255,0.08);
      }
      .bubble.user { margin-left:auto; background:#32407a; color:white;}
      .bubble.bot { margin-right:auto; background:#243050; color:#eaf0ff;}
      .h1 {font-size: 2rem; font-weight: 700; letter-spacing: .3px;}
      .sub {color: var(--muted); margin-top:-6px;}
      .ring {
        width: 160px; height:160px; border-radius:50%; position: relative; display:inline-block;
        background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(255,255,255,0.08) 0);
      }
      .ring::after {
        content:""; position:absolute; inset:10px; border-radius:50%;
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
      }
      .ring-label { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
        font-size:1.2rem; font-weight:700; color:var(--text); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- STATE ---------------------------
if "chat" not in st.session_state: st.session_state.chat = []
if "xp" not in st.session_state: st.session_state.xp = 0
if "streak" not in st.session_state: st.session_state.streak = 0
if "last_log_date" not in st.session_state: st.session_state.last_log_date = None

# --------------------------- HEADER ---------------------------
st.markdown("<div class='h1'>📘 Study Pattern Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Track your habits, hit your goals, and improve daily — no AI required.</div>", unsafe_allow_html=True)
st.write("")

# --------------------------- LAYOUT ---------------------------
left, mid, right = st.columns([1.1, 1, 1.1])

# =========================== LEFT: INPUTS ===========================
with left:
    st.markdown("### ✨ Your Study Inputs")
    with st.container():
        with st.form("study_form", clear_on_submit=False):
            hours = st.slider("📚 Hours studied today", min_value=0.0, max_value=12.0, value=4.0, step=0.5)
            goal = st.slider("🎯 Your daily study goal (hours)", min_value=1.0, max_value=12.0, value=6.0, step=0.5)
            breaks = st.slider("☕ Breaks taken", min_value=0, max_value=12, value=2, step=1)
            revision = st.selectbox("🔁 Did you revise today?", ["Yes", "No"])
            mood = st.selectbox("😊 Mood today", ["Happy", "Neutral", "Stressed", "Tired"])
            energy = st.selectbox("⚡ Energy level", ["High", "Medium", "Low"])
            focus_area = st.text_input("📌 Focus topic (optional)", placeholder="e.g., Dynamic Programming, Calculus, DBMS…")
            submitted = st.form_submit_button("🔍 Analyze My Study Pattern", use_container_width=True)

    # Build prompt-like summary string (kept for chat history clarity)
    summary_line = (
        f"Hours: {hours}, Goal: {goal}, Breaks: {breaks}, "
        f"Revision: {revision}, Mood: {mood}, Energy: {energy}"
        + (f", Focus: {focus_area}" if focus_area else "")
    )

# =========================== MID: SUMMARY & RING ===========================
with mid:
    st.markdown("### 📊 Today at a Glance")
    # Progress percentage towards goal
    pct = 0 if goal == 0 else min(100, round((hours / goal) * 100))
    st.markdown(
        f"""
        <div class="glass" style="text-align:center;">
          <div class="ring" style="--p:{pct};">
            <div class="ring-label">{pct}%</div>
          </div>
          <div style="margin-top:10px; color:var(--muted);">Goal Completion</div>
          <div class="chip" style="margin-top:10px;">⏳ {hours}h studied / 🎯 {goal}h goal</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            f"""
            <div class="metric">
              <div>🧠</div>
              <div><b>Revision</b><br><span style="color:var(--muted)">{'Completed' if revision=='Yes' else 'Pending'}</span></div>
            </div>
            """, unsafe_allow_html=True
        )
    with colB:
        balance = "Balanced" if 1 <= breaks <= 5 else ("Too Few" if breaks == 0 else "Too Many")
        st.markdown(
            f"""
            <div class="metric">
              <div>☕</div>
              <div><b>Breaks</b><br><span style="color:var(--muted)">{breaks} ({balance})</span></div>
            </div>
            """, unsafe_allow_html=True
        )
    st.write("")
    st.markdown(
        f"""
        <div class="metric">
          <div>😊</div>
          <div><b>Mood & Energy</b><br><span style="color:var(--muted)">{mood} · {energy}</span></div>
        </div>
        """, unsafe_allow_html=True
    )

# =========================== RIGHT: RECOMMENDATIONS ===========================
def build_recommendations(h, g, b, rev, md, en, focus):
    recs = []

    # Hours vs goal
    if h < g * 0.6:
        recs.append("📈 You studied much less than your goal. Plan **two focused 45-minute blocks** tomorrow.")
    elif h < g:
        recs.append("👍 Close to your goal—add **one extra 30-minute session** to bridge the gap.")
    else:
        recs.append("🏅 Great job hitting your goal! Consider a **brief recap** to consolidate learning.")

    # Breaks quality
    if b == 0:
        recs.append("☕ Add **short 5-minute breaks** every 25–30 minutes to avoid fatigue.")
    elif b > 6:
        recs.append("🧭 Too many breaks can hurt momentum. Try **2–5 breaks** spread through the day.")

    # Revision
    if rev == "No":
        recs.append("🔁 Do **10-minute active recall** on yesterday’s topic. It boosts long-term memory.")

    # Mood/Energy combos
    if md == "Stressed" and en in ("Low", "Medium"):
        recs.append("🧘 Do **5 minutes of box breathing** or a quick walk before your next session.")
    if md == "Tired" and en == "Low":
        recs.append("😴 Take a **20-minute power nap** or **light stretching**; return for one short session.")
    if md == "Happy" and en == "High":
        recs.append("🚀 You’re in the zone—schedule a **deep work block (60–90 mins)** on your hardest topic.")

    # Focus suggestion
    if focus:
        recs.append(f"🎯 Stick to **{focus}** today. End with a **3-point summary** in your notes.")

    # General best practices (add two random)
    best = [
        "📚 Start each session by **rewriting your goals** for that block.",
        "📝 Use **active recall** instead of rereading notes.",
        "⏱️ Try **Pomodoro (25/5)** for sustained focus.",
        "📵 Keep your phone **outside the room** while studying.",
        "🧪 End with a **quick self-quiz** (5 questions).",
        "🌙 Review your key points **before sleep**."
    ]
    recs.extend(random.sample(best, 2))
    return recs

with right:
    st.markdown("### 💡 Recommendations")
    if left and 'submitted' in locals() and submitted:
        recs = build_recommendations(hours, goal, breaks, revision, mood, energy, focus_area)
        with st.container():
            for r in recs:
                st.markdown(f"- {r}")

        # Chat-style history
        st.markdown("### 💬 Study Insights")
        st.session_state.chat.append(("user", summary_line))
        st.session_state.chat.append(("bot", "\n".join(recs)))
    else:
        st.info("Fill in the inputs and click **Analyze My Study Pattern** to get tailored recommendations.")

# =========================== CHAT HISTORY ===========================
st.markdown("<div class='bubbles'>", unsafe_allow_html=True)
for role, text in st.session_state.chat[-6:]:  # show last 6 messages
    cls = "user" if role == "user" else "bot"
    st.markdown(f"<div class='bubble {cls}'>{text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================== SIDEBAR: GAMIFICATION & EXTRAS ===========================
st.sidebar.header("🎮 Your Progress")

# Daily log / streak
today = dt.date.today().isoformat()
if st.sidebar.button("🗓️ Log today's study"):
    if st.session_state.last_log_date != today:
        # if yesterday logged, increment streak, otherwise reset
        if st.session_state.last_log_date:
            last = dt.date.fromisoformat(st.session_state.last_log_date)
            if (dt.date.today() - last).days == 1:
                st.session_state.streak += 1
            elif (dt.date.today() - last).days > 1:
                st.session_state.streak = 1
        else:
            st.session_state.streak = 1
        st.session_state.last_log_date = today
        st.success("Logged! 🔥 Streak updated.")
    else:
        st.info("Already logged today ✅")

st.sidebar.write(f"🔥 **Daily streak:** {st.session_state.streak} day(s)")

# XP actions
if st.sidebar.button("✅ I followed today's advice!"):
    st.session_state.xp += 10
    st.sidebar.success("Great! You earned **+10 XP**")

st.sidebar.progress(min(st.session_state.xp, 100))
st.sidebar.write(f"🏅 XP: **{st.session_state.xp}/100**")
if st.session_state.xp >= 100:
    st.sidebar.success("🎉 Level Up! You reached **Level 1**")

# Motivational quote
quotes = [
    "Small steps every day lead to big results.",
    "Consistency beats intensity.",
    "Focus on progress, not perfection.",
    "Discipline is choosing what you want most over what you want now.",
    "You don't have to be great to start, but you have to start to be great."
]
st.sidebar.markdown("### ✨ Motivation")
st.sidebar.info(random.choice(quotes))

# =========================== EXPORT SUMMARY ===========================
st.markdown("### 📤 Export")
if left and 'submitted' in locals() and submitted:
    # Compose a plain-text daily report
    balance = "Balanced" if 1 <= breaks <= 5 else ("Too Few" if breaks == 0 else "Too Many")
    report = f"""Study Report — {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}
------------------------------------------------------------
Inputs:
- Hours Studied: {hours} / Goal: {goal}  ({min(100, round((hours/goal)*100))}%)
- Breaks: {breaks} ({balance})
- Revision: {revision}
- Mood: {mood}
- Energy: {energy}
- Focus: {focus_area if focus_area else '—'}

Recommendations:
- """ + "\n- ".join(build_recommendations(hours, goal, breaks, revision, mood, energy, focus_area))

    st.download_button(
        label="⬇️ Download Today's Summary",
        data=report,
        file_name=f"study_summary_{dt.date.today().isoformat()}.txt",
        mime="text/plain",
        use_container_width=True
    )

# =========================== FOOTER ===========================
st.markdown(
    "<div style='text-align:center; color:var(--muted); margin-top:20px;'>"
    "Made to be friendly, fast, and offline — driven by simple rules and your inputs."
    "</div>",
    unsafe_allow_html=True
)
