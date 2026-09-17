from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


class AIResponse(BaseModel):
    """Base response model for AI providers"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""
    embeddings: List[List[float]]
    model: str
    provider: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class ProviderConfig(BaseModel):
    """Configuration for AI providers"""
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-5-nano"
    temperature: float = 0.7
    max_tokens: Optional[int] = 1000
    timeout: int = 30


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AIResponse:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    async def get_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """Get embeddings for texts"""
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _call_with_retry(self, func, *args, **kwargs):
        """Wrapper for retry logic"""
        return await func(*args, **kwargs)
    
    async def close(self):
        """Clean up resources"""
        if self._client:
            if hasattr(self._client, 'close'):
                await self._client.close()
            elif hasattr(self._client, '__aexit__'):
                await self._client.__aexit__(None, None, None)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model={self.config.model})"