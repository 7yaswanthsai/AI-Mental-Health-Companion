import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# -----------------------------------------------------
# 🔧 App Configuration
# -----------------------------------------------------
st.set_page_config(page_title="PAI-MHC", page_icon="💬", layout="centered")
st.title("🧠 Personalized AI Mental Health Companion")

API_BASE = "http://127.0.0.1:8000"
LOGIN_URL = f"{API_BASE}/login"
CHAT_URL = f"{API_BASE}/chat"
HISTORY_URL = f"{API_BASE}/history"
WELLNESS_URL = f"{API_BASE}/wellness"
RECS_URL = f"{API_BASE}/recommendations"

# -----------------------------------------------------
# 🔧 Session State
# -----------------------------------------------------
if "jwt" not in st.session_state:
    st.session_state.jwt = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm here to support you. How are you feeling today?"}
    ]

if "subject_id" not in st.session_state:
    st.session_state.subject_id = "S10"

if "pwi_history" not in st.session_state:
    st.session_state.pwi_history = []

if "rec_history" not in st.session_state:
    st.session_state.rec_history = []

# -----------------------------------------------------
# 🔐 Login Screen
# -----------------------------------------------------
if st.session_state.jwt is None:
    st.subheader("Login to continue")
    email = st.text_input("Email", "test@pai.com")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            res = requests.post(LOGIN_URL, json={"email": email, "password": pwd})
            if res.status_code == 200:
                st.session_state.jwt = res.json().get("access_token")
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Login failed: {e}")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.jwt}"}

# -----------------------------------------------------
# 🌤️ Welcome Message
# -----------------------------------------------------
st.markdown(
    "<h4 style='color:#4CAF50;'>💚 Welcome back. You’re not alone — I’m here with you.</h4>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------
# 📌 Sidebar Controls
# -----------------------------------------------------
st.sidebar.header("⚙️ Controls")
st.session_state.subject_id = st.sidebar.text_input("Subject ID", st.session_state.subject_id)

if st.sidebar.button("Refresh Wellness"):
    try:
        res = requests.get(f"{WELLNESS_URL}/{st.session_state.subject_id}", headers=headers)
        if res.status_code == 200:
            data = res.json()
            st.session_state.pwi_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "pwi": data.get("pwi"),
                "status": data.get("status"),
            })
            st.sidebar.success("Refreshed!")
        else:
            st.sidebar.error("Failed to fetch wellness data.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# -----------------------------------------------------
# 💬 Chat Input
# -----------------------------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        res = requests.post(
            CHAT_URL,
            headers=headers,
            json={"text": user_input, "subject_id": st.session_state.subject_id},
        )
        res.raise_for_status()

        data = res.json()
        bot_msg = data.get("text")
        wellness = data.get("wellness")
        recs = data.get("recommendations", [])

        st.session_state.messages.append({"role": "assistant", "content": bot_msg})

        if wellness:
            st.session_state.pwi_history.append({
                "timestamp": data.get("timestamp"),
                "pwi": wellness.get("pwi"),
                "status": wellness.get("status"),
            })

        if recs:
            st.session_state.rec_history.extend(recs)

    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Error: {e}"
        })

# -----------------------------------------------------
# 💬 Chat Messages Display
# -----------------------------------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -----------------------------------------------------
# 🩺 Current Wellness Snapshot
# -----------------------------------------------------
st.divider()
st.subheader("🩺 Current Wellness Overview")

latest_pwi = None
latest_status = None

if st.session_state.pwi_history:
    last = st.session_state.pwi_history[-1]
    latest_pwi = last.get("pwi")
    latest_status = last.get("status")

# Color mapping
color_map = {
    "Calm": "#4CAF50",
    "Neutral": "#2196F3",
    "Stressed": "#FF5722",
    "High Stress": "#D32F2F",
    "Unknown (No Data)": "#757575"
}

col1, col2 = st.columns(2)

col1.metric("PWI Score", latest_pwi if latest_pwi is not None else "—")
col2.markdown(
    f"<h4 style='color:{color_map.get(latest_status, '#000')}'>{latest_status or 'No Data'}</h4>",
    unsafe_allow_html=True
)

# -----------------------------------------------------
# 📈 Wellness History Trend
# -----------------------------------------------------
st.subheader("📈 Wellness Trend")
if st.session_state.pwi_history:
    df = pd.DataFrame(st.session_state.pwi_history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    st.line_chart(df["pwi"])
else:
    st.info("No wellness data yet. Send a message or refresh wellness.")

# -----------------------------------------------------
# 🧭 Recommendations (with History)
# -----------------------------------------------------
st.subheader("🧭 Recommendations")
if st.session_state.rec_history:
    with st.expander("View Recommendation History"):
        for r in st.session_state.rec_history:
            st.write(f"- {r}")
else:
    st.caption("No recommendations yet. Start chatting to receive guidance.")
