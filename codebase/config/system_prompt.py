"""System Prompt Configuration - loads from MD file"""
from pathlib import Path

# Load from MD file
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "docs" / "system_prompt.md"

def load_system_prompt() -> str:
    """Load the default system prompt from MD file"""
    content = SYSTEM_PROMPT_PATH.read_text()
    # Extract the default prompt between the first ``` fences
    lines = content.split('\n')
    in_code_block = False
    prompt_lines = []
    
    for line in lines:
        if line.strip() == '```':
            if in_code_block:
                break  # End of default prompt
            else:
                in_code_block = True
                continue
        if in_code_block and line.strip():
            prompt_lines.append(line)
    
    return '\n'.join(prompt_lines)

SYSTEM_PROMPT = load_system_prompt()

# Prompt variants (can also be loaded from MD)
PROMPT_VARIANTS = {
    "strict": """You must answer ONLY based on the provided context. 
If the answer is not explicitly stated, respond with: "I cannot determine the answer from the provided context."
Do not make assumptions or infer information not directly stated.""",
    
    "flexible": """You may use common sense reasoning in addition to the provided context.
If the context provides partial information, you may expand on it reasonably.""",
    
    "concise": """Provide brief, direct answers. Maximum 2-3 sentences.""",
    
    "detailed": """Provide comprehensive answers with full explanations and citations from the context."""
}

__all__ = ["SYSTEM_PROMPT", "PROMPT_VARIANTS", "load_system_prompt"]