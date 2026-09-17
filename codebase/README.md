# AI Pipeline Template

## Project Structure

```
codebase/
├── README.md           ← file này
├── data/              ← dữ liệu mẫu và processed (KHÔNG commit — xem quy định bảo mật)
│   └── vlearn-pack/   ← chatlog, slides, transcript
├── notebooks/         ← Jupyter notebooks cho EDA và thử nghiệm
├── src/               ← source code chính
│   ├── __init__.py
│   ├── preprocessing/ ← làm sạch và chuẩn hóa data
│   │   └── __init__.py
│   ├── clustering/    ← thuật toán gom nhóm câu hỏi
│   │   └── __init__.py
│   ├── grounding/     ← liên kết với học liệu
│   │   └── __init__.py
│   ├── ui/            ← giao diện người dùng
│   │   ├── __init__.py
│   │   └── mockup.html
│   ├── prompting/     ← prompt engineering (Person 2)
│   │   ├── __init__.py
│   │   ├── system_prompt.md
│   │   ├── prompts.py
│   │   └── prompt_versions.md
│   ├── providers/     ← AI Provider implementations
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract base class
│   │   ├── openai_provider.py # OpenAI provider
│   │   ├── gemini_provider.py # Google Gemini provider
│   │   ├── openrouter_provider.py # OpenRouter provider
│   │   └── omniroute_provider.py # OmniRoute with fallback
│   ├── evaluation/    ← bộ công cụ eval (golden set, runner, scorer, noise)
│   │   ├── __init__.py
│   │   ├── build_golden_set.py  # sinh eval/golden_set
│   │   ├── run_omniroute.py     # chạy case qua API
│   │   ├── score_runs.py        # chấm điểm + tính 4 metrics
│   │   ├── dedup_noise.py       # thí nghiệm Noise Resistance
│   │   └── dedup_experiment.py  # thí nghiệm Noise Resistance cho v1.1
│   ├── env.py         # Loads API keys from .env
│   ├── demo.py        # Live demo script
│   └── eval.py        # Evaluation runner
├── tests/             # unit tests
│   ├── __init__.py
│   ├── test_cases.py  # Golden test set loader (Person 3)
│   └── fixtures/
│       └── test_cases_template.md
└── requirements.txt   # Dependencies
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
python src/demo.py --provider openai --model gpt-5-nano
```

### Run Evaluation
```bash
python src/eval.py --provider openai --model gpt-5-nano
```

### Pipeline evaluation mới (OmniRoute)
```bash
# 1. Sinh golden set từ 19 case JSON
python src/evaluation/build_golden_set.py

# 2. Chạy 19 case qua OmniRoute
OMNIROUTE_BASE_URL=... OMNIROUTE_API_KEY=... python src/evaluation/run_omniroute.py \
    --prompt-file codebase/src/prompting/system_prompt.md --tag run_001_baseline \
    --model kiro/deepseek-3.2 --base-url $OMNIROUTE_BASE_URL --api-key $OMNIROUTE_API_KEY

# 3. Tính 4 metrics + comparison
python src/evaluation/score_runs.py
```

## Roles

| Person | Role | Focus |
|--------|------|-------|
| Person 1 | AI Implementation | Connect real AI, fix providers |
| Person 2 | Test/Golden Set | Refine prompts in `src/prompting/prompts.py` |
| Person 3 | Evaluation | Run `src/eval.py`, analyze results |

## Test Cases (15 total)

- **Normal** (4): Standard Q&A from context
- **Missing Info** (3): Question without required context
- **No Answer** (3): Question unrelated to context
- **Difficult** (3): Requires reasoning/calculation
- **Edge Case** (2): Empty context, unusual formatting