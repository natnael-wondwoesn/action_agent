import asyncio
from doctest import debug
import os
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
from pprint import pprint
from browser_use import Agent, Browser, BrowserConfig, AgentHistoryList

from infrastructure.action_agent.action_agent import ActionAgent

load_dotenv()

class BrowserUseInput(BaseModel):
    """Schema for browser use input parameters"""
    task: str
    chrome_path: Optional[str] = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    model_name: Optional[str] = "gemini-2.0-flash-exp"
    max_steps: Optional[int] = 3

class BrowserActionOutput(BaseModel):
    """Schema for browser action outputs"""
    action_type: str
    action_data: Dict[str, Any]
    timestamp: Optional[str]

class BrowserThought(BaseModel):
    """Schema for browser agent thoughts"""
    thought: str
    timestamp: Optional[str]

class BrowserUseOutput(BaseModel):
    """Schema for browser use output"""
    success: bool
    final_result: Dict[str, Any]
    errors: List[str]
    model_actions: List[BrowserActionOutput]
    model_thoughts: List[BrowserThought]

class BrowserUseAgent(ActionAgent):
    """Class for browser-based actions using browser-use library inheriting from ActionAgent."""
    
    input_schema = BrowserUseInput
    output_schema = BrowserUseOutput
    required_credentials = ["GEMINI_API_KEY"]

    def __init__(
        self,
        name: str,
        credentials: Dict[str, str],
        general_prompt: str,
        timeout: int = 30,
        llm_config: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ):
        super().__init__(
            name=name,
            credentials=credentials,
            general_prompt=general_prompt,
            timeout=timeout,
            llm_config=llm_config,
            data=data,
        )
        
        self.browser = None
        self.agent = None
        self._initialize_browser()

    def _initialize_browser(self):
        """Initialize browser session with configuration"""
        input_data = self.validate_input(self.data)
        
        self.config = BrowserConfig(
            headless=True,
            chrome_instance_path=input_data.chrome_path
        )
        self.browser = Browser(config=self.config)

        self.llm = ChatGoogleGenerativeAI(
            model=input_data.model_name,
            api_key=SecretStr(self.credentials["GEMINI_API_KEY"]),
        )

        self.agent = Agent(
            task=input_data.task,
            llm=self.llm,
            browser=self.browser
        )

    async def run(self, *args, **kwargs) -> Dict:
        """Execute the browser automation task"""
        try:
            input_data = self.validate_input(self.data)
            history: AgentHistoryList = await self.agent.run(max_steps=input_data.max_steps)
            # print(history)
            
            # Return raw output without validation
            return {
                "success": True,
                "final_result": history.final_result(),  # Return as is
                "errors": history.errors(),
                "model_actions": [
                    {
                        "action_type": action.get("type", "unknown"),
                        "action_data": action,
                        "timestamp": action.get("timestamp")
                    }
                    for action in (history.model_actions() or [])
                ],
                "model_thoughts": [
                    {
                        "thought": thought,
                        "timestamp": None
                    }
                    for thought in (history.model_thoughts() or [])
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "final_result": str(e),  # Return error message directly
                "errors": [str(e)],
                "model_actions": [],
                "model_thoughts": []
            }

    async def cleanup(self):
        """Cleanup browser session"""
        if self.browser:
            await self.browser.close()


# Example usage
if __name__ == "__main__":
    credentials = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    }
    
    task_data = {
        "task": "Go to medium.com and try to sign in using the available gmail profile account to sign in and search for articles that explain how to learn cybersecurity",
        "max_steps": 3
    }
    
    agent = BrowserUseAgent(
        name="browser_automation",
        credentials=credentials,
        general_prompt="You are a browser automation agent that helps users perform web-based tasks.",
        data=task_data
    )
    
    result = asyncio.run(agent.run(debug=True))
    print(result)
    asyncio.run(agent.cleanup())
