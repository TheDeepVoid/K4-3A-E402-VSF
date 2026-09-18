import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add codebase to path for relative imports if run from root
sys.path.insert(0, str(Path(__file__).parent.parent))

from providers import OpenAIProvider, GeminiProvider, OpenRouterProvider, OmniRouteProvider
from providers.base import ProviderConfig
from env import get_api_key, PROVIDER_CONFIG

app = FastAPI(title="VLearn Pulse API")

# Setup paths
UI_DIR = Path(__file__).parent

class GenerateRequest(BaseModel):
    topic: str
    desc: str
    question: str
    sources: list[str]

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
    provider_name = os.getenv("UI_PROVIDER")
    
    if not provider_name:
        if os.getenv("OMNIROUTE_API_KEY"):
            provider_name = "omniroute"
        else:
            provider_name = PROVIDER_CONFIG.get("default", "openai")
            
    model = os.getenv(f"{provider_name.upper()}_MODEL") or PROVIDER_CONFIG.get("default_model")
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

    # 3. Tạo Prompt từ file system_prompt_v1_1.md
    prompt_path = UI_DIR.parent / "prompting" / "system_prompt_v1_1.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    
    # Chuẩn bị dữ liệu theo contract của v1.1
    input_data = {
        "task": "review_card",
        "scope": {
            "cohort": "unknown",
            "lecture": "unknown",
            "time_range": "unknown"
        },
        "questions": [
            {
                "student": "S_Mock",
                "is_preset": False,
                "student_question": req.question
            }
        ],
        "materials": [
            {
                "source_id": s,
                "source_type": "transcript",
                "content": f"Nội dung minh họa của {s} về {req.topic}: Mục tiêu là giúp học viên hiểu rõ khái niệm này. Nhiều học viên thường nhầm lẫn khi áp dụng vào thực tế. Ví dụ đúng là phải thực hiện bước chuẩn bị trước khi phân tích. Câu hỏi kiểm tra: Bước nào quan trọng nhất trước khi phân tích?"
            } for s in req.sources
        ],
        "selected_cluster": {
            "concept": req.topic,
            "notes": req.desc
        },
        "teacher_confirmed_source": True
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)}
    ]
    
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
        
        review_card = data.get("review_card", {})
        
        # Luôn luôn đảm bảo response trả về có đủ 4 trường để giao diện cũ không bị vỡ
        return {
            "goal": review_card.get("learning_objective", f'Làm rõ "{req.topic}"'),
            "mis": review_card.get("misconception_to_check", "Chưa xác định rõ hiểu nhầm."),
            "example": review_card.get("short_explanation_example", "Hãy cung cấp thêm ví dụ từ bài giảng."),
            "question": review_card.get("understanding_check", "Hãy đặt câu hỏi kiểm tra lại.")
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
    import argparse
    
    parser = argparse.ArgumentParser(description="VLearn Pulse UI Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind to")
    args = parser.parse_args()
    
    port = int(os.environ.get("UI_PORT", 8701))
    
    print(f"Starting server at http://{args.host}:{port}/")
    uvicorn.run(app, host=args.host, port=port)
