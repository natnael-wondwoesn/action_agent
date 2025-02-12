import streamlit as st

# Apply custom CSS for styling
def apply_chat_styles():
    st.markdown("""
        <style>
            .chat-container {
                display: flex;
                flex-direction: column;
                width: 100%;
                gap: 15px;
            }
            .agent-block {
                display: flex;
                justify-content: flex-start;
                width: 60%;
            }
            .agent-message {
                background-color: #e0f7fa;
                padding: 10px;
                border-radius: 10px;
                max-width:50%;
            }
            .thought-box {
                background: #f1f1f1;
                padding: 10px;
                border-radius: 10px;
                max-width: 50%;
            }
            .user-message-container {
                display: flex;
                justify-content: flex-end;
                width: 50%;
            }
            .user-message {
                background-color: #c8e6c9;
                padding: 10px;
                border-radius: 10px;
                max-width: 60%;
            }
        </style>
    """, unsafe_allow_html=True)

# Display chat messages in correct UI format
def display_chat(messages):
    # Start the chat container with a flex layout
    st.markdown('<div class="chat-container" style="display: flex; flex-direction: column; width: 100%;">', unsafe_allow_html=True)

    # Loop through the messages
    for message in messages:
        if message["type"] == "user":
            # User message - on the far right side of the chat
            st.markdown(f'<div class="user-message" style="align-self: flex-end; background-color: #e1f5fe; padding: 10px; border-radius: 8px;">**User:** {message["message"]}</div>', unsafe_allow_html=True)
        elif message["type"] == "agent":
            # Agent message - on the left side of the chat
            st.markdown(f'<div class="agent-message" style="align-self: flex-start; background-color: #f1f1f1; padding: 10px; border-radius: 8px;">**Agent:** {message["message"]}</div>', unsafe_allow_html=True)
        elif message["type"] == "thought":
            # Agent thoughts - collapsible component
            if "thoughts" in message:  # Ensure "thoughts" exists before displaying
                with st.expander("🤖 Agent's Thought Process"):
                    for thought in message["thoughts"]:
                        st.write(f"• {thought}")

    # End the chat container
    st.markdown('</div>', unsafe_allow_html=True)
