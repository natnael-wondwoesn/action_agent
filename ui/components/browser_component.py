import streamlit as st
from typing import Dict

def display_browser_actions(result: Dict):
    """Display browser automation actions and thoughts"""
    if not result:
        return
    
    # Display thoughts
    if result.get("model_thoughts"):
        st.subheader("Agent's Thoughts")
        for thought in result["model_thoughts"]:
            st.write(f"- {thought['thought']}")
    
    # Display actions
    if result.get("model_actions"):
        st.subheader("Actions Taken")
        for action in result["model_actions"]:
            st.write(f"- {action['action_type']}: {action['action_data']}")
    
    # Display final result
    if result.get("final_result"):
        st.subheader("Final Result")
        st.json(result["final_result"])
    
    # Display errors
    if not result.get("success", True) and result.get("errors"):
        st.error("Errors occurred:")
        for error in result["errors"]:
            st.error(error)
