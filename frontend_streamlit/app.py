import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import time

# -----------------------------------------------------
# App Configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="PAI-MHC",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .welcome-message {
        background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .pwi-card-green {
        background: #e8f5e9;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pwi-card-yellow {
        background: #fff9c4;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pwi-card-red {
        background: #ffebee;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pwi-card-unknown {
        background: #f5f5f5;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #9e9e9e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-item {
        background: #fde3c6;
        padding: 0.75rem;
        margin: 0.4rem 0;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        color: #333333;
        font-size: 0.95rem;
    }
    .chat-bubble-user {
        background: #e3f2fd;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-bubble-bot {
        background: #f1f8e9;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧠 Personalized AI Mental Health Companion</div>', unsafe_allow_html=True)

API_BASE = "http://127.0.0.1:8000"
LOGIN_URL = f"{API_BASE}/login"
CHAT_URL = f"{API_BASE}/chat"
HISTORY_URL = f"{API_BASE}/history"
WELLNESS_URL = f"{API_BASE}/wellness"
RECS_URL = f"{API_BASE}/recommendations"

# -----------------------------------------------------
# Session State
# -----------------------------------------------------
if "jwt" not in st.session_state:
    st.session_state.jwt = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm here to support you.", "timestamp": datetime.now().strftime("%H:%M:%S")}
    ]

if "subject_id" not in st.session_state:
    st.session_state.subject_id = "S10"

if "pwi_history" not in st.session_state:
    st.session_state.pwi_history = []

if "rec_history" not in st.session_state:
    st.session_state.rec_history = []

# -----------------------------------------------------
# Login
# -----------------------------------------------------
if st.session_state.jwt is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Login to continue")
        email = st.text_input("Email", "test@pai.com")
        pwd = st.text_input("Password", type="password")
        if st.button("Login", type="primary"):
            with st.spinner("Logging in..."):
                try:
                    res = requests.post(LOGIN_URL, json={"email": email, "password": pwd}, timeout=10)
                    if res.status_code == 200:
                        st.session_state.jwt = res.json().get("access_token")
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error(f"Login failed: {e}")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.jwt}"}

# -----------------------------------------------------
# Welcome Message
# -----------------------------------------------------
st.markdown(
    '<div class="welcome-message"><h4 style="color:#4CAF50;margin:0;">💚 Welcome back. I\'m here with you.</h4></div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
with st.sidebar:
    st.header("⚙️ Session Controls")

    st.session_state.subject_id = st.text_input("Subject ID", st.session_state.subject_id)

    colA, colB = st.columns(2)

    with colA:
        if st.button("🔄 Refresh Wellness"):
            try:
                res = requests.get(f"{WELLNESS_URL}/{st.session_state.subject_id}", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.pwi_history.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "pwi": data.get("pwi"),
                        "status": data.get("status"),
                    })
                    st.success("Wellness updated")
                else:
                    st.error("Failed to fetch wellness")
            except Exception as e:
                st.error(f"Error: {e}")

    with colB:
        if st.button("📜 Load History"):
            try:
                res = requests.get(HISTORY_URL, headers=headers)
                if res.status_code == 200:
                    st.success("History loaded")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    if st.button("🚪 Logout", type="secondary"):
        st.session_state.jwt = None
        st.session_state.messages = []
        st.session_state.pwi_history = []
        st.session_state.rec_history = []
        st.rerun()

# -----------------------------------------------------
# Main Layout (Chat + Wellness)
# -----------------------------------------------------
col_chat, col_wellness = st.columns([2, 1])

# ---------------- CHAT DISPLAY ----------------
with col_chat:
    st.subheader("💬 Conversation")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            role = msg["role"]
            timestamp = msg.get("timestamp", datetime.now().strftime("%H:%M:%S"))
            content = msg["content"]

            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)
                    st.caption(f"🕐 {timestamp}")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)
                    st.caption(f"🕐 {timestamp}")
                    # Show emotion and tone as badges
                    metadata_cols = st.columns([1, 1])
                    if "emotion" in msg:
                        with metadata_cols[0]:
                            st.caption(f"🎭 {msg['emotion']}")
                    if "tone" in msg:
                        with metadata_cols[1]:
                            st.caption(f"🎨 {msg['tone']}")

