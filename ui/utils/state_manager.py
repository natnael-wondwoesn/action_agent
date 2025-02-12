import streamlit as st
import uuid

def init_session_state():
    if "chats" not in st.session_state:
        st.session_state["chats"] = {}

def generate_chat_id():
    return str(uuid.uuid4())[:8]  # Short unique ID
