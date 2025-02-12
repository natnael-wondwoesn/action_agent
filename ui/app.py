import streamlit as st
from chat import run
from pages.browser_automation import render as render_browser_automation
from utils.state_manager import generate_chat_id

st.set_page_config(
    page_title="Action Agent Demo",
    layout="wide"
)

def main():
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    pages = {
        "Chat": chat_page,
        "Browser Automation": render_browser_automation,
    }
    
    # Create a radio button for navigation
    selection = st.sidebar.radio("Select a page", list(pages.keys()))
    
    # Call the selected page function
    page = pages[selection]
    page()

def chat_page():
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

if __name__ == "__main__":
    main()
