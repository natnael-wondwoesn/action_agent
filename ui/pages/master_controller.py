import streamlit as st
import os
import asyncio
from infrastructure.master_controller.main import MasterController, ActionResult
import time

def display_action_result(result: ActionResult):
    """Display the result of an action"""
    # Display the thinking process
    with st.expander("🤔 Thought Process", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Confidence", f"{result.confidence:.0%}")
            st.write(f"**Action Type:** {result.action_type}")
        with col2:
            st.write("**Reasoning:**")
            st.info(result.reasoning)
            st.write("**Enhanced Prompt:**")
            st.info(result.enhanced_prompt)
    
    # Display execution status
    if result.success:
        st.success("✅ Task completed successfully!")
    else:
        st.error("❌ Task failed!")
        
    # Display errors if any
    if result.errors:
        with st.expander("⚠️ Errors"):
            for error in result.errors:
                st.error(error)
    
    # Display execution details
    st.subheader("📝 Execution Details")
    
    # Display result based on action type
    if result.action_type == "browser_use":
        from components.browser_component import display_browser_actions
        display_browser_actions(result.result)
    elif result.action_type == "api_call":
        with st.expander("API Call Results"):
            st.json(result.result)
    else:
        with st.expander("Task Results"):
            st.json(result.result)

def render():
    # Page header with description
    st.title("🤖 AI Task Assistant")
    st.markdown("""
    I'm your AI assistant powered by Gemini Pro! I can help you with:
    - 🌐 Web browsing and automation
    - 🔄 API interactions
    - 💻 Local system tasks
    
    Just tell me what you need in natural language!
    """)
    
    # Get API key from environment or secrets
    api_key = os.getenv("GEMINI_API_KEY", st.secrets.get("GEMINI_API_KEY", ""))
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment or secrets")
        return
    
    # Input form with examples
    with st.form("task_form"):
        task = st.text_area(
            "What would you like me to do?",
            value="",
            height=100,
            help="""Examples:
            - "Search for recent news about artificial intelligence"
            - "Find Python programming tutorials on YouTube"
            - "Get the weather forecast for New York"
            """
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            max_retries = st.number_input("Max Retries", min_value=1, max_value=5, value=3)
        with col2:
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        with col3:
            submitted = st.form_submit_button("🚀 Start Task", use_container_width=True)
    
    if submitted and task:
        # Initialize controller with custom config
        credentials = {
            "GEMINI_API_KEY": api_key
        }
        
        config = {
            "max_retries": max_retries,
            "temperature": temperature
        }
        
        controller = MasterController(credentials=credentials, config=config)
        
        # Process request with progress
        with st.status("🔄 Processing your request...", expanded=True) as status:
            try:
                # Set up event loop for Windows
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                
                # Process the request
                status.update(label="🤔 Analyzing your request...")
                time.sleep(1)  # Give user time to see the status
                
                result = loop.run_until_complete(controller.process_request(task))
                
                status.update(label="✨ Task completed!")
                status.markdown(f"**Action chosen:** {result.action_type}")
                time.sleep(1)
                
                # Display results
                display_action_result(result)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                loop.close()
                status.update(label="Done!")

if __name__ == "__main__":
    render()
