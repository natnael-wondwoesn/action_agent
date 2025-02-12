from typing import Dict, Optional, Type, Any
from pydantic import BaseModel, ValidationError
import inspect


class ActionAgent:
    """
    Base class for all LangChain Action Agents with dynamic schema and credential handling
    """

    input_schema: Type[BaseModel] = None  # To be overridden by subclasses
    output_schema: Type[BaseModel] = None  # To be overridden by subclasses
    required_credentials: list = []  # To be overridden by subclasses

    def __init__(
        self,
        name: str,
        credentials: Dict[str, str],
        general_prompt: str,
        timeout: int = 30,
        llm_config: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ):
        self.name = name
        self.credentials = credentials
        self.general_prompt = general_prompt
        self.timeout = timeout
        self.llm_config = llm_config or {}
        self.data = data or {}

        self._validate_credentials()
        self._validate_schemas()

    def _validate_credentials(self):
        """Validate required credentials using subclass requirements"""
        missing = [
            cred for cred in self.required_credentials if cred not in self.credentials
        ]
        if missing:
            raise ValueError(f"Missing required credentials: {missing}")

    def _validate_schemas(self):
        """Ensure subclasses define valid schemas"""
        if not self.input_schema or not issubclass(self.input_schema, BaseModel):
            raise ValueError("Invalid input schema defined")
        if not self.output_schema or not issubclass(self.output_schema, BaseModel):
            raise ValueError("Invalid output schema defined")

    def validate_input(self, input_data: Dict) -> BaseModel:
        """Validate input against class schema"""
        return self.input_schema(**input_data)

    def validate_output(self, output_data: Dict) -> BaseModel:
        """Validate output against class schema"""
        return self.output_schema(**output_data)

    async def run(self, *args, **kwargs):
        """To be implemented by subclasses"""
        raise NotImplementedError

    async def cleanup(self):
        """Optional cleanup logic"""
        pass
