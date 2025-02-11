import streamlit as st

def display_chat(messages):
    for message in messages:
        if message["type"] == "user":
            st.markdown(f"**User:** {message['message']}")
        elif message["type"] == "agent":
            st.markdown(f"**Agent:** {message['message']}")
        elif message["type"] == "thought":
            with st.expander("🤖 Thinking..."):
                for thought in message["thoughts"]:
                    st.write(thought)
