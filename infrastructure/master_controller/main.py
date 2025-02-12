import os
from typing import Dict, Optional, List, Any, Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from infrastructure.browser_use.main import BrowserUseAgent
import json
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

load_dotenv()

class ActionType(BaseModel):
    """Schema for action type determination"""
    type: Literal["browser_use", "api_call", "local_function"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    enhanced_prompt: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ActionResult(BaseModel):
    """Schema for action execution result"""
    success: bool
    result: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)
    action_type: str
    confidence: float
    reasoning: str
    enhanced_prompt: str
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class MasterControllerConfig(BaseModel):
    """Configuration for the master controller"""
    model_name: str = "gemini-1.0-pro"
    max_retries: int = 3
    initial_wait: float = 1.0
    max_wait: float = 10.0
    temperature: float = 0.7
    action_selection_prompt: str = """
    You are a master controller that determines the best way to handle user requests.
    Your role is to:
    1. Understand the user's intent
    2. Enhance the prompt with necessary details
    3. Choose the most appropriate action type
    
    Available actions:
    1. Browser automation (browser_use):
       - For tasks requiring web interaction
       - Examples: web search, scraping, form filling
       
    2. API calls (api_call):
       - For tasks that can be done via direct API access
       - Examples: weather data, stock prices, translations
       
    3. Local functions (local_function):
       - For tasks that can be done locally
       - Examples: file operations, calculations, text processing
    
    User request: {user_prompt}

    Think through this step by step:
    1. What is the user trying to achieve?
    2. What additional context or parameters would help?
    3. Which action type would be most efficient?
    4. How confident are you in this choice?

    Respond in the following JSON format:
    {
        "type": "browser_use|api_call|local_function",
        "confidence": 0.0-1.0,
        "reasoning": "Detailed step-by-step explanation of your thought process and why this action type was chosen",
        "enhanced_prompt": "An enhanced version of the user's prompt with additional context, parameters, and specific instructions"
    }
    """

class MasterController:
    """Master controller for routing and enhancing user requests"""
    
    def __init__(
        self,
        credentials: Dict[str, str],
        config: Optional[Dict] = None
    ):
        self.credentials = credentials
        self.config = MasterControllerConfig(**(config or {}))
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the LLM with retry logic"""
        @retry(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=self.config.initial_wait,
                max=self.config.max_wait
            ),
            reraise=True
        )
        def create_llm():
            return ChatGoogleGenerativeAI(
                model=self.config.model_name,
                api_key=self.credentials["GEMINI_API_KEY"],
                temperature=self.config.temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        
        try:
            return create_llm()
        except tenacity.RetryError as e:
            raise Exception(f"Failed to initialize LLM after {self.config.max_retries} retries: {str(e)}")

    async def determine_action(self, user_prompt: str) -> ActionType:
        """Determine the best action type for the user's prompt"""
        try:
            # Format the prompt with the user's request
            formatted_prompt = self.config.action_selection_prompt.format(
                user_prompt=user_prompt
            )
            
            # Get LLM response
            response = await self.llm.agenerate([formatted_prompt])
            response_text = response.generations[0][0].text
            
            # Parse JSON response
            try:
                action_data = json.loads(response_text)
                return ActionType(**action_data)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse LLM response as JSON")
            
        except Exception as e:
            raise Exception(f"Failed to determine action: {str(e)}")

    async def execute_action(self, action: ActionType) -> ActionResult:
        """Execute the determined action"""
        start_time = datetime.now()
        try:
            if action.type == "browser_use":
                # Execute browser automation
                agent = BrowserUseAgent(
                    name="browser_automation",
                    credentials=self.credentials,
                    general_prompt="You are a browser automation agent that helps users perform web-based tasks.",
                    data={
                        "task": action.enhanced_prompt,
                        "max_steps": 3
                    }
                )
                result = await agent.run()
                await agent.cleanup()
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return ActionResult(
                    success=result["success"],
                    result=result,
                    action_type="browser_use",
                    confidence=action.confidence,
                    reasoning=action.reasoning,
                    enhanced_prompt=action.enhanced_prompt,
                    execution_time=execution_time
                )
                
            elif action.type == "api_call":
                # TODO: Implement API call handling
                raise NotImplementedError("API call handling not implemented yet")
                
            elif action.type == "local_function":
                # TODO: Implement local function handling
                raise NotImplementedError("Local function handling not implemented yet")
                
            else:
                raise ValueError(f"Unknown action type: {action.type}")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ActionResult(
                success=False,
                result={},
                errors=[str(e)],
                action_type=action.type,
                confidence=action.confidence,
                reasoning=action.reasoning,
                enhanced_prompt=action.enhanced_prompt,
                execution_time=execution_time
            )

    async def process_request(self, user_prompt: str) -> ActionResult:
        """Process a user request from start to finish"""
        try:
            # Determine the best action
            action = await self.determine_action(user_prompt)
            
            # Execute the action
            result = await self.execute_action(action)
            
            return result
            
        except Exception as e:
            return ActionResult(
                success=False,
                result={},
                errors=[str(e)],
                action_type="unknown",
                confidence=0.0,
                reasoning="Failed to process request",
                enhanced_prompt=user_prompt,
                execution_time=0.0
            )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        credentials = {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
        }
        
        controller = MasterController(credentials=credentials)
        result = await controller.process_request(
            "Go to Google and search for 'Python programming tutorials'"
        )
        print(result)
    
    asyncio.run(main())
