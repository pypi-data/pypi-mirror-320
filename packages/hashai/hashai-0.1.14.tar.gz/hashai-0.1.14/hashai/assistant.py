from typing import Optional, List, Dict, Union, Iterator, Any
from pydantic import BaseModel, Field, ConfigDict
from PIL.Image import Image
import requests
import re
import io
import json
from .rag import RAG
from .llm.base_llm import BaseLLM
from .knowledge_base.retriever import Retriever
from .knowledge_base.vector_store import VectorStore

class Assistant(BaseModel):
    # -*- Agent settings
    name: Optional[str] = Field(None, description="Name of the assistant.")
    description: Optional[str] = Field(None, description="Description of the assistant's role.")
    instructions: Optional[List[str]] = Field(None, description="List of instructions for the assistant.")
    model: Optional[str] = Field(None, description="The LLM model to use (e.g., Groq, OpenAI).")
    show_tool_calls: bool = Field(False, description="Whether to show tool calls in the response.")
    markdown: bool = Field(False, description="Whether to format the response in markdown.")
    tools: Optional[List[Union[str, Dict]]] = Field(None, description="List of tools available to the assistant.")
    user_name: Optional[str] = Field("User", description="Name of the user interacting with the assistant.")
    emoji: Optional[str] = Field(":robot:", description="Emoji to represent the assistant in the CLI.")
    rag: Optional[RAG] = Field(None, description="RAG instance for context retrieval.")
    knowledge_base: Optional[Dict] = Field(None, description="Knowledge base for domain-specific information.")
    llm: Optional[BaseLLM] = Field(None, description="The LLM instance to use.")
    json_output: bool = Field(False, description="Whether to format the response as JSON.")
    api: bool = Field(False, description="Whether to generate an API for the assistant.")
    api_config: Optional[Dict] = Field(
        None,
        description="Configuration for the API (e.g., host, port, authentication).",
    )
    api_generator: Optional[Any] = Field(None, description="The API generator instance.")
    expected_output: Optional[Union[str, Dict]] = Field(None, description="The expected format or structure of the output.")

    # Allow arbitrary types
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize the model and tools here if needed
        self._initialize_model()
        # Initialize RAG if not provided
        if self.rag is None:
            self.rag = self._initialize_default_rag()
        # Automatically generate API if api=True
        if self.api:
            self._generate_api()

    def _initialize_model(self):
        """Initialize the model based on the provided configuration."""
        if self.llm is not None:
            return  # LLM is already initialized, do nothing
        if self.model is None:
            raise ValueError("Model must be specified.")
        if self.model.lower() == "groq":
            from .llm.groq import GroqLlm
            self.llm = GroqLlm(api_key=self.llm.api_key if self.llm else None)
        elif self.model.lower() == "openai":
            from .llm.openai import OpenAILlm
            self.llm = OpenAILlm()
        elif self.model.lower() == "anthropic":
            from .llm.anthropic import AnthropicLlm
            self.llm = AnthropicLlm()
        else:
            raise ValueError(f"Unsupported model: {self.model}")

    def _initialize_default_rag(self) -> RAG:
        """Initialize a default RAG instance with a dummy vector store."""
        vector_store = VectorStore()
        retriever = Retriever(vector_store)
        return RAG(retriever)

    def load_image_from_url(self, image_url: str) -> Image:
        """Load an image from a URL and return it as a PIL Image."""
        response = requests.get(image_url)
        image_bytes = response.content
        return Image.open(io.BytesIO(image_bytes))

    def print_response(
        self,
        message: Optional[Union[str, Image, List, Dict]] = None,
        stream: bool = False,
        markdown: bool = False,
        **kwargs,
    ) -> Union[str, Dict]:  # Add return type hint
        """Print the assistant's response to the console and return it."""
        if isinstance(message, Image):
            # Handle image input
            message = self._process_image(message)

        if stream:
            # Handle streaming response
            response = ""
            for chunk in self._stream_response(message, markdown=markdown, **kwargs):
                print(chunk)
                response += chunk
            return response
        else:
             # Generate and return the response
            response = self._generate_response(message, markdown=markdown, **kwargs)
            print(response)  # Print the response to the console
            return response

    def _process_image(self, image: Image) -> str:
        """Process the image and return a string representation."""
        # Convert the image to text or extract relevant information
        # For now, we'll just return a placeholder string
        return "Image processed. Extracted text: [Placeholder]"

    def _stream_response(self, message: str, markdown: bool = False, **kwargs) -> Iterator[str]:
        """Stream the assistant's response."""
        # Simulate streaming by yielding chunks of the response
        response = self._generate_response(message, markdown=markdown, **kwargs)
        for chunk in response.split():
            yield chunk + " "

    def _generate_response(self, message: str, markdown: bool = False, **kwargs) -> str:
        """Generate the assistant's response."""
        # Retrieve relevant context using RAG
        context = self.rag.retrieve(message) if self.rag else None

        # Prepare the prompt with instructions, description, and context
        prompt = self._build_prompt(message, context)

        # Generate the response using the LLM
        response = self.llm.generate(prompt=prompt, context=context, **kwargs)

        # Format the response based on the json_output flag
        if self.json_output:
            response = self._format_response_as_json(response)

        # Validate the response against the expected_output
        if self.expected_output:
            response = self._validate_response(response)

        if markdown:
            return f"**Response:**\n\n{response}"
        return response

    def _build_prompt(self, message: str, context: Optional[List[Dict]]) -> str:
        """Build the prompt using instructions, description, and context."""
        prompt_parts = []

        # Add description if available
        if self.description:
            prompt_parts.append(f"Description: {self.description}")

        # Add instructions if available
        if self.instructions:
            instructions = "\n".join(self.instructions)
            prompt_parts.append(f"Instructions: {instructions}")

        # Add context if available
        if context:
            prompt_parts.append(f"Context: {context}")

        # Add the user's message
        prompt_parts.append(f"User Input: {message}")

        return "\n\n".join(prompt_parts)

    def _format_response_as_json(self, response: str) -> Union[Dict, str]:
        """Format the response as JSON if json_output is True."""
        try:
            # Use regex to extract JSON from the response (e.g., within ```json ``` blocks)
            json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
            if json_match:
                # Extract the JSON part and parse it
                json_str = json_match.group(1)
                return json.loads(json_str)  # Return the parsed JSON object (a dictionary)
            else:
                # If no JSON block is found, try to parse the entire response as JSON
                return json.loads(response)  # Return the parsed JSON object (a dictionary)
        except json.JSONDecodeError:
            # If the response is not valid JSON, wrap it in a dictionary
            return {"response": response}  # Return a dictionary with the response as a string

    def _validate_response(self, response: Union[str, Dict]) -> Union[str, Dict]:
        """Validate the response against the expected_output format."""
        if isinstance(self.expected_output, dict):
            if not isinstance(response, dict):
                raise ValueError("Expected output is a dictionary, but the response is not.")
            for key, value in self.expected_output.items():
                if key not in response:
                    raise ValueError(f"Expected key '{key}' not found in the response.")
                if isinstance(value, dict) and isinstance(response[key], dict):
                    self._validate_response(response[key])
                elif isinstance(value, type) and not isinstance(response[key], value):
                    raise ValueError(f"Expected type '{value}' for key '{key}', but got '{type(response[key])}'.")
        elif isinstance(self.expected_output, str):
            if not isinstance(response, str):
                raise ValueError("Expected output is a string, but the response is not.")
        return response

    def cli_app(
        self,
        message: Optional[str] = None,
        exit_on: Optional[List[str]] = None,
        **kwargs,
    ):
        """Run the assistant in a CLI app."""
        from rich.prompt import Prompt

        if message:
            self.print_response(message=message, **kwargs)

        _exit_on = exit_on or ["exit", "quit", "bye"]
        while True:
            message = Prompt.ask(f"[bold] {self.emoji} {self.user_name} [/bold]")
            if message in _exit_on:
                break

            self.print_response(message=message, **kwargs)

    def _generate_api(self):
        """Generate an API for the assistant if api=True."""
        from .api.api_generator import APIGenerator
        self.api_generator = APIGenerator(self)
        print(f"API generated for assistant '{self.name}'. Use `.run_api()` to start the API server.")

    def run_api(self):
        """Run the API server for the assistant."""
        if not hasattr(self, 'api_generator'):
            raise ValueError("API is not enabled for this assistant. Set `api=True` when initializing the assistant.")
    
        # Get API configuration
        host = self.api_config.get("host", "0.0.0.0") if self.api_config else "0.0.0.0"
        port = self.api_config.get("port", 8000) if self.api_config else 8000

        # Run the API server
        self.api_generator.run(host=host, port=port)