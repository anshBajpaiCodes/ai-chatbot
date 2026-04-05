import streamlit as st
from openai import OpenAI
import sqlite3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------ DATABASE SETUP ------------------
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    session_id TEXT,
    role TEXT,
    content TEXT
)
""")
conn.commit()

# ------------------ SESSION ID ------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ------------------ DB FUNCTIONS ------------------
def load_chat(session_id):
    cursor.execute("SELECT role, content FROM chats WHERE session_id=?", (session_id,))
    return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def save_message(session_id, role, content):
    cursor.execute(
        "INSERT INTO chats (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()

def clear_chat(session_id):
    cursor.execute("DELETE FROM chats WHERE session_id=?", (session_id,))
    conn.commit()

# ------------------ API KEY (LOCAL + DEPLOY BOTH) ------------------
api_key = None

try:
    api_key = st.secrets["OPENROUTER_API_KEY"]  # Streamlit
except:
    api_key = os.getenv("OPENROUTER_API_KEY")   # Local

if not api_key:
    st.error("API key not found. Set in .env or Streamlit secrets.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# ------------------ UI ------------------
st.set_page_config(page_title="Ansh GPT", page_icon="🤖")
st.title("🤖 Ansh GPT")

# Sidebar
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Welcome 👋")

# Clear Chat Button
if st.sidebar.button("🗑️ Clear Chat"):
    clear_chat(st.session_state.session_id)
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.rerun()

# ------------------ LOAD MEMORY ------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ] + load_chat(st.session_state.session_id)

# ------------------ SHOW CHAT ------------------
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ INPUT ------------------
if prompt := st.chat_input("Type your message..."):

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    save_message(st.session_state.session_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=st.session_state.messages,
                extra_headers={
                    "HTTP-Referer": "https://your-app.streamlit.app",
                    "X-Title": "Ansh GPT"
                }
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save AI message
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
    save_message(st.session_state.session_id, "assistant", reply)