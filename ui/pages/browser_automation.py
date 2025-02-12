import streamlit as st
import os
import asyncio
from infrastructure.browser_use.main import BrowserUseAgent
from components.browser_component import display_browser_actions

async def run_browser_automation(agent):
    """Run browser automation asynchronously"""
    try:
        result = await agent.run()
        await agent.cleanup()
        return result
    except Exception as e:
        return {
            "success": False,
            "final_result": {},
            "errors": [str(e)],
            "model_actions": [],
            "model_thoughts": []
        }

def render():
    st.title("Browser Automation")
    
    # Get API key from environment or secrets
    api_key = os.getenv("GEMINI_API_KEY", st.secrets.get("GEMINI_API_KEY", ""))
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment or secrets")
        return
    
    # Input form
    with st.form("browser_automation_form"):
        task = st.text_area("Enter your task:", value="", height=100)
        max_steps = st.number_input("Maximum steps:", min_value=1, max_value=10, value=3)
        submitted = st.form_submit_button("Start Automation")
    
    if submitted and task:
        # Initialize agent
        credentials = {
            "GEMINI_API_KEY": api_key
        }
        
        data = {
            "task": task,
            "max_steps": max_steps
        }
        
        agent = BrowserUseAgent(
            name="browser_automation",
            credentials=credentials,
            general_prompt="You are a browser automation agent that helps users perform web-based tasks.",
            data=data
        )
        
        # Run automation with progress
        with st.spinner("Running browser automation..."):
            try:
                # Run the async function using asyncio
                result = asyncio.run(run_browser_automation(agent))
                
                # Display results using the browser component
                if result["success"]:
                    st.success("Browser automation completed successfully!")
                display_browser_actions(result)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    render()