# ---------------- WELLNESS DASHBOARD ----------------
with col_wellness:
    st.subheader("🩺 Wellness Dashboard")

    latest_pwi = None
    latest_status = None

    if st.session_state.pwi_history:
        latest = st.session_state.pwi_history[-1]
        latest_pwi = latest["pwi"]
        latest_status = latest["status"]

    # Colored PWI Card
    if latest_pwi is not None:
        if latest_pwi >= 70:
            card_class = "pwi-card-green"
            status_emoji = "🟢"
            status_text = "Good"
        elif latest_pwi >= 40:
            card_class = "pwi-card-yellow"
            status_emoji = "🟡"
            status_text = "Moderate"
        else:
            card_class = "pwi-card-red"
            status_emoji = "🔴"
            status_text = "Low"
        
        st.markdown(
            f"""
            <div class="{card_class}">
                <h3 style="margin:0;color:#333;">{status_emoji} PWI Score: <strong>{latest_pwi:.1f}</strong></h3>
                <p style="margin:0.5rem 0 0 0;color:#666;">Status: <strong>{latest_status or status_text}</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="pwi-card-unknown">
                <h3 style="margin:0;color:#333;">⚪ PWI Score: N/A</h3>
                <p style="margin:0.5rem 0 0 0;color:#666;">No wellness data available</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("📈 Trend")
    if st.session_state.pwi_history:
        df = pd.DataFrame(st.session_state.pwi_history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
        st.line_chart(df["pwi"], height=200)
    else:
        st.caption("No history yet. Send a message to start tracking.")

    st.divider()

    # Collapsible Recommendations
    with st.expander("💡 Recommendations History", expanded=True):
        if st.session_state.rec_history:
            # Show last 5 recommendations
            for rec in st.session_state.rec_history[-5:]:
                st.markdown(
                    f"""
                    <div class='recommendation-item'>
                        💡 <strong>{rec['text']}</strong><br>
                        <span style="font-size:0.8rem;color:#666;">{rec['timestamp']}</span>
                        {f"<span style='font-size:0.8rem;color:#999;'> • Emotion: {rec.get('emotion', 'N/A')}</span>" if 'emotion' in rec else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No recommendations yet. Recommendations will appear here after chatting.")

# -----------------------------------------------------
# CHAT INPUT (MUST BE OUTSIDE COLUMNS)
# -----------------------------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    st.rerun()

# -----------------------------------------------------
# PROCESS BOT RESPONSE
# -----------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_msg = st.session_state.messages[-1]["content"]
    
    # Show loading indicator
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        with st.spinner("🤔 Thinking... Analyzing your message and preparing a response."):
            try:
                res = requests.post(
                    CHAT_URL,
                    headers=headers,
                    json={"text": last_user_msg, "subject_id": st.session_state.subject_id},
                    timeout=15
                )
                res.raise_for_status()

                data = res.json()
                bot_msg = data.get("text", "I'm here for you.")
                emotion = data.get("emotion")
                tone = data.get("tone")
                wellness = data.get("wellness", {})
                recs = data.get("recommendations", [])
                escalate = data.get("escalate", False)

                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_msg,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "emotion": emotion,
                    "tone": tone,
                    "escalate": escalate
                })

                # Update PWI history if available
                if wellness and wellness.get("pwi") is not None:
                    pwi_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "pwi": wellness["pwi"],
                        "status": wellness.get("status", "Unknown")
                    }
                    # Avoid duplicates
                    if not st.session_state.pwi_history or st.session_state.pwi_history[-1] != pwi_entry:
                        st.session_state.pwi_history.append(pwi_entry)

                # Add recommendations
                for r in recs:
                    rec_entry = {
                        "text": r,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "emotion": emotion
                    }
                    # Avoid duplicates
                    if not st.session_state.rec_history or st.session_state.rec_history[-1]["text"] != r:
                        st.session_state.rec_history.append(rec_entry)

                loading_placeholder.empty()
                st.rerun()

            except requests.exceptions.Timeout:
                loading_placeholder.empty()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⏱️ The request took too long. Please try again.",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
            except requests.exceptions.RequestException as e:
                loading_placeholder.empty()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Connection error: {str(e)}. Please check if the backend is running.",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
            except Exception as e:
                loading_placeholder.empty()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {str(e)}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()

# -----------------------------------------------------
# Footer Stats
# -----------------------------------------------------
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Messages", len(st.session_state.messages))
c2.metric("Wellness Points", len(st.session_state.pwi_history))
c3.metric("Recommendations", len(st.session_state.rec_history))
c4.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
