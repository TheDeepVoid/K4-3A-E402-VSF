"""OpenRouter Provider Implementation"""
import time
from typing import Dict, List, Any
from openai import AsyncOpenAI

from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter AI provider - unified API for multiple models"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # OpenRouter uses a specific base URL
        base_url = config.base_url or "https://openrouter.ai/api/v1"
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            timeout=config.timeout,
            default_headers={
                "HTTP-Referer": "https://github.com/ai-pipeline",
                "X-Title": "AI Pipeline"
            }
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Generate chat completion using OpenRouter"""
        start_time = time.time()
        
        try:
            # Map model names to OpenRouter format if needed
            model = kwargs.get("model", self.config.model)
            
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                provider="openrouter",
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=latency_ms
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model,
                provider="openrouter",
                error=str(e)
            )

    async def get_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """Get embeddings using OpenRouter"""
        try:
            # OpenRouter may not support all embedding models
            # Fallback to a supported model or raise error
            model = kwargs.get("model", "text-embedding-3-small")
            
            response = await self._client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                provider="openrouter",
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=self.config.model,
                provider="openrouter",
                error=str(e)
            )

    async def close(self):
        """Close the OpenRouter client"""
        await super().close()