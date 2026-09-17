"""Test Cases - load from MD file"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from pathlib import Path
import re

TEST_CASES_PATH = Path(__file__).parent / "fixtures" / "test_cases_template.md"


class TestCategory(Enum):
    """Categories of test cases"""
    NORMAL = "normal"
    MISSING_INFO = "missing"
    NO_ANSWER = "no_answer"
    DIFFICULT = "difficult"
    EDGE_CASE = "edge_case"


@dataclass
class TestCase:
    """Single test case definition"""
    id: str
    category: TestCategory
    context: str
    question: str
    expected_answer: str
    criteria: str
    tags: List[str]


def load_test_cases() -> List[TestCase]:
    """Load test cases from MD file"""
    content = TEST_CASES_PATH.read_text()
    test_cases = []
    
    # Parse MD sections
    sections = re.split(r'\n##\s+', content)
    
    category_map = {
        "Normal Cases": TestCategory.NORMAL,
        "Missing Info Cases": TestCategory.MISSING_INFO,
        "No Answer Cases": TestCategory.NO_ANSWER,
        "Difficult Cases": TestCategory.DIFFICULT,
        "Edge Cases": TestCategory.EDGE_CASE,
    }
    
    current_category = None
    
    for section in sections:
        lines = section.split('\n')
        if not lines:
            continue
            
        # Check if this is a category header
        for cat_name, cat_enum in category_map.items():
            if lines[0].strip() == cat_name:
                current_category = cat_enum
                lines = lines[1:]
                break
        
        if current_category is None:
            continue
            
        # Parse test cases in this section
        current_test = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('### '):
                # New test case
                if current_test:
                    test_cases.append(_create_test_case(current_test, current_category))
                current_test = {"id": line.replace('### ', '').strip()}
                
            elif line.startswith('- **Context**:'):
                current_test["context"] = line.replace('- **Context**:', '').strip()
            elif line.startswith('- **Question**:'):
                current_test["question"] = line.replace('- **Question**:', '').strip()
            elif line.startswith('- **Expected**:'):
                current_test["expected"] = line.replace('- **Expected**:', '').strip()
            elif line.startswith('- **Criteria**:'):
                current_test["criteria"] = line.replace('- **Criteria**:', '').strip()
            elif line.startswith('- **Tags**:'):
                current_test["tags"] = [t.strip() for t in line.replace('- **Tags**:', '').split(',')]
        
        # Add last test case
        if current_test:
            test_cases.append(_create_test_case(current_test, current_category))
    
    return test_cases


def _create_test_case(data: dict, category: TestCategory) -> TestCase:
    return TestCase(
        id=data["id"],
        category=category,
        context=data.get("context", ""),
        question=data.get("question", ""),
        expected_answer=data.get("expected", ""),
        criteria=data.get("criteria", ""),
        tags=data.get("tags", [])
    )


# Load test cases
TEST_CASES = load_test_cases()

__all__ = ["TestCase", "TestCategory", "TEST_CASES"]