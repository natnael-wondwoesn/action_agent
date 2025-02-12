import os
import requests
from typing import Dict, Optional, Any,Union
from pydantic import BaseModel, SecretStr
from infrastructure.action_agent.action_agent import ActionAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import asyncio
class APIAgentInput(BaseModel):
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

class APIAgentOutput(BaseModel):
    status: int
    message: str
    data: Optional[Union[Dict[str, Any], list]]

class APIAgent(ActionAgent):
    input_schema = APIAgentInput
    output_schema = APIAgentOutput
    required_credentials = ["api_key"]

    def __init__(self, name: str, credentials: Dict[str, str], general_prompt: str, timeout: int = 30, llm_config: Optional[Dict] = None, data: Optional[Dict] = None):
        super().__init__(name, credentials, general_prompt, timeout, llm_config, data)
    
    def _send_request(self, input_data: APIAgentInput) -> requests.Response:
        headers = input_data.headers or {}
        if 'Authorization' not in headers and 'bearer_token' in self.credentials:
            headers['Authorization'] = f"Bearer {self.credentials['bearer_token']}"
        elif 'api_key' in self.credentials:
            headers['X-API-KEY'] = self.credentials['api_key']
        headers.setdefault('Content-Type', 'application/json')
        
        return requests.request(method=input_data.method.upper(), url=input_data.url, headers=headers, params=input_data.params, json=input_data.data, timeout=self.timeout)
    
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        input_data = self.validate_input(self.data)
        try:
            response = self._send_request(input_data)
            response.raise_for_status()
            return self.validate_output({
                "status": response.status_code,
                "message": "Success",
                "data": response.json()
            }).dict()
        except requests.RequestException as e:
            return self.validate_output({
                "status": response.status_code if response else 500,
                "message": str(e),
                "data": None
            }).dict()

    async def cleanup(self):
        print(f"Cleaning up API Agent: {self.name}")


class LLMAgentInput(BaseModel):
    prompt: str

class LLMAgentOutput(BaseModel):
    status: int
    message: str
    data: Optional[str]

class LLMAgent(ActionAgent):
    input_schema = LLMAgentInput
    output_schema = LLMAgentOutput
    required_credentials = ["api_key"]

    def __init__(self, name: str, credentials: Dict[str, str], general_prompt: str, model: str , model_type: str, timeout: int = 30, llm_config: Optional[Dict] = None, data: Optional[Dict] = None):
        super().__init__(name, credentials, general_prompt, timeout, llm_config, data)
        self.model = model
        self.model_type = model_type
        self.api_key = credentials.get("api_key", "")
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        if self.model == "Gemini":
            if not self.api_key:
                self.api_key = os.getenv("GEMINI_API_KEY")
            self.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(self.api_key))
        elif self.model == "OpenAI":
            if not self.api_key:
                self.api_key = os.getenv(" OPENAI_API_KEY")
                # print(f"\n\n\n {self.api_key} \n\n\n")
            self.llm = ChatOpenAI(model="gpt-4omini", api_key=self.api_key)
        else:
            raise ValueError("Unsupported model. Choose OpenAI, Anthropic, or Gemini.")
    
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        input_data = self.validate_input(self.data)
        try:
            response = self.llm.invoke(input_data.prompt)
            response_content = response.content if isinstance(response.content, str) else response.content.decode('utf-8')
            print(f"response: {response_content}")
            
            return self.validate_output({
                "status": 200,
                "message": "Success",
                "data": response_content
            }).dict()
        except Exception as e:
            return self.validate_output({
                "status": 500,
                "message": str(e),
                "data": None
            }).dict()
    
    async def cleanup(self):
        print(f"Cleaning up LLM Agent: {self.name}")



def test_api_agent():
    credentials = {"api_key": "test_api_key"}
    data = {
        "url": "https://jsonplaceholder.typicode.com/posts/3",
        "method": "GET"
    }
    
    agent = APIAgent(
        name="test_api_agent",
        credentials=credentials,
        general_prompt="Test API Agent",
        data=data
    )

    result = asyncio.run(agent.run())
    print("API Agent Test Result:", result)
    asyncio.run(agent.cleanup())


def test_llm_agent():
    credentials = {"api_key": "AIzaSyB5HvN_XTYClEsJhOdFDzoiUuBov8Ttx9k"}
    data = {
        "prompt": "What is the capital of France?"
    }
    
    agent = LLMAgent(
        name="test_llm_agent",
        credentials=credentials,
        general_prompt="Test LLM Agent",
        model="Gemini",
        data=data
    )
    # print(f"\n\n\n {agent.api_key} \n\n\n")
    result = asyncio.run(agent.run())
    print("LLM Agent Test Result:", result)
    asyncio.run(agent.cleanup())


test_api_agent()
# test_llm_agent()