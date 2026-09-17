#!/usr/bin/env python3
"""Demo script to showcase the AI pipeline - for live demos"""
import asyncio
import os
import sys
from pathlib import Path

# Add codebase to path
sys.path.insert(0, str(Path(__file__).parent))

from providers import OpenAIProvider, GeminiProvider, OpenRouterProvider
from providers.base import ProviderConfig
from config.system_prompt import SYSTEM_PROMPT


async def run_demo(provider_name: str = "openai", model: str = "gpt-3.5-turbo"):
    """Run a simple demo showing the AI pipeline"""
    
    print(f"\n{'='*60}")
    print(f"AI PIPELINE DEMO - {provider_name}/{model}")
    print(f"{'='*60}\n")
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY", "demo-key")
    
    config = ProviderConfig(
        api_key=api_key,
        model=model,
        temperature=0.7,
        max_tokens=200
    )
    
    # Select provider
    if provider_name == "openai":
        provider = OpenAIProvider(config)
    elif provider_name == "gemini":
        provider = GeminiProvider(config)
    elif provider_name == "openrouter":
        provider = OpenRouterProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    # Demo test
    demo_context = """The project started in January 2024 with a budget of $50,000.
The team consists of 5 developers and 2 designers. The deadline is December 2024."""
    
    demo_question = "When did the project start?"
    
    # Build messages
    formatted_prompt = SYSTEM_PROMPT.format(
        context=demo_context,
        question=demo_question
    )
    
    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": demo_question}
    ]
    
    print(f"Context: {demo_context}")
    print(f"Question: {demo_question}\n")
    print("Calling AI...")
    
    response = await provider.chat_completion(messages)
    
    print(f"\n{'='*60}")
    print("RESPONSE:")
    print(f"{'='*60}")
    print(response.content)
    print(f"\nModel: {response.model}")
    print(f"Provider: {response.provider}")
    print(f"Latency: {response.latency_ms:.0f}ms")
    
    if response.error:
        print(f"Error: {response.error}")
    
    await provider.close()
    
    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Pipeline Demo")
    parser.add_argument("--provider", default="openai", 
                       choices=["openai", "gemini", "openrouter"])
    parser.add_argument("--model", default="gpt-3.5-turbo")
    
    args = parser.parse_args()
    
    asyncio.run(run_demo(args.provider, args.model))