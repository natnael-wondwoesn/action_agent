import streamlit as st
from chat import run
from utils.state_manager import generate_chat_id

st.set_page_config(page_title="LLM Chat Demo", layout="wide")

st.sidebar.title("Chat History")

# Initialize session state for storing chats
if "chats" not in st.session_state:
    st.session_state["chats"] = {}

# "New Chat" button
if st.sidebar.button("➕ New Chat"):
    new_chat_id = generate_chat_id()
    st.session_state["chats"][new_chat_id] = {"messages": [], "flow": []}
    st.session_state["selected_chat"] = new_chat_id  # Set new chat as selected

# Get available chat history
chat_keys = list(st.session_state["chats"].keys())

# Allow switching between chats
selected_chat = st.sidebar.radio("Select a chat", chat_keys, index=0) if chat_keys else None

# Store selected chat in session state
st.session_state["selected_chat"] = selected_chat

# Start chat
run(selected_chat)
