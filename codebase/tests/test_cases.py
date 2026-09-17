"""Test Case Definitions for AI Pipeline"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class TestCategory(Enum):
    """Categories of test cases"""
    NORMAL = "normal"           # Standard question with clear answer
    MISSING_INFO = "missing"    # Question missing required context
    NO_ANSWER = "no_answer"     # Question with no answer in context
    DIFFICULT = "difficult"     # Edge cases, ambiguous questions
    EDGE_CASE = "edge_case"     # Boundary conditions


@dataclass
class TestCase:
    """Single test case definition"""
    id: str
    category: TestCategory
    context: str
    question: str
    expected_answer: str  # Key phrase or pattern that should be in answer
    criteria: str         # PASS/FAIL criteria description
    tags: List[str]       # Additional tags for filtering
    
    def __post_init__(self):
        if isinstance(self.category, str):
            self.category = TestCategory(self.category)


# Test cases for Person 3 to use (12-15 cases)
TEST_CASES: List[TestCase] = [
    # === NORMAL CASES (4) ===
    TestCase(
        id="norm_001",
        category=TestCategory.NORMAL,
        context="The project started in 2024 with a budget of $50,000. "
                "The team consists of 5 developers and 2 designers.",
        question="When did the project start?",
        expected_answer="2024",
        criteria="Answer contains '2024'",
        tags=["date", "basic"]
    ),
    TestCase(
        id="norm_002",
        category=TestCategory.NORMAL,
        context="Python was created by Guido van Rossum in 1991. "
                "JavaScript was created by Brendan Eich in 1995.",
        question="Who created Python?",
        expected_answer="Guido van Rossum",
        criteria="Answer contains 'Guido van Rossum'",
        tags=["person", "basic"]
    ),
    TestCase(
        id="norm_003",
        category=TestCategory.NORMAL,
        context="The app supports three payment methods: credit card, PayPal, and bank transfer. "
                "Processing time is 2-3 business days.",
        question="What payment methods are supported?",
        expected_answer="credit card, PayPal, bank transfer",
        criteria="Answer lists all three payment methods",
        tags=["list", "feature"]
    ),
    TestCase(
        id="norm_004",
        category=TestCategory.NORMAL,
        context="The temperature today is 72°F with humidity at 65%. "
                "Wind speed is 10 mph from the northwest.",
        question="What is the current temperature?",
        expected_answer="72",
        criteria="Answer contains '72' (Fahrenheit)",
        tags=["number", "weather"]
    ),
    
    # === MISSING INFO CASES (3) ===
    TestCase(
        id="miss_001",
        category=TestCategory.MISSING_INFO,
        context="The meeting is scheduled for next Tuesday.",
        question="What time is the meeting?",
        expected_answer="cannot determine",
        criteria="Answer indicates inability to determine (not hallucinated time)",
        tags=["missing", "time"]
    ),
    TestCase(
        id="miss_002",
        category=TestCategory.MISSING_INFO,
        context="The product costs $99.",
        question="What is the shipping cost?",
        expected_answer="cannot determine",
        criteria="Answer indicates shipping cost is not in context",
        tags=["missing", "price"]
    ),
    TestCase(
        id="miss_003",
        category=TestCategory.MISSING_INFO,
        context="User satisfaction rating is 4.5 out of 5.",
        question="How many users were surveyed?",
        expected_answer="cannot determine",
        criteria="Answer does not hallucinate a number",
        tags=["missing", "count"]
    ),
    
    # === NO ANSWER CASES (3) ===
    TestCase(
        id="noans_001",
        category=TestCategory.NO_ANSWER,
        context="The company was founded in 2010. "
                "Revenue has grown consistently over 5 years.",
        question="What is the stock price?",
        expected_answer="cannot determine",
        criteria="Answer says cannot determine (not hallucinated)",
        tags=["missing", "financial"]
    ),
    TestCase(
        id="noans_002",
        category=TestCategory.NO_ANSWER,
        context="The database contains 1 million records. "
                "Backup frequency is daily at midnight.",
        question="Who is the CEO?",
        expected_answer="cannot determine",
        criteria="Answer indicates CEO not in context",
        tags=["missing", "person"]
    ),
    TestCase(
        id="noans_003",
        category=TestCategory.NO_ANSWER,
        context="The algorithm has O(n log n) time complexity.",
        question="What is the memory usage?",
        expected_answer="cannot determine",
        criteria="Answer does not make up memory usage",
        tags=["missing", "technical"]
    ),
    
    # === DIFFICULT CASES (3) ===
    TestCase(
        id="diff_001",
        category=TestCategory.DIFFICULT,
        context="The project timeline shows: Phase 1 (Jan-Mar), Phase 2 (Apr-Jun), "
                "Phase 3 (Jul-Sep). Phase 2 had a 2-week delay.",
        question="When did Phase 3 start?",
        expected_answer="July",
        criteria="Answer correctly calculates: starts mid-July despite delay",
        tags=["date", "calculation"]
    ),
    TestCase(
        id="diff_002",
        category=TestCategory.DIFFICULT,
        context="The discount structure is: 10% for orders over $100, "
                "15% for orders over $500, 20% for orders over $1000. "
                "Customer has $1200 order but used a $200 coupon.",
        question="What discount applies?",
        expected_answer="20% or 1000",
        criteria="Handles coupon interaction correctly or asks for clarification",
        tags=["logic", "edge"]
    ),
    TestCase(
        id="diff_003",
        category=TestCategory.DIFFICULT,
        context="Version 2.0 was released in March. Version 2.1 in May. "
                "Version 3.0 in August. Bug reports: v2.0 (50), v2.1 (30), v3.0 (80).",
        question="Which version has the most bugs?",
        expected_answer="3.0",
        criteria="Correctly identifies v3.0 despite being newest",
        tags=["analysis", "comparison"]
    ),
    
    # === EDGE CASES (2) ===
    TestCase(
        id="edge_001",
        category=TestCategory.EDGE_CASE,
        context="",
        question="What is the capital of France?",
        expected_answer="cannot determine",
        criteria="Handles empty context gracefully",
        tags=["empty", "boundary"]
    ),
    TestCase(
        id="edge_002",
        category=TestCategory.EDGE_CASE,
        context="The answer is42.",
        question="What is the answer?",
        expected_answer="42",
        criteria="Handles unusual formatting (no space after 'is')",
        tags=["format", "parsing"]
    ),
]

# Export for easy access
__all__ = ["TestCase", "TestCategory", "TEST_CASES"]