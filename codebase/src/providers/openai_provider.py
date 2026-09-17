"""OpenAI Provider Implementation"""
import time
from typing import Dict, List, Any
from openai import AsyncOpenAI

from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig


class OpenAIProvider(BaseAIProvider):
    """OpenAI AI provider using the OpenAI API"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,  # For proxy/custom endpoints
            timeout=config.timeout
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Generate chat completion using OpenAI"""
        start_time = time.time()
        
        try:
            response = await self._client.chat.completions.create(
                model=kwargs.get("model", self.config.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=latency_ms
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model,
                provider="openai",
                error=str(e)
            )

    async def get_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """Get embeddings using OpenAI's embedding models"""
        try:
            model = kwargs.get("model", "text-embedding-3-small")
            
            response = await self._client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=self.config.model,
                provider="openai",
                error=str(e)
            )

    async def close(self):
        """Close the OpenAI client"""
        await super().close()