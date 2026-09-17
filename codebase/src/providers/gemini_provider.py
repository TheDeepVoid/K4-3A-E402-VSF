"""Google Gemini Provider Implementation"""
import time
import asyncio
from typing import Dict, List, Any
from google import genai
from google.genai import types

from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = genai.Client(api_key=config.api_key)
        self._generation_config = types.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
        )

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

            model_name = kwargs.get("model", self.config.model)

            def _generate():
                return self._client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    generation_config=self._generation_config,
                )

            response = await asyncio.to_thread(_generate)

            latency_ms = (time.time() - start_time) * 1000

            return AIResponse(
                content=response.text or "",
                model=model_name,
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
        """Get embeddings for texts"""
        start_time = time.time()

        try:
            model_name = kwargs.get("model", self.config.model)
            # Use the embedding model
            def _embed():
                return self._client.models.embed_content(
                    model=model_name,
                    contents=texts,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )

            response = await asyncio.to_thread(_embed)

            latency_ms = (time.time() - start_time) * 1000

            return EmbeddingResponse(
                embeddings=[emb.values for emb in response.embeddings],
                model=model_name,
                provider="gemini",
                latency_ms=latency_ms
            )
        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=self.config.model,
                provider="gemini",
                error=str(e)
            )

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[types.Content]:
        """Convert OpenAI-style messages to Gemini contents"""
        contents = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            # Gemini uses 'user' and 'model' roles; map 'assistant' to 'model'
            if role == "assistant":
                role = "model"
            elif role not in ["user", "model"]:
                # Default to user for system or unknown roles
                role = "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=content)]))
        return contents