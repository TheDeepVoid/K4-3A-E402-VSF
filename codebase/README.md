# AI Pipeline Template

## Project Structure

```
codebase/
├── providers/              # AI Provider implementations
│   ├── __init__.py
│   ├── base.py            # Abstract base class
│   ├── openai_provider.py # OpenAI provider
│   ├── gemini_provider.py # Google Gemini provider
│   ├── openrouter_provider.py # OpenRouter provider
│   └── omniroute_provider.py # OmniRoute with fallback
├── config/
│   ├── __init__.py
│   └── system_prompt.py   # Prompt engineering (Person 2)
├── tests/
│   ├── __init__.py
│   └── test_cases.py      # Golden test set (Person 3)
├── eval.py                # Evaluation runner
├── demo.py                # Live demo script
├── requirements.txt       # Dependencies
└── main.py                # Entry point (to be created)
```

## Setup

```bash
cd codebase
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
```

## Usage

### Run Demo
```bash
python demo.py --provider openai --model gpt-5-nano
```

### Run Evaluation
```bash
python eval.py --provider openai --model gpt-5-nano
```

## Roles

| Person | Role | Focus |
|--------|------|-------|
| Person 1 | AI Implementation | Connect real AI, fix providers |
| Person 2 | Test/Golden Set | Refine prompts in `config/system_prompt.py` |
| Person 3 | Evaluation | Run `eval.py`, analyze results |

## Test Cases (15 total)

- **Normal** (4): Standard Q&A from context
- **Missing Info** (3): Question without required context
- **No Answer** (3): Question unrelated to context
- **Difficult** (3): Requires reasoning/calculation
- **Edge Case** (2): Empty context, unusual formatting