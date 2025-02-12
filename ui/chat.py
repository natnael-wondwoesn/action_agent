import streamlit as st
from components.chat_component import display_chat
from utils.state_manager import init_session_state, generate_chat_id

def run(selected_chat=None):
    st.title("Chat with LLM")

    init_session_state()

    # If selected chat exists, use its flow; otherwise, create a new chat
    if selected_chat and selected_chat in st.session_state["chats"]:
        chat_data = st.session_state["chats"][selected_chat]
        flow = chat_data["flow"]
    else:
        chat_id = generate_chat_id()
        flow = []
        st.session_state["chats"][chat_id] = {"messages": [], "flow": flow}
        selected_chat = chat_id  # Assign chat_id for a new session

    st.session_state["selected_chat"] = selected_chat  # Store globally

    user_input = st.text_input("Enter your task:")

    if user_input:
        # Store user message
        st.session_state["chats"][selected_chat]["messages"].append({"type": "user", "message": user_input})

        # Simulate agent response
        agent_response = f"Task '{user_input}' completed successfully."
        thought_process = ["Analyzing task...", "Executing step 1...", "Finalizing response..."]
        new_flow_step = {"task": user_input, "steps": thought_process, "status": "completed"}

        # Store thoughts and response
        st.session_state["chats"][selected_chat]["messages"].append({"type": "thought", "thoughts": thought_process})
        st.session_state["chats"][selected_chat]["messages"].append({"type": "agent", "message": agent_response})

        # Update flow
        st.session_state["chats"][selected_chat]["flow"].append(new_flow_step)

    # Display chat
    display_chat(st.session_state["chats"][selected_chat]["messages"])
