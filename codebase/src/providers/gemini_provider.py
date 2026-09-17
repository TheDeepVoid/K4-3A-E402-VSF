"""Google Gemini Provider Implementation"""
import time
from typing import Dict, List, Any
import google.generativeai as genai

from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self._generation_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Generate chat completion using Gemini"""
        start_time = time.time()
        
        try:
            # Convert messages to Gemini format
            contents = self._convert_messages(messages)
            
            model = genai.GenerativeModel(
                model_name=kwargs.get("model", self.config.model),
                generation_config=self._generation_config
            )
            
            response = await model.generate_content_async(contents)
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=response.text or "",
                model=model.model_name,
                provider="gemini",
                latency_ms=latency_ms
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model,
                provider="gemini",
                error=str(e)
            )

    async def get_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """Get embeddings using Gemini's embedding models"""
        try:
            model = kwargs.get("model", "gemini-embedding-001")
            
            # Gemini embeddings are done one at a time
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=model,
                    content=text
                )
                embeddings.append(result["embedding"])
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                provider="gemini"
            )
        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=self.config.model,
                provider="gemini",
                error=str(e)
            )

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini format"""
        # Gemini uses a simpler format - just concatenate messages
        content = []
        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            content.append(f"{role}: {text}")
        return "\n".join(content)

    async def close(self):
        """Close resources (no-op for Gemini)"""
        pass