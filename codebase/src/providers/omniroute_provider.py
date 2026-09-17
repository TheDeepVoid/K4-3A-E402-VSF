"""OmniRoute Provider Implementation"""
import time
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI

from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig


class OmniRouteProvider(BaseAIProvider):
    """OmniRoute AI provider - multi-provider aggregation with fallback"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://api.omniroute.ai/v1",
            timeout=config.timeout
        )
        self._fallback_providers: List[BaseAIProvider] = []

    def add_fallback(self, provider: BaseAIProvider):
        """Add a fallback provider for when the primary fails"""
        self._fallback_providers.append(provider)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Generate chat completion with automatic fallback"""
        # Try primary provider first
        result = await self._primary_completion(messages, **kwargs)
        
        # If primary fails, try fallbacks
        if result.error and self._fallback_providers:
            for fallback in self._fallback_providers:
                result = await fallback.chat_completion(messages, **kwargs)
                if not result.error:
                    break
        
        return result

    async def _primary_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Primary provider completion"""
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
                provider="omniroute",
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=latency_ms
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model,
                provider="omniroute",
                error=str(e)
            )

    async def get_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """Get embeddings with fallback support"""
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
                provider="omniroute",
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=self.config.model,
                provider="omniroute",
                error=str(e)
            )

    async def close(self):
        """Close all providers"""
        await super().close()
        for provider in self._fallback_providers:
            await provider.close()