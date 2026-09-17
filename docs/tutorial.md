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
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo
```

---

## Bước 2: Chạy Demo

Chạy script demo để kiểm tra pipeline:

```bash
# Sử dụng OpenAI
python codebase/src/demo.py --provider openai --model gpt-3.5-turbo

# Sử dụng Gemini
python codebase/src/demo.py --provider gemini --model gemini-3.5-flash-lite

# Sử dụng OpenRouter
python codebase/src/demo.py --provider openrouter --model gpt-3.5-turbo
```

---

## Bước 3: Chạy Evaluation

Chạy bộ test để đánh giá AI:

```bash
# Với OpenAI
python codebase/src/eval.py --provider openai --model gpt-3.5-turbo

# Với Gemini
python codebase/src/eval.py --provider gemini --model gemini-3.5-flash-lite

# Lưu kết quả ra file
python codebase/src/eval.py --provider openai --output results.json
```

Kết quả sẽ hiển thị:
- Tổng số test
- Số test passed/failed
- Tỷ lệ pass
- Chi tiết theo từng category

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
│   ├── providers/        # Các AI provider
│   │   ├── base.py       # Class cơ sở
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   ├── openrouter_provider.py
│   │   └── omniroute_provider.py
│   ├── env.py            # Đọc .env
│   ├── demo.py           # Script demo
│   └── eval.py           # Script đánh giá
├── tests/                # Unit tests
│   ├── test_cases.py     # Load test cases từ fixtures
│   └── fixtures/
│       └── test_cases_template.md
└── requirements.txt      # Dependencies
```

---

## Cách Thêm Provider Mới

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