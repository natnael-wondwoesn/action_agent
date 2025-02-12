import streamlit as st
from typing import List
from infrastructure.browser_use.main import BrowserActionOutput, BrowserThought

def apply_browser_styles():
    """Apply custom CSS styles for browser automation display"""
    st.markdown("""
        <style>
            .browser-action {
                background-color: #f0f4f8;
                padding: 12px;
                border-radius: 8px;
                margin: 8px 0;
                border-left: 4px solid #3b82f6;
            }
            .browser-thought {
                background-color: #f8f0f4;
                padding: 12px;
                border-radius: 8px;
                margin: 8px 0;
                border-left: 4px solid #ec4899;
            }
            .timestamp {
                color: #6b7280;
                font-size: 0.875rem;
            }
        </style>
    """, unsafe_allow_html=True)

def display_browser_actions(actions: List[BrowserActionOutput], thoughts: List[BrowserThought]):
    """Display browser actions and thoughts in an interleaved timeline"""
    apply_browser_styles()
    
    st.subheader("Actions & Thoughts Timeline")
    
    # Create two columns for actions and thoughts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖱️ Browser Actions")
        for action in actions:
            with st.container():
                st.markdown(
                    f"""
                    <div class="browser-action">
                        <strong>{action.action_type}</strong>
                        <div class="timestamp">{action.timestamp or 'No timestamp'}</div>
                        <div>{str(action.action_data)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    with col2:
        st.markdown("### 💭 Model Thoughts")
        for thought in thoughts:
            with st.container():
                st.markdown(
                    f"""
                    <div class="browser-thought">
                        <div>{thought.thought}</div>
                        <div class="timestamp">{thought.timestamp or 'No timestamp'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
