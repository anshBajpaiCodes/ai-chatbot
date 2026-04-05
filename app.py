
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import json





load_dotenv()



# Setup client
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)







st.set_page_config(page_title="Ansh GPT", page_icon="🤖")
st.title("🤖 Ansh GPT")

# Sidebar
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Welcome Ansh 👋")
st.sidebar.divider()

FILE_PATH = "chat_history.json"

# ✅ CREATE FILE IF NOT EXISTS
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as f:
        json.dump([], f)

# ✅ SAFE LOAD FUNCTION (no crash)
def load_chat():
    try:
        with open(FILE_PATH, "r") as f:
            data = f.read().strip()
            if data == "":
                return []
            return json.loads(data)
    except:
        return []

# ✅ SAFE SAVE FUNCTION
def save_chat(messages):
    with open(FILE_PATH, "w") as f:
        json.dump(messages, f, indent=2)

# ✅ CLEAR CHAT (FIXED)
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful English teacher."}
    ]
    save_chat([])   # always valid JSON
    st.rerun()      # 🔥 important

# ✅ INITIALIZE MEMORY (ONLY ONCE)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful English teacher. Remember user's name and context."
        }
    ] + load_chat()

# ✅ SHOW CHAT
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✅ INPUT
if prompt := st.chat_input("Type your message..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=st.session_state.messages,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "Ansh GPT"
                }
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # 💾 SAVE CHAT
    save_chat(st.session_state.messages[1:])