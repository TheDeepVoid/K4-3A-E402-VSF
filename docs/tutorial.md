# Hướng Dẫn Sử Dụng

## Giới thiệu

Đây là hướng dẫn cách chạy và sử dụng dự án AI Pipeline cho VLearn Pulse.

Luôn chạy **model rẻ nhất còn đang phục vụ**. Không dùng ID đã ngừng (`gpt-3.5-turbo`, `gemini-pro`, `gemini-1.5-flash`).

## Yêu cầu

- Python 3.9+
- API key từ các provider (OpenAI, Gemini, OpenRouter, OmniRoute)

## Model rẻ nhất còn phục vụ (tháng 9/2026)

| Provider | Model ID | Ghi chú |
| --- | --- | --- |
| OpenAI | `gpt-5-nano` | Rẻ nhất trên bảng giá OpenAI (~$0.05 / $0.40 mỗi 1M token) |
| Gemini | `gemini-2.5-flash-lite` | Rẻ nhất hiện tại; `gemini-pro` / `gemini-1.5-*` đã deprecated |
| OpenRouter | `google/gemma-4-31b-it:free` | Miễn phí (có rate-limit). Fallback trả phí: `mistralai/mistral-nemo` |
| OmniRoute | `gpt-5-nano` | Router tương thích OpenAI; gửi ID rẻ để chọn route rẻ nhất |

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
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-5-nano
FALLBACK_PROVIDER=openrouter
```

---

## Bước 2: Chạy Demo

Chạy script demo với model rẻ nhất còn phục vụ:

```bash
# OpenAI — rẻ nhất
python codebase/demo.py --provider openai --model gpt-5-nano

# Gemini — rẻ nhất
python codebase/demo.py --provider gemini --model gemini-2.5-flash-lite

# OpenRouter — miễn phí
python codebase/demo.py --provider openrouter --model google/gemma-4-31b-it:free

# OmniRoute — route rẻ nhất
python codebase/demo.py --provider omniroute --model gpt-5-nano
```

Nếu OpenRouter `:free` bị rate-limit:

```bash
python codebase/demo.py --provider openrouter --model mistralai/mistral-nemo
```

---

## Bước 3: Chạy Evaluation

Chạy bộ test với cùng các model rẻ nhất:

```bash
# OpenAI
python codebase/eval.py --provider openai --model gpt-5-nano

# Gemini
python codebase/eval.py --provider gemini --model gemini-2.5-flash-lite

# OpenRouter
python codebase/eval.py --provider openrouter --model google/gemma-4-31b-it:free

# OmniRoute
python codebase/eval.py --provider omniroute --model gpt-5-nano

# Lưu kết quả ra file
python codebase/eval.py --provider openai --model gpt-5-nano --output results.json
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
├── providers/           # Các AI provider
│   ├── base.py          # Class cơ sở
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   ├── openrouter_provider.py
│   └── omniroute_provider.py
├── docs/                # Template files
│   ├── system_prompt_template.md
│   └── test_cases_template.md
├── config/              # Cấu hình
│   ├── env.py           # Đọc .env
│   └── system_prompt.py
├── tests/               # Test cases
│   └── test_cases.py
├── eval.py              # Script đánh giá
├── demo.py              # Script demo
└── requirements.txt     # Dependencies
```

---

## Cách Thêm Provider Mới

### Bước 1: Tạo provider file

Tạo file `codebase/providers/myprovider_provider.py`:

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

### Bước 2: Thêm vào `__init__.py`

```python
from .myprovider_provider import MyProvider
```

### Bước 3: Cập nhật eval.py

Thêm provider vào danh sách trong `run_evaluation()`.

---

## Cách Sửa Test Cases

Chỉnh sửa file `codebase/docs/test_cases_template.md`:

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

Chỉnh sửa file `codebase/docs/system_prompt_template.md`. Config sẽ tự động load prompt từ file này.

---

## Troubleshooting

### Lỗi authentication

Kiểm tra API key trong file `.env` đã đúng chưa.

### Model not found / model deprecated

Đừng dùng `gpt-3.5-turbo`, `gemini-pro`, `gemini-1.5-flash`. Dùng đúng ID trong bảng phía trên.

### OpenRouter `:free` bị 429

Đổi sang `mistralai/mistral-nemo` (rẻ, trả phí).

### Module not found

```bash
pip install -r codebase/requirements.txt
```

### Lỗi import

Đảm bảo đang chạy từ thư mục gốc của dự án.

---

## Liên hệ

Nếu có câu hỏi, vui lòng tạo issue trên GitHub.
