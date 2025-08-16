# app.py
import time
import random
import datetime as dt
from io import BytesIO

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# ===========================
# CONFIG & STATE
# ===========================
st.set_page_config(
    page_title="📘 Study Pattern Analyzer — Super Edition",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

def init_state():
    ss = st.session_state
    ss.setdefault("theme", "Dark")
    ss.setdefault("xp", 0)
    ss.setdefault("streak", 0)
    ss.setdefault("last_log_date", None)
    ss.setdefault("chat", [])          # (role, text)
    ss.setdefault("buddy_chat", [])    # (who, text)
    ss.setdefault("hours", 4.0)
    ss.setdefault("goal", 6.0)
    ss.setdefault("breaks", 2)
    ss.setdefault("revision", "Yes")
    ss.setdefault("mood", "Happy")
    ss.setdefault("energy", "High")
    ss.setdefault("focus", "")
    # Music
    ss.setdefault("music_on", False)
    ss.setdefault("music_track", "Lo-fi Focus")
    # Pomodoro
    ss.setdefault("pomo_running", False)
    ss.setdefault("pomo_mode", "Work")       # Work / Break
    ss.setdefault("pomo_work_min", 25)
    ss.setdefault("pomo_break_min", 5)
    ss.setdefault("pomo_target_ts", None)    # epoch seconds when current phase ends
    # Buddy
    ss.setdefault("buddy", "Coach Nova")

init_state()

# ===========================
# THEME
# ===========================
LIGHT = {
    "--bg1": "#F7F9FC", "--bg2": "#ECF2FF", "--card": "#FFFFFF", "--text": "#0F172A",
    "--muted": "#475569", "--accent": "#4F46E5", "--success": "#10B981",
    "--warn": "#F59E0B", "--danger": "#EF4444"
}
DARK = {
    "--bg1": "#0f1220", "--bg2": "#171a2e", "--card": "#1f2442", "--text": "#e6e9f5",
    "--muted": "#b8c1ec", "--accent": "#7c9cff", "--success": "#61d095",
    "--warn": "#ffb84d", "--danger": "#ff6b6b"
}
THEME = LIGHT if st.session_state.theme == "Light" else DARK

st.markdown(
    f"""
    <style>
      :root {{
        --bg1:{THEME['--bg1']}; --bg2:{THEME['--bg2']}; --card:{THEME['--card']};
        --text:{THEME['--text']}; --muted:{THEME['--muted']}; --accent:{THEME['--accent']};
        --success:{THEME['--success']}; --warn:{THEME['--warn']}; --danger:{THEME['--danger']};
      }}
      .stApp {{
        background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
      }}
      .glass {{
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
      }}
      .metric {{
        display:flex; align-items:center; gap:12px; padding:10px 12px; border-radius:14px;
        background: rgba(255,255,255,0.30); border:1px solid rgba(0,0,0,0.06);
      }}
      .chip {{
        display:inline-block; padding:6px 10px; border-radius:20px; font-size:0.9rem;
        background: rgba(255,255,255,0.40); border:1px solid rgba(0,0,0,0.06);
      }}
      .bubble {{ padding:12px 14px; margin:8px 0; border-radius: 14px; max-width: 90%; border:1px solid rgba(0,0,0,0.06); }}
      .user {{ margin-left:auto; background:rgba(79,70,229,0.18); }}
      .bot  {{ margin-right:auto; background:rgba(0,0,0,0.06); }}
      .ring {{
        width: 160px; height:160px; border-radius:50%; position: relative; display:inline-block;
        background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(0,0,0,0.08) 0);
      }}
      .ring::after {{ content:""; position:absolute; inset:10px; border-radius:50%; background: var(--card); border: 1px solid rgba(0,0,0,0.06); }}
      .ring-label {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:700; color:var(--text); }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===========================
# HELPERS
# ===========================
def percent(hours, goal):
    try:
        return min(100, round((hours / goal) * 100))
    except ZeroDivisionError:
        return 0

def format_seconds(total_s: int) -> str:
    total_s = max(0, int(total_s))
    m, s = divmod(total_s, 60)
    return f"{m:02d}:{s:02d}"

def now_ts():
    return int(time.time())

def phase_seconds(mode: str) -> int:
    if mode == "Work":
        return int(st.session_state.pomo_work_min * 60)
    return int(st.session_state.pomo_break_min * 60)

def start_phase(mode: str):
    st.session_state.pomo_mode = mode
    st.session_state.pomo_target_ts = now_ts() + phase_seconds(mode)
    st.session_state.pomo_running = True

def stop_timer():
    st.session_state.pomo_running = False

def reset_timer():
    st.session_state.pomo_running = False
    st.session_state.pomo_mode = "Work"
    st.session_state.pomo_target_ts = None

def current_remaining():
    if not st.session_state.pomo_running or st.session_state.pomo_target_ts is None:
        return phase_seconds(st.session_state.pomo_mode)
    return max(0, st.session_state.pomo_target_ts - now_ts())

def buddy_msg(trigger="general"):
    p = st.session_state.buddy
    bank = {
        "general": {
            "Coach Nova": "I’m proud of the consistency. One more small win today!",
            "Zen Panda": "Breathe in focus, breathe out distraction. You’ve got this.",
            "Professor Byte": "Incremental improvements compile into greatness."
        },
        "work_start": {
            "Coach Nova": "Work block started. Keep your eyes on the rep count.",
            "Zen Panda": "Focus like water—flow through one problem at a time.",
            "Professor Byte": "Executing deep work routine… expect performance gains."
        },
        "break_start": {
            "Coach Nova": "Break time! Shake it out, hydrate, then back to it.",
            "Zen Panda": "Rest the mind to sharpen the blade of thought.",
            "Professor Byte": "Garbage collection in progress—refreshing mental memory."
        },
        "goal_hit": {
            "Coach Nova": "Goal hit! That’s how you build momentum.",
            "Zen Panda": "Harmony achieved. Let gratitude close the day.",
            "Professor Byte": "Target reached. Logging achievement badge."
        }
    }
    return bank.get(trigger, bank["general"]).get(p, bank["general"]["Coach Nova"])

def build_recommendations(h, g, b, rev, md, en, focus):
    recs = []
    if h < g * 0.6: recs.append("📈 You studied less than planned. Schedule **two 45-min blocks** tomorrow.")
    elif h < g:     recs.append("👍 Close to your goal—add **one extra 30-min session**.")
    else:           recs.append("🏅 Goal achieved! Do a **quick recap** to lock it in.")
    if b == 0:      recs.append("☕ Add **short 5-min breaks** every 25–30 minutes.")
    elif b > 6:     recs.append("🧭 Too many breaks—aim for **2–5** evenly spaced.")
    if rev == "No": recs.append("🔁 Do **10-minute active recall** on yesterday’s topic.")
    if md == "Stressed" and en in ("Low","Medium"): recs.append("🧘 Try **box breathing (5 min)** or a brief walk.")
    if md == "Tired" and en == "Low": recs.append("😴 Take a **20-min power nap** then one short session.")
    if md == "Happy" and en == "High": recs.append("🚀 Plan a **deep work block (60–90 min)** on your hardest topic.")
    if focus:       recs.append(f"🎯 Stick to **{focus}** and end with a **3-point summary**.")
    recs.extend(random.sample([
        "📚 Start each session by **rewriting your block goal**.",
        "📝 Use **active recall** instead of rereading.",
        "⏱️ Use **Pomodoro (25/5)** for sustained focus.",
        "📵 Keep your phone **outside the room**.",
        "🧪 End with a **5-question self-quiz**.",
        "🌙 Review key points **before sleep**."
    ], 2))
    return recs

def growth_stage(pct):
    if pct < 30:   return "🌱 Seedling — just getting started."
    if pct < 70:   return "🌿 Sapling — growing strong."
    if pct < 100:  return "🌳 Tree — almost there!"
    return "🌸 Flourishing — goal achieved!"

# ===========================
# HEADER
# ===========================
col_logo, col_title, col_theme = st.columns([0.6, 2, 1])
with col_logo:
    st.markdown("### 📘")
with col_title:
    st.markdown("## Study Pattern Analyzer — **Super Edition**")
    st.caption("Coaching you with timers, music, voice input, a growth tree, and a friendly study buddy.")
with col_theme:
    mode = st.radio("Appearance", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, horizontal=True)
    if mode != st.session_state.theme:
        st.session_state.theme = mode
        st.experimental_rerun()

st.write("")

# ===========================
# LAYOUT
# ===========================
left, mid, right = st.columns([1.15, 1, 1.1])

# ---------------------------
# LEFT: INPUTS + TREE + MUSIC
# ---------------------------
with left:
    st.markdown("### ✨ Your Study Inputs")
    with st.form("study_form", clear_on_submit=False):
        st.session_state.hours  = st.slider("📚 Hours studied today", 0.0, 12.0, float(st.session_state.hours), 0.5)
        st.session_state.goal   = st.slider("🎯 Daily goal (hours)", 1.0, 12.0, float(st.session_state.goal), 0.5)
        st.session_state.breaks = st.slider("☕ Breaks taken", 0, 12, int(st.session_state.breaks), 1)
        st.session_state.revision = st.selectbox("🔁 Did you revise today?", ["Yes", "No"], index=0 if st.session_state.revision=="Yes" else 1)
        st.session_state.mood     = st.selectbox("😊 Mood today", ["Happy", "Neutral", "Stressed", "Tired"],
                                                 index=["Happy","Neutral","Stressed","Tired"].index(st.session_state.mood))
        st.session_state.energy   = st.selectbox("⚡ Energy level", ["High", "Medium", "Low"],
                                                 index=["High","Medium","Low"].index(st.session_state.energy))
        st.session_state.focus    = st.text_input("📌 Focus topic (optional)", value=st.session_state.focus, placeholder="e.g., Calculus, DBMS…")
        submitted = st.form_submit_button("🔍 Analyze", use_container_width=True)

    # 🌱 Growth Tree
    pct = percent(st.session_state.hours, st.session_state.goal)
    tree = growth_stage(pct)
    st.markdown("### 🌱 Growth Tree")
    st.markdown(
        f"""
        <div class="glass">
          <div style="font-size: 2rem;">{tree.split('—')[0]}</div>
          <div style="margin-top:6px;">{tree}</div>
          <div style="margin-top:10px;" class="chip">Progress: {pct}%</div>
        </div>
        """, unsafe_allow_html=True
    )

    # 🎶 Background Music
    st.markdown("### 🎶 Background Music")
    tracks = {
        "Lo-fi Focus": "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Saw_Cassette/Angstspridaren/Saw_Cassette_-_05_-_3rd_Room.mp3",
        "Soft Piano": "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Komiku/It_is_time_for_adventure/Komiku_-_07_-_Its_time_for_adventure.mp3",
        "Ambient Rain": "https://file-examples.com/storage/fef7e9005ab8b309/2017/11/file_example_MP3_1MG.mp3"
    }
    st.session_state.music_on = st.toggle("Play background music", value=st.session_state.music_on)
    st.session_state.music_track = st.selectbox("Track", list(tracks.keys()), index=list(tracks.keys()).index(st.session_state.music_track))
    if st.session_state.music_on:
        st.audio(tracks[st.session_state.music_track], format="audio/mp3")

# ---------------------------
# MID: SUMMARY + RING + POMODORO (auto-update)
# ---------------------------
with mid:
    st.markdown("### 📊 Today at a Glance")
    pct = percent(st.session_state.hours, st.session_state.goal)
    st.markdown(
        f"""
        <div class="glass" style="text-align:center;">
          <div class="ring" style="--p:{pct};">
            <div class="ring-label">{pct}%</div>
          </div>
          <div style="margin-top:10px; color:var(--muted);">Goal Completion</div>
          <div class="chip" style="margin-top:10px;">⏳ {st.session_state.hours}h / 🎯 {st.session_state.goal}h</div>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("")
    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            f"""
            <div class="metric">
              <div>🧠</div>
              <div><b>Revision</b><br><span style="color:var(--muted)">{'Completed' if st.session_state.revision=='Yes' else 'Pending'}</span></div>
            </div>
            """, unsafe_allow_html=True
        )
    with colB:
        balance = "Balanced" if 1 <= st.session_state.breaks <= 5 else ("Too Few" if st.session_state.breaks == 0 else "Too Many")
        st.markdown(
            f"""
            <div class="metric">
              <div>☕</div>
              <div><b>Breaks</b><br><span style="color:var(--muted)">{st.session_state.breaks} ({balance})</span></div>
            </div>
            """, unsafe_allow_html=True
        )

    # ⏱️ Pomodoro Timer
    st.markdown("### ⏱️ Pomodoro")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    with c1:
        st.number_input("Work (min)", min_value=5, max_value=90, value=st.session_state.pomo_work_min, step=5, key="pomo_work_min")
    with c2:
        st.number_input("Break (min)", min_value=1, max_value=30, value=st.session_state.pomo_break_min, step=1, key="pomo_break_min")
    with c3:
        st.write(" ")
        if st.button("Start / Resume" if not st.session_state.pomo_running else "Pause", use_container_width=True):
            if st.session_state.pomo_running:
                stop_timer()
            else:
                # (Re)start current phase with remaining seconds (if paused) or fresh phase if none
                remaining = current_remaining()
                st.session_state.pomo_target_ts = now_ts() + remaining
                st.session_state.pomo_running = True
                if st.session_state.pomo_mode == "Work":
                    st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("work_start")))
                else:
                    st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("break_start")))
            st.rerun()
    with c4:
        st.write(" ")
        if st.button("Reset", use_container_width=True):
            reset_timer()
            st.rerun()

    # Show remaining, flip mode when time hits zero
    remaining = current_remaining()
    if st.session_state.pomo_running and remaining == 0:
        # switch phase
        next_mode = "Break" if st.session_state.pomo_mode == "Work" else "Work"
        start_phase(next_mode)
        if next_mode == "Work":
            st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("work_start")))
        else:
            st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("break_start")))
        st.rerun()

    st.markdown(
        f"""
        <div class="glass" style="text-align:center;">
          <div class="chip">{'🟢 Running' if st.session_state.pomo_running else '⏸️ Paused'} • {st.session_state.pomo_mode} Mode</div>
          <h2 style="margin:6px 0;">{format_seconds(remaining)}</h2>
          <div style="color:var(--muted)">Focus during Work • Stretch during Breaks</div>
        </div>
        """, unsafe_allow_html=True
    )

    # Small auto-refresh effect while running
    if st.session_state.pomo_running:
        time.sleep(1)
        st.rerun()

