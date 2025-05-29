"""Module for handling text translation."""
from typing import Optional
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

class Translator:
    """Handles translation of text between languages."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the translator with a specific model.
        
        Args:
            model_name: Name of the OpenAI model to use for translation.
        """
        self.model = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def translate_to_spanish(self, text: str) -> str:
        """Translate text to Spanish.
        
        Args:
            text: The text to translate.
            
        Returns:
            The translated text in Spanish.
        """
        system_prompt = (
            "You are a professional translator. Translate the following text to Spanish. "
            "Maintain the original tone, style, and meaning. Keep proper nouns, names, "
            "and technical terms in their original form if no common Spanish equivalent exists. "
            "Ensure the translation sounds natural and fluent in Spanish."
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text)
        ]
        
        response = await self.model.ainvoke(messages)
        return response.content

    def batch_translate(self, texts: list[str]) -> list[str]:
        """Translate a list of texts to Spanish.
        
        Args:
            texts: List of texts to translate.
            
        Returns:
            List of translated texts.
        """
        return [self.translate_to_spanish(text) for text in texts]
