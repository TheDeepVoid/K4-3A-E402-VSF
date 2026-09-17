# AI Pipeline Template

## Cấu Trúc Dự Án

```
codebase/
├── README.md           ← file này
├── data/              ← dữ liệu mẫu và processed (KHÔNG commit — xem quy định bảo mật)
│   └── vlearn-pack/   ← chatlog, slides, transcript
├── notebooks/         ← Jupyter notebooks cho EDA và thử nghiệm
├── src/               ← source code chính
│   ├── __init__.py
│   ├── preprocessing/ ← làm sạch và chuẩn hóa data
│   │   ├── __init__.py
│   │   └── preprocess.py   ← tool `preprocess_questions` (lọc preset/rỗng, chuẩn hoá, dedupe)
│   ├── clustering/    ← thuật toán gom nhóm câu hỏi
│   │   ├── __init__.py
│   │   └── cluster.py      ← tool `cluster_questions` (overlap/Jaccard trên từ khoá, deterministic)
│   ├── grounding/     ← liên kết với học liệu
│   │   ├── __init__.py
│   │   └── ground.py       ← tool `ground_clusters` (tf-idf cụm ↔ segment [Txx-NNN], trả top-k + snippet)
│   ├── tools/         ← function calling cho model (Person 1)
│   │   ├── __init__.py
│   │   ├── schemas.py      ← OpenAI tool schemas (3 tool trên)
│   │   ├── registry.py     ← tên tool → hàm thực thi (+ wrapper an toàn)
│   │   ├── engine.py       ← vòng lặp gọi-chạy-trả kết quả; tự inject pipeline nếu model không gọi tool
│   │   └── selftest.py     ← kiểm thử tool calling với API thật
│   ├── ui/            ← giao diện người dùng (functional web UI)
│   │   ├── __init__.py
│   │   ├── app.py     ← HTTP server + API gọi pipeline AI thật (stdlib, không cần cài thêm)
│   │   ├── index.html ← frontend (chạy từ mockup, call API thật)
│   │   └── mockup.html← giao diện mockup cũ (không được sử dụng trong phiên bản hiện tại)
│   ├── prompting/     ← prompt engineering (Person 2)
│   │   ├── __init__.py
│   │   ├── system_prompt.md
│   │   ├── prompts.py
│   │   └── prompt_versions.md
│   ├── providers/     ← AI Provider implementations (legacy, không còn được sử dụng)
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract base class
│   │   ├── openai_provider.py # OpenAI provider
│   │   ├── gemini_provider.py # Google Gemini provider
│   │   ├── openrouter_provider.py # OpenRouter provider
│   │   └── omniroute_provider.py # OmniRoute provider
│   ├── evaluation/    ← bộ công cụ eval (golden set, runner, scorer, noise)
│   │   ├── __init__.py
│   │   ├── build_golden_set.py  # sinh eval/golden_set
│   │   ├── run_cases.py         # chạy case qua API (chọn provider: --provider)
│   │   ├── score_runs.py        # chấm điểm + tính 4 metrics
│   │   ├── dedup_noise.py       # thí nghiệm Noise Resistance
│   │   └── dedup_experiment.py  # thí nghiệm Noise Resistance cho v1.1
│   ├── env.py         # Loads API keys from .env
├── tests/             # unit tests
│   ├── __init__.py
│   ├── test_tools.py  # Unit test 3 module tool + engine (chạy `python -m unittest tests.test_tools`)
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

Model được trang bị **3 tool function calling** (xem `src/tools/`):
- `preprocess_questions(questions)` — lọc is_preset/câu rỗng, chuẩn hoá, dedupe theo học viên
- `cluster_questions(questions)` — cụm chủ đề thô (overlap coeff trên unigram+bigram)
- `ground_clusters(clusters, materials)` — tìm đoạn `[Txx-NNN]` khớp từ khoá (tf-idf) kèm snippet

`tools/engine.py` chạy vòng lặp function calling. Mặc định **preinject**: engine chạy sẵn
chuỗi deterministic preprocess → cluster → ground và ghi thành các message
`assistant(tool_calls)` + `tool(result)` THẬT vào lịch sử, rồi model chỉ cần 1 round
(`create`) để tổng hợp output cuối (nhanh ~5–7× so với 3–4 round). Model vốn đã tự gọi
tool native (đã xác minh với OmniRoute), và engine vẫn nhận tool call ở cả 2 dạng:
field `tool_calls` chuẩn của OpenAI lẫn `<function_calls>` trong content (DeepSeek/
ApiMoose style — tự giải nén); nếu vòng đầu model không gọi tool thì engine inject luôn.
Dù model có gọi hay không, 3 tool LUÔN chạy — dữ liệu thật và deterministic, model chỉ
phán đoán + viết output theo schema v1.2.

Kiểm tra nhanh (không cần khởi động UI):
```bash
python -m unittest tests.test_tools            # 16 unit test deterministic
python src/tools/selftest.py                   # gọi tool với API thật (OmniRoute local)
```

API (frontend gọi qua fetch):
- `GET /api/health` → provider/model đang dùng, có key hay không (không trả secret)
- `GET /api/meta` → cohort/bài giảng/thời gian có trong data pack + metadata 6 transcript
- `POST /api/analyze` → gửi câu hỏi thật theo scope (code chỉ lọc scope; preset/rỗng/dedupe
  do tool `preprocess_questions` xử lý) → model gom cụm (task=`analyze_clusters`)
- `POST /api/card` → tạo thẻ ôn 5 phút (task=`review_card`, `teacher_confirmed_source=true`),
  tool `ground_clusters` tìm nguồn cho selected_cluster

Bảo mật: client chỉ nhận cluster đã ẩn danh + số liệu aggregate + tên tool đã chạy — KHÔNG
nhận câu hỏi nguyên văn hay mã học viên.


## Test Cases (15 total)

- **Normal** (4): Standard Q&A from context
- **Missing Info** (3): Question without required context
- **No Answer** (3): Question unrelated to context
- **Difficult** (3): Requires reasoning/calculation
- **Edge Case** (2): Empty context, unusual formatting
