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
│   └── env.py             ← utils để lấy API key và cấu hình từ .env
```

## Mô tả chi tiết

### `src/`
Nơi chứa toàn bộ mã nguồn của hệ thống.

#### `preprocessing/`
- `preprocess.py`: **Tool** `preprocess_questions` – lọc câu hỏi preset/rỗng, chuẩn hoá văn bản, loại bỏ trùng lặp theo học viên.

#### `clustering/`
- `cluster.py`: **Tool** `cluster_questions` – gom nhóm câu hỏi thành các chủ đề dựa trên độ tương đồng Jaccard của từ khóa (unigram+bigram), deterministic.

#### `grounding/`
- `ground.py`: **Tool** `ground_clusters` – liên kết từng cụm với đoạn học liệu có mã trích dẫn `[Txx-NNN]` qua tf-idf, trả về top-k đoạn kèm snippet.

#### `tools/`
Hệ thống function calling cho LLM.
- `schemas.py`: Định nghĩa JSON schema cho 3 tool trên (OpenAI function calling format).
- `registry.py`: Bản đồ tên tool → hàm thực thi, bao gồm wrapper an toàn để chạy tool và bắt lỗi.
- `engine.py`: Vòng lặp chính:
  1. Gọi `chat.completions` với `tools=TOOL_SCHEMAS`, `tool_choice="auto"`.
  2. Nếu model trả `tool_calls` → chạy từng tool qua registry, đưa kết quả về dưới dạng message `role="tool"`, затем gọi lại.
  3. Nếu model **không** gọi tool ở vòng đầu (ví dụ do provider không hỗ trợ ổn định), tự động "inject" chuỗi tool determinístico (`preprocess → cluster → ground`) như `tool_calls` thật, trả kết quả cho model. Nhờ vậy 3 tool **luôn** được dùng, model chỉ cần tập trung vào phần tổng hợp cuối cùng.
  4. Hỗ trợ cả `native tool_calls` và việc model nhúng `<function_calls>` trong nội dung (parse qua XML).
- `selftest.py`: Kiểm thử end-to-end với API thật (cần cấu hình `.env`).

#### `ui/`
Giao diện web функционал.
- `app.py`: HTTP server stdlib (không cần FastAPI/uvicorn) cung cấp:
  - `GET /` → trả về `index.html`
  - `GET /api/health` → kiểm tra trạng thái
  - `GET /api/meta` → trả về metadata (provider, model, v.v.)
  - `POST /api/analyze` → chạy pipeline đầy đủ trên danh sách câu hỏi, trả về kết quả phân tích (cụm, grounding, v.v.)
  - `POST /api/card` → tạo thẻ ôn tập cho một cụm cụ thể.
- `index.html`: Frontend thực tế, gọi API thật để hiển thị danh sách câu hỏi, cụm, và tạo thẻ ôn.
- `mockup.html`: Giao diện mockup cũ (được dùng trong phiên bản demo trước) – **không còn được sử dụng** bởi `app.py`.

#### `prompting/`
- `system_prompt.md`: Prompt hệ thống mặc định (có thể覆盖 qua biến môi trường).
- `prompts.py`: Hàm trợ giúp để construir prompt cuối cùng từ system prompt và dữ liệu đầu vào.
- `prompt_versions.md`: Lịch sử thay đổi prompt.

#### `providers/` (legacy)
Bộ cung cấp AI ban đầu (OpenAIProvider, GeminiProvider, v.v.) – **đã được thay thế** bằng việc gọi trực tiếp OpenAI SDK qua `tools/engine.py`. Bộ mã này được giữ lại chỉ để tham khảo nhưng **không còn được import** ở bất kỳ nơi nào trong pipeline chính.

#### `env.py`
Hàm tiện ích `get_api_key(provider_name)` để đọc biến môi secrète từ `.env` hoặc `process.env`, cũng như tải cấu hình từ file `.env` (được gitignore).

## Các lệnh hữu ích

### Chạy UI server
```bash
# Từ thư mục gốc codebase
python src/ui/app.py
```
Server sẽ lắng nghe tại `http://127.0.0.1:8080` (mặc định).

### Chạy selftest (kiểm tra tool calling với API thật)
```bash
python src/tools/selftest.py
```
Cần cấu hình `.env` với ít nhất một provider (OMNIROUTE_API_KEY hoặc OPENAI_API_KEY, v.v.).

### Chạy bộ kiểm tra unit
```bash
python -m unittest discover -s src/tests -p "test_*.py"
```
Hoặc nếu có thể sử dụng pytest:
```bash
pytest
```

## Lưu ý bảo mật
- File `.env` chứa các khóa API **không được commit** vào git (đã nằm trong `.gitignore`).
- Tuyệt đối không chia sẻ hoặc trả về khóa API gốc cho người dùng finais; pipeline chỉ sử dụng chúng nội bộ để gọi model.
- Dữ liệu học viên được tối ưu ẩn danh trước khi cung cấp; pipeline chỉ làm việc với câu hỏi đã được làm sạch (không chứa mã học viên).