# ---------------------------
# RIGHT: VOICE + BUDDY + RECS + PDF
# ---------------------------
with right:
    st.markdown("### 🎙️ Voice Input (Chrome recommended)")
    st.caption("Click Start, speak (e.g., 'I studied 3 hours, mood stressed'), then copy the transcript into any field below.")
    st.components.v1.html(
        """
        <div style="padding:12px;border-radius:12px;border:1px solid #ccc;background:#fff;color:#111;font-family:sans-serif">
          <button id="start" style="padding:8px 12px;border-radius:8px;border:1px solid #333;cursor:pointer;">🎤 Start</button>
          <button id="stop"  style="padding:8px 12px;border-radius:8px;border:1px solid #333;cursor:pointer;margin-left:6px;">⏹️ Stop</button>
          <div style="margin-top:8px;font-size:12px;color:#333;">(Uses your browser's Web Speech API; works best on Chrome.)</div>
          <textarea id="out" rows="5" style="width:100%;margin-top:8px;border-radius:8px;padding:8px;border:1px solid #999;"></textarea>
          <button id="copy" style="margin-top:6px;padding:6px 10px;border-radius:8px;border:1px solid #333;cursor:pointer;">📋 Copy transcript</button>
        </div>
        <script>
          let rec;
          function supports() { return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window; }
          const startBtn = document.getElementById('start');
          const stopBtn  = document.getElementById('stop');
          const out = document.getElementById('out');
          const copyBtn = document.getElementById('copy');
          if(!supports()){
            out.value = "Speech recognition not supported in this browser. Try Chrome on desktop.";
            startBtn.disabled = true; stopBtn.disabled = true;
          } else {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            rec = new SR(); rec.lang='en-US'; rec.interimResults = true; rec.continuous = true;
            rec.onresult = (e) => {
              let txt = '';
              for (let i= e.resultIndex; i< e.results.length; i++) {{
                txt += e.results[i][0].transcript;
              }}
              out.value = txt;
            };
            rec.onerror = (e) => {{ console.log('SR error', e); }};
          }
          startBtn.onclick = () => {{ try {{ rec && rec.start(); }} catch(e){{}} }};
          stopBtn.onclick  = () => {{ try {{ rec && rec.stop(); }} catch(e){{}} }};
          copyBtn.onclick  = async () => {{ try {{ await navigator.clipboard.writeText(out.value); copyBtn.innerText = "✅ Copied"; setTimeout(()=> copyBtn.innerText = "📋 Copy transcript", 1400);} catch(e){{}} }}
        </script>
        """,
        height=220,
    )

    # Buddy selection
    st.markdown("### 🧑‍🤝‍🧑 Study Buddy")
    persona = st.selectbox("Choose your buddy", ["Coach Nova", "Zen Panda", "Professor Byte"],
                           index=["Coach Nova","Zen Panda","Professor Byte"].index(st.session_state.buddy))
    if persona != st.session_state.buddy:
        st.session_state.buddy = persona

    # Analyze -> recommendations
    if submitted:
        recs = build_recommendations(
            st.session_state.hours, st.session_state.goal, st.session_state.breaks,
            st.session_state.revision, st.session_state.mood, st.session_state.energy, st.session_state.focus
        )
        user_line = f"Hours:{st.session_state.hours} Goal:{st.session_state.goal} Breaks:{st.session_state.breaks} Rev:{st.session_state.revision} Mood:{st.session_state.mood} Energy:{st.session_state.energy} Focus:{st.session_state.focus or '—'}"
        st.session_state.chat.append(("user", user_line))
        st.session_state.chat.append(("bot", "\n".join(recs)))
        # Goal hit -> XP, streak, buddy
        if st.session_state.hours >= st.session_state.goal:
            st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("goal_hit")))
            st.session_state.xp += 20
            today = dt.date.today().isoformat()
            if st.session_state.last_log_date != today:
                if st.session_state.last_log_date:
                    last = dt.date.fromisoformat(st.session_state.last_log_date)
                    if (dt.date.today() - last).days == 1:
                        st.session_state.streak += 1
                    elif (dt.date.today() - last).days > 1:
                        st.session_state.streak = 1
                else:
                    st.session_state.streak = 1
                st.session_state.last_log_date = today

    st.markdown("### 💡 Recommendations")
    if 'recs' in locals() and submitted:
        for r in recs:
            st.markdown(f"- {r}")
    else:
        st.info("Fill inputs and click **Analyze** for tailored tips.")

    # ----- PDF EXPORT -----
    st.markdown("### 📄 Export Today's Report (PDF)")
    def build_pdf() -> BytesIO:
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        x, y = 50, height - 50

        def write_line(text, font="Helvetica", size=11, dy=16):
            nonlocal y
            c.setFont(font, size)
            c.drawString(x, y, text)
            y -= dy
            if y < 60:
                c.showPage()
                y = height - 50

        def write_wrap(text, max_width=500, bullet=False):
            nonlocal y
            c.setFont("Helvetica", 11)
            lines = simpleSplit(text, "Helvetica", 11, max_width)
            for ln in lines:
                c.drawString(x + (12 if bullet else 0), y, ("- " if bullet else "") + ln)
                y -= 16
                if y < 60:
                    c.showPage()
                    y = height - 50

        # Header
        write_line("Study Report", "Helvetica-Bold", 18, 22)
        write_line(dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "Helvetica", 10, 18)
        y -= 6

        # Inputs
        write_line("Inputs", "Helvetica-Bold", 14, 18)
        write_line(f"Hours Studied: {st.session_state.hours}")
        write_line(f"Goal (hours): {st.session_state.goal}")
        write_line(f"Goal Completion: {percent(st.session_state.hours, st.session_state.goal)}%")
        write_line(f"Breaks: {st.session_state.breaks}")
        write_line(f"Revision: {st.session_state.revision}")
        write_line(f"Mood: {st.session_state.mood}")
        write_line(f"Energy: {st.session_state.energy}")
        write_line(f"Focus: {st.session_state.focus or '—'}")
        y -= 6

        # Gamification
        write_line("Progress", "Helvetica-Bold", 14, 18)
        write_line(f"XP: {st.session_state.xp}")
        write_line(f"Streak: {st.session_state.streak} day(s)")
        y -= 6

        # Recommendations (last bot message)
        write_line("Recommendations", "Helvetica-Bold", 14, 18)
        last_bot = ""
        for role, text in reversed(st.session_state.chat):
            if role == "bot":
                last_bot = text
                break
        if last_bot:
            for line in last_bot.split("\n"):
                write_wrap(line, bullet=True)
        else:
            write_wrap("No recommendations generated yet.")

        # Buddy snippets (last 3)
        y -= 6
        write_line("Buddy Messages", "Helvetica-Bold", 14, 18)
        if st.session_state.buddy_chat:
            for who, msg in st.session_state.buddy_chat[-3:]:
                write_wrap(f"{who}: {msg}", bullet=True)
        else:
            write_wrap("No buddy messages yet.")

        c.showPage()
        c.save()
        buf.seek(0)
        return buf

    pdf_bytes = build_pdf()
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name=f"study_report_{dt.date.today().isoformat()}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ===========================
# INSIGHTS FEED & BUDDY FEED
# ===========================
st.markdown("### 💬 Insights Feed")
for role, text in st.session_state.chat[-6:]:
    cls = "user" if role == "user" else "bot"
    st.markdown(f"<div class='bubble {cls}'>{text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

st.markdown("### 🧑‍🤝‍🧑 Buddy Corner")
for who, msg in st.session_state.buddy_chat[-4:]:
    st.markdown(f"<div class='bubble bot'><b>{who}:</b> {msg}</div>", unsafe_allow_html=True)

# ===========================
# SIDEBAR: PROGRESS & QUICK POMODORO
# ===========================
with st.sidebar:
    st.header("🎮 Progress")
    st.progress(min(st.session_state.xp, 100))
    st.write(f"🏅 XP: **{st.session_state.xp}/100**")
    st.write(f"🔥 Streak: **{st.session_state.streak}** day(s)")

    st.divider()
    st.header("⏱️ Pomodoro Quick")
    if st.button("▶️ Start Work"):
        start_phase("Work")
        st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("work_start")))
        st.experimental_rerun()
    if st.button("☕ Start Break"):
        start_phase("Break")
        st.session_state.buddy_chat.append((st.session_state.buddy, buddy_msg("break_start")))
        st.experimental_rerun()
    if st.button("⏸️ Pause"):
        stop_timer()
    if st.button("🔄 Reset"):
        reset_timer()

st.caption("Tip: Use Voice Input (Chrome) to dictate your study log. Toggle music and theme in the app for a cozy focus vibe ✨")
