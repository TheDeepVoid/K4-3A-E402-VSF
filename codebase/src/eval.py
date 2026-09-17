"""Evaluation Script for AI Pipeline - Person 3 will use this"""
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# Add codebase/src and codebase to path
sys.path.insert(0, str(Path(__file__).parent))          # codebase/src
sys.path.insert(0, str(Path(__file__).parent.parent))   # codebase

from tests.test_cases import TEST_CASES, TestCase, TestCategory
from providers import OpenAIProvider, GeminiProvider, OpenRouterProvider, OmniRouteProvider
from providers.base import ProviderConfig, AIResponse
from prompting.prompts import SYSTEM_PROMPT


@dataclass
class TestResult:
    """Result of a single test case"""
    test_id: str
    category: str
    passed: bool
    actual_output: str
    expected_phrase: str
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    model: Optional[str] = None
    provider: Optional[str] = None


@dataclass
class EvaluationSummary:
    """Summary of evaluation run"""
    total_tests: int
    passed: int
    failed: int
    pass_rate: float
    by_category: Dict[str, Dict[str, int]]
    results: List[TestResult]
    timestamp: str
    model: str
    provider: str


class AIEvaluator:
    """Evaluate AI provider against test cases"""
    
    def __init__(self, provider, system_prompt: str = SYSTEM_PROMPT):
        self.provider = provider
        self.system_prompt = system_prompt
    
    def _build_messages(self, test_case: TestCase) -> List[Dict[str, str]]:
        """Build message list for the AI"""
        formatted_prompt = self.system_prompt.format(
            context=test_case.context,
            question=test_case.question
        )
        
        return [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": test_case.question}
        ]
    
    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            messages = self._build_messages(test_case)
            response: AIResponse = await self.provider.chat_completion(messages)
            
            latency_ms = (time.time() - start_time) * 1000
            
            passed = self._check_answer(
                response.content, 
                test_case.expected_answer,
                test_case.criteria
            )
            
            return TestResult(
                test_id=test_case.id,
                category=test_case.category.value,
                passed=passed,
                actual_output=response.content,
                expected_phrase=test_case.expected_answer,
                error=response.error,
                latency_ms=latency_ms,
                model=response.model,
                provider=response.provider
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_case.id,
                category=test_case.category.value,
                passed=False,
                actual_output="",
                expected_phrase=test_case.expected_answer,
                error=str(e)
            )
    
    def _check_answer(self, actual: str, expected: str, criteria: str) -> bool:
        """Check if the answer meets the criteria"""
        actual_lower = actual.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Handle "cannot determine" cases
        if expected_lower == "cannot determine":
            cannot_determine_phrases = [
                "cannot determine",
                "cannot be determined",
                "not specified",
                "not mentioned",
                "not provided",
                "no information",
                "không xác định",
                "không có thông tin"
            ]
            return any(phrase in actual_lower for phrase in cannot_determine_phrases)
        
        # Normal case: check if expected phrase is in actual
        return expected_lower in actual_lower
    
    async def run_all_tests(self, test_cases: List[TestCase] = None) -> EvaluationSummary:
        """Run all test cases"""
        test_cases = test_cases or TEST_CASES
        
        results: List[TestResult] = []
        
        for tc in test_cases:
            result = await self.run_single_test(tc)
            results.append(result)
            print(f"  {tc.id}: {'PASS' if result.passed else 'FAIL'}")
        
        # Calculate summary
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        
        # Group by category
        by_category: Dict[str, Dict[str, int]] = {}
        for tc in test_cases:
            cat = tc.category.value
            if cat not in by_category:
                by_category[cat] = {"passed": 0, "failed": 0}
            
            result = next(r for r in results if r.test_id == tc.id)
            if result.passed:
                by_category[cat]["passed"] += 1
            else:
                by_category[cat]["failed"] += 1
        
        model = results[0].model if results else "unknown"
        provider = results[0].provider if results else "unknown"
        
        return EvaluationSummary(
            total_tests=len(results),
            passed=passed,
            failed=failed,
            pass_rate=passed / len(results) if results else 0,
            by_category=by_category,
            results=results,
            timestamp=datetime.now().isoformat(),
            model=model,
            provider=provider
        )


def print_summary(summary: EvaluationSummary):
    """Print evaluation summary"""
    print("\n" + "=" * 60)
    print(f"EVALUATION SUMMARY - {summary.timestamp}")
    print("=" * 60)
    print(f"Provider: {summary.provider}")
    print(f"Model: {summary.model}")
    print(f"Total Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Pass Rate: {summary.pass_rate:.1%}")
    print("\nBy Category:")
    for cat, counts in summary.by_category.items():
        total = counts["passed"] + counts["failed"]
        rate = counts["passed"] / total if total > 0 else 0
        print(f"  {cat}: {counts['passed']}/{total} ({rate:.0%})")
    print("=" * 60)


async def run_evaluation(
    provider_type: str = "openai",
    model: str = "gpt-5-nano",
    api_key: str = None,
    base_url: str = None
) -> EvaluationSummary:
    """Run evaluation with specified provider"""
    
    import os
    api_key = api_key or os.getenv("OPENAI_API_KEY") or "dummy-key-for-testing"
    
    config = ProviderConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.3,
        max_tokens=500
    )
    
    if provider_type == "openai":
        provider = OpenAIProvider(config)
    elif provider_type == "gemini":
        provider = GeminiProvider(config)
    elif provider_type == "openrouter":
        provider = OpenRouterProvider(config)
    elif provider_type == "omniroute":
        provider = OmniRouteProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider_type}")
    
    print(f"\nRunning evaluation with {provider_type}/{model}")
    
    evaluator = AIEvaluator(provider)
    summary = await evaluator.run_all_tests()
    
    await provider.close()
    
    return summary


def save_results(summary: EvaluationSummary, output_path: str = "eval_results.json"):
    """Save results to JSON file"""
    data = {
        "total_tests": summary.total_tests,
        "passed": summary.passed,
        "failed": summary.failed,
        "pass_rate": summary.pass_rate,
        "by_category": summary.by_category,
        "timestamp": summary.timestamp,
        "model": summary.model,
        "provider": summary.provider,
        "results": [
            {
                "test_id": r.test_id,
                "category": r.category,
                "passed": r.passed,
                "actual_output": r.actual_output,
                "expected_phrase": r.expected_phrase,
                "error": r.error,
                "latency_ms": r.latency_ms
            }
            for r in summary.results
        ]
    }
    
    Path(output_path).write_text(json.dumps(data, indent=2))
    print(f"\nResults saved to {output_path}")


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate AI Pipeline")
    parser.add_argument("--provider", default="openai", choices=["openai", "gemini", "openrouter", "omniroute"])
    parser.add_argument("--model", default="gpt-5-nano")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--output", default="eval_results.json")
    
    args = parser.parse_args()
    
    summary = asyncio.run(run_evaluation(
        provider_type=args.provider,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url
    ))
    
    print_summary(summary)
    save_results(summary, args.output)