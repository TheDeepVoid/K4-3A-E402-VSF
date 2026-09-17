import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add codebase to path for relative imports if run from root
sys.path.insert(0, str(Path(__file__).parent))

from providers import OpenAIProvider, GeminiProvider, OpenRouterProvider, OmniRouteProvider
from providers.base import ProviderConfig
from env import get_api_key, PROVIDER_CONFIG

app = FastAPI(title="VLearn Pulse API")

# Setup paths
SRC_DIR = Path(__file__).parent
UI_DIR = SRC_DIR / "ui"

class GenerateRequest(BaseModel):
    topic: str
    desc: str
    question: str
    source: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Phục vụ file giao diện mockup.html"""
    html_path = UI_DIR / "mockup.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Giao diện không tồn tại")
    return html_path.read_text(encoding="utf-8")

@app.post("/api/generate")
async def generate_flashcard(req: GenerateRequest):
    """API gọi model AI sinh nội dung Thẻ ôn tập (Flashcard)"""
    
    # 1. Load config
    provider_name = PROVIDER_CONFIG["default"]
    model = PROVIDER_CONFIG["default_model"]
    api_key = get_api_key(provider_name)
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail=f"Thiếu API Key cho provider '{provider_name}'. Vui lòng thêm vào file .env"
        )
        
    config = ProviderConfig(
        api_key=api_key,
        model=model,
        temperature=0.7,
        max_tokens=1000
    )
    
    # 2. Khởi tạo Provider
    if provider_name == "openai":
        provider = OpenAIProvider(config)
    elif provider_name == "gemini":
        provider = GeminiProvider(config)
    elif provider_name == "openrouter":
        provider = OpenRouterProvider(config)
    elif provider_name == "omniroute":
        provider = OmniRouteProvider(config)
    else:
        raise HTTPException(status_code=500, detail=f"Unknown provider: {provider_name}")

    # 3. Tạo Prompt
    # Dùng JSON mode hoặc prompt hướng dẫn JSON
    system_prompt = f"""Bạn là trợ lý giảng dạy AI. Nhiệm vụ của bạn là tạo một "Thẻ ôn tập 5 phút" dựa trên vấn đề mà học viên đang gặp khó khăn.

Dữ liệu đầu vào:
- Chủ đề: {req.topic}
- Mô tả: {req.desc}
- Câu hỏi minh hoạ của học viên: {req.question}
- Nguồn học liệu: {req.source}

Nhiệm vụ: Trả về kết quả CHUẨN ĐỊNH DẠNG JSON sau đây (không bao gồm text nào khác ngoài JSON, không cần bọc trong ```json):
{{
  "goal": "Viết ngắn gọn mục tiêu cần ôn lại (1 câu).",
  "mis": "Phân tích hiểu nhầm phổ biến của học viên dựa trên câu hỏi (1-2 câu).",
  "example": "Đưa ra một ví dụ giải thích siêu ngắn gọn, dễ hiểu để khắc phục (2-3 câu).",
  "question": "Đặt một câu hỏi trắc nghiệm hoặc kiểm tra nhanh để xem học viên đã hiểu chưa."
}}"""

    messages = [{"role": "system", "content": system_prompt}]
    
    try:
        response = await provider.chat_completion(messages)
        
        # Xử lý kết quả trả về, cắt bớt markdown ```json nếu có
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        data = json.loads(content)
        
        # Luôn luôn đảm bảo response trả về có đủ 4 trường
        return {
            "goal": data.get("goal", f'Làm rõ "{req.topic}"'),
            "mis": data.get("mis", "Chưa xác định rõ hiểu nhầm."),
            "example": data.get("example", "Hãy cung cấp thêm ví dụ từ bài giảng."),
            "question": data.get("question", "Hãy đặt câu hỏi kiểm tra lại.")
        }
        
    except json.JSONDecodeError:
        return {
            "error": True,
            "message": "AI không trả về chuẩn định dạng JSON.",
            "raw": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await provider.close()

if __name__ == "__main__":
    import uvicorn
    # Chạy server tại localhost:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
