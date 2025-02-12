import streamlit as st
import asyncio
import os
from infrastructure.browser_use.main import BrowserUseAgent
from components.browser_component import display_browser_actions
from utils.state_manager import init_session_state

def run_browser_automation():
    st.title("Browser Automation")
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("""
        No Gemini API key found. Please set up your API key in one of these ways:
        1. Create a `.streamlit/secrets.toml` file in the project root with:
           ```toml
           GEMINI_API_KEY = "your-api-key-here"
           ```
        2. Set the GEMINI_API_KEY environment variable
        """)
        return
    
    # Initialize session state for browser automation
    if "browser_history" not in st.session_state:
        st.session_state["browser_history"] = []
    
    # Task input
    task = st.text_input("Enter your browser automation task:", 
                        placeholder="e.g., Go to medium.com and search for articles about Python")
    
    max_steps = st.slider("Maximum steps:", min_value=1, max_value=10, value=3)
    
    if st.button("Run Automation"):
        if not task:
            st.warning("Please enter a task before running automation.")
            return
            
        with st.spinner("Running browser automation..."):
            try:
                # Create agent instance
                agent = BrowserUseAgent(
                    name="browser_automation",
                    credentials={
                        "GEMINI_API_KEY": api_key
                    },
                    general_prompt="You are a browser automation agent that helps users perform web-based tasks.",
                    data={
                        "task": task,
                        "max_steps": max_steps
                    }
                )
                
                # Run the automation
                result = asyncio.run(agent.run())
                
                # Store result in session state
                st.session_state["browser_history"].append({
                    "task": task,
                    "result": result
                })
                
                # Cleanup
                asyncio.run(agent.cleanup())
                
            except Exception as e:
                st.error(f"Error during automation: {str(e)}")
    
    # Display browser automation history
    if st.session_state["browser_history"]:
        for idx, history_item in enumerate(reversed(st.session_state["browser_history"])):
            with st.expander(f"Task: {history_item['task']}", expanded=(idx == 0)):
                result = history_item["result"]
                
                # Display final result
                st.subheader("Final Result")
                if result.success:
                    st.json(result.final_result)
                
                # Display errors if any
                if result.errors:
                    st.error("Errors encountered:")
                    for error in result.errors:
                        st.write(f"- {error}")
                
                # Display model actions and thoughts
                display_browser_actions(result.model_actions, result.model_thoughts)

if __name__ == "__main__":
    run_browser_automation()
