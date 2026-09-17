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
│   ├── ui/            ← giao diện người dùng (functional web UI)
│   │   ├── __init__.py
│   │   ├── app.py     ← HTTP server + API gọi pipeline AI thật (stdlib, không cần cài thêm)
│   │   └── index.html ← frontend (chạy từ mockup, call API thật)
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
│   │   ├── run_cases.py         # chạy case qua API (chọn provider: --provider)
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

### Pipeline evaluation mới (runner đa provider)
```bash
# 1. Sinh golden set từ 19 case JSON
python src/evaluation/build_golden_set.py

# 2. Chạy case qua provider (mặc định lấy DEFAULT_PROVIDER trong .env;
#    API key/base URL đọc từ <PROVIDER>_API_KEY / <PROVIDER>_BASE_URL)
python src/evaluation/run_cases.py --provider omniroute \
    --prompt-file codebase/src/prompting/system_prompt.md --tag run_003_v1_2 \
    --model kiro/deepseek-3.2

# 3. Tính 4 metrics + comparison
python src/evaluation/score_runs.py
```

### Web UI functional
```bash
# Chạy server (mặc định http://127.0.0.1:8701/; data pack nhạy cảm nên chỉ host local)
python src/ui/app.py

# Tuỳ chọn: đổi provider/port
UI_PROVIDER=omniroute UI_PORT=8701 python src/ui/app.py --host 127.0.0.1
```
UI tự chọn provider: ưu tiên `omniroute` nếu có `OMNIROUTE_API_KEY` (router local — không
gửi data ra ngoài), rồi mới đến `DEFAULT_PROVIDER`/`openai`. Cấu hình tương tự
`run_cases.py`: `<PROVIDER>_API_KEY / <PROVIDER>_BASE_URL / <PROVIDER>_MODEL`.

API (frontend gọi qua fetch):
- `GET /api/health` → provider/model đang dùng, có key hay không (không trả secret)
- `GET /api/meta` → cohort/bài giảng/thời gian có trong data pack + metadata 6 transcript
- `POST /api/analyze` → lọc câu hỏi thật theo scope (bỏ preset/câu rỗng bằng code),
  gom cluster bằng system prompt (task=`analyze_clusters`)
- `POST /api/card` → tạo thẻ ôn 5 phút (task=`review_card`, `teacher_confirmed_source=true`)

Bảo mật: client chỉ nhận cluster đã ẩn danh + số liệu aggregate — KHÔNG nhận câu hỏi
nguyên văn hay mã học viên.

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