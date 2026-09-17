# Hướng Dẫn Sử Dụng

## Giới thiệu

Đây là hướng dẫn cách chạy và sử dụng dự án AI Pipeline cho VLearn Pulse.

## Yêu cầu

- Python 3.9+
- API key từ các provider (OpenAI, Gemini, OpenRouter, OmniRoute)

---

## Bước 1: Cài đặt

### Clone dự án

```bash
cd /home/aminix/Projects/K4-3A-E402-VSF
```

### Cài đặt dependencies

```bash
pip install -r codebase/requirements.txt
```

### Thiết lập API Keys

```bash
# Sao chép file mẫu
cp .env.example .env

# Chỉnh sửa file .env và thêm API key của bạn
```

Nội dung file `.env`:
```env
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
OPENROUTER_API_KEY=your-openrouter-key
OMNIROUTE_API_KEY=your-omniroute-key
DEFAULT_PROVIDER=omniroute
DEFAULT_MODEL=kiro/deepseek-3.2
```

---

## Bước 2: Chạy Demo (tùy chọn)

> **Lưu ý**: Các script `demo.py` và `eval.py` gốc đã bị loại bỏ trong quá trình làm sạch.
> Để chạy pipeline, hãy sử dụng các script trong thư mục `evaluation/` và `ui/` như được mô tả bên dưới.

---

## Bước 3: Chạy Evaluation

Chạy bộ test để đánh giá AI:

```bash
# 1. Sinh golden set từ 19 case JSON
python codebase/src/evaluation/build_golden_set.py

# 2. Chạy case qua provider (mặc định lấy DEFAULT_PROVIDER trong .env;
#    API key/base URL đọc từ <PROVIDER>_API_KEY / <PROVIDER>_BASE_URL)
python codebase/src/evaluation/run_cases.py --provider omniroute \
    --prompt-file codebase/src/prompting/system_prompt.md --tag run_003_v1_2 \
    --model kiro/deepseek-3.2

# 3. Tính 4 metrics + comparison
python codebase/src/evaluation/score_runs.py
```

---

## Cấu trúc Dự án

```
codebase/
├── data/                 # Dữ liệu mẫu và processed (không commit)
├── notebooks/            # Jupyter notebooks (EDA và thử nghiệm)
├── src/                  # Source code chính
│   ├── preprocessing/    # Làm sạch và chuẩn hóa data
│   ├── clustering/       # Thuật toán gom nhóm câu hỏi
│   ├── grounding/        # Liên kết với học liệu
│   ├── ui/               # Giao diện người dùng
│   │   └── mockup.html
│   ├── prompting/        # Prompt engineering
│   │   ├── system_prompt.md
│   │   ├── prompts.py
│   │   └── prompt_versions.md
│   ├── providers/        # Các AI provider (legacy, không còn được sử dụng)
│   │   ├── base.py       # Class cơ sở
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   ├── openrouter_provider.py
│   │   └── omniroute_provider.py
│   ├── env.py            # Đọc .env
│   ├── evaluation/       # Bộ công cụ eval (golden set, runner, scorer, noise)
│   │   ├── build_golden_set.py  # sinh eval/golden_set
│   │   ├── run_cases.py         # chạy case qua API (chọn provider: --provider)
│   │   ├── score_runs.py        # chấm điểm + tính 4 metrics
│   │   ├── dedup_noise.py       # thí nghiệm Noise Resistance
│   │   └── dedup_experiment.py  # thí nghiệm Noise Resistance cho v1.1
│   ├── tools/            # Function calling cho model
│   │   ├── schemas.py      # OpenAI tool schemas (3 tool trên)
│   │   ├── registry.py     # Tên tool → hàm thực thi (+ wrapper an toàn)
│   │   ├── engine.py       # Vòng lặp gọi-chạy-trả kết quả; tự inject pipeline nếu model không gọi tool
│   │   └── selftest.py     # Kiểm thử tool calling với API thật
├── tests/                # Unit tests
│   ├── test_tools.py     # Unit test 3 module tool + engine (chạy `python -m unittest tests.test_tools`)
│   └── fixtures/
│       └── test_cases_template.md
└── requirements.txt      # Dependencies
```

---

## Cách Thêm Provider Mới

> **Lưu ý**: Các provider trong `src/providers/` hiện không được sử dụng trong pipeline chính.
> Pipeline hiện tại sử dụng việc gọi trực tiếp OpenAI SDK qua `tools/engine.py`.
> Tuy nhiên, nếu bạn muốn tham khảo hoặc sử dụng lại các provider này, bạn có thể làm như sau:

### Bước 1: Tạo provider file

Tạo file `codebase/src/providers/myprovider_provider.py`:

```python
from .base import BaseAIProvider, AIResponse, EmbeddingResponse, ProviderConfig

class MyProvider(BaseAIProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # Khởi tạo client

    async def chat_completion(self, messages, **kwargs):
        # Triển khai chat completion
        pass

    async def get_embeddings(self, texts, **kwargs):
        # Triển khai embeddings
        pass
```

### Bước 2: Thêm vào __init__.py

```python
from .myprovider_provider import MyProvider
```

### Bước 3: Cập nhật eval.py

Thêm provider vào danh sách trong `run_evaluation()`.

---

## Cách Sửa Test Cases

Chỉnh sửa file `codebase/tests/fixtures/test_cases_template.md`:

```markdown
### norm_001
- **Input**: ...
- **Context**: ...
- **Expected**: ...
- **Criteria**: ...
```

Eval script sẽ tự động load từ file này.

---

## Cách Sửa System Prompt

Chỉnh sửa file `codebase/src/prompting/system_prompt.md`:

```markdown
## Prompt Mặc định

```
Bạn là AI assistant...
```
```

Config sẽ tự động load prompt từ file này.

---

## Troubleshooting

### Lỗi authentication

Kiểm tra API key trong file `.env` đã đúng chưa.

### Module not found

```bash
pip install -r codebase/requirements.txt
```

### Lỗi import

Đảm bảo đang chạy từ thư mục gốc của dự án.

---

## Liên hệ

Nếu có câu hỏi, vui lòng tạo issue trên GitHub.
