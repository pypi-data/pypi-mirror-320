from typing import List, Dict, Optional
from .base_llm import BaseLLM
import openai

class OpenAILlm(BaseLLM):
    def __init__(self, model: str = "gpt-4", api_key: str = None):
        self.model = model
        self.api_key = api_key
        openai.api_key = api_key

    def generate(self, prompt: str, context: Optional[List[Dict]] = None, memory: Optional[List[Dict]] = None) -> str:
        messages = []
        if memory:
            messages.extend(memory)
        if context:
            messages.append({"role": "system", "content": "Context: " + str(context)})
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message["content"]