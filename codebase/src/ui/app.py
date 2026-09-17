#!/usr/bin/env python3
"""VLearn Pulse — functional web UI (stdlib HTTP server, không cần cài thêm gì).

Server phục vụ file giao diện và các API gọi pipeline AI thật (có function
calling tools cho model):
   GET  /                → index.html
   GET  /api/health      → provider/model đang dùng, key có sẵn hay không
   GET  /api/meta        → cohort/lecture có trong data pack + danh sách học liệu
   POST /api/analyze     → lọc câu hỏi thật từ tutor_turns.csv theo scope, đưa
                           vào payload task=analyze_clusters; model được trang bị
                           tools preprocess_questions / cluster_questions /
                           ground_clusters (xem codebase/src/tools/)
   POST /api/card        → tạo thẻ ôn 5 phút (task=review_card,
                           teacher_confirmed_source=true) — cùng cơ chế tools

Bảo mật:
- Chỉ lắng nghe trên 127.0.0.1 (mặc định) — data pack nhạy cảm.
- Không in/hiện API key hay base URL; client chỉ nhận provider + model.
- Client KHÔNG nhận câu hỏi nguyên văn hay mã học viên — chỉ nhận cluster
  (example_questions đã ẩn danh), số liệu aggregate và tên tool đã chạy.

Cấu hình (qua .env hoặc biến môi trường, giống run_cases.py):
   UI_PROVIDER / DEFAULT_PROVIDER   — provider (openai|openrouter|omniroute|gemini)
   <PROVIDER>_API_KEY, <PROVIDER>_BASE_URL, <PROVIDER>_MODEL
   UI_PORT (mặc định 8701), UI_HOST (mặc định 127.0.0.1)

Chạy:
   .venv/bin/python codebase/src/ui/app.py
"""
import argparse
import csv
import json
import os
import re
import sys
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "codebase/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# -------------------- argument parsing --------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="VLearn Pulse — functional web UI (stdlib HTTP server, không cần cài thêm gì).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8701)
    parser.add_argument("--no_browser", action="store_true")
    # New arguments for provider and model selector (like run_cases.py)
    parser.add_argument("--provider", choices=["openai", "openrouter", "omniroute", "gemini"],
                        default=None,
                        help="Tên provider; mặc định lấy DEFAULT_PROVIDER trong .env")
    parser.add_argument("--model", default=None,
                        help="Model; mặc định <PROVIDER>_MODEL / DEFAULT_MODEL")
    parser.add_argument("--base-url", default=None,
                        help="Ghi đè base URL (mặc định <PROVIDER>_BASE_URL)")
    parser.add_argument("--api-key", default=None,
                        help="Ghi đè API key (mặc định <PROVIDER>_API_KEY)")
    return parser.parse_args()

# Set environment variables based on CLI args (if provided) before loading config
args = parse_args()
if args.provider:
    os.environ["DEFAULT_PROVIDER"] = args.provider
if args.model:
    # Determine provider for model env var (use args.provider if set, else from env or default)
    provider_for_model = args.provider or os.environ.get("DEFAULT_PROVIDER", "openai")
    os.environ[f"{provider_for_model.upper()}_MODEL"] = args.model
if args.base_url:
    provider_for_base = args.provider or os.environ.get("DEFAULT_PROVIDER", "openai")
    os.environ[f"{provider_for_base.upper()}_BASE_URL"] = args.base_url
if args.api_key:
    provider_for_key = args.provider or os.environ.get("DEFAULT_PROVIDER", "openai")
    os.environ[f"{provider_for_key.upper()}_API_KEY"] = args.api_key

# Now import modules that depend on the environment
from prompting.prompts import SYSTEM_PROMPT  # noqa: E402  (bản đang giữ — v1.2)
from tools.engine import (  # noqa: E402
    get_engine_config, call_llm_with_tools,
)

# -------------------- configuration --------------------
ENGINE_CONFIG = get_engine_config()
PROVIDER = ENGINE_CONFIG["provider"]
MODEL = ENGINE_CONFIG["model"]
HAS_KEY = bool(ENGINE_CONFIG["api_key"])
DEFAULT_CHAR_BUDGET = 30_000
MAX_CHAR_BUDGET = 120_000
DEFAULT_SAMPLE_SIZE = 200
MAX_SAMPLE_SIZE = 800

SEG_RE = re.compile(r"^\*\*\[(T\d{2}-\d{3})\]\*\*(.*)$")

# ---------------- gọi model (có tools) ----------------
def call_llm(payload: dict) -> tuple[str, list, str]:
    """Gọi model với system prompt hiện tại + tools preprocess/cluster/ground.

    Trả về (final_text, trace, error); trace là list tool call đã chạy.
    """
    return call_llm_with_tools(payload, SYSTEM_PROMPT)

def extract_json(text):
    """Lấy JSON từ text output; chịu được code fence ```json ... ``` và lời dẫn/đuôi bằng prose trước/sau JSON."""
    data = text.strip()
    while data.startswith("```"):
        nl = data.find("\n")
        data = (data[nl + 1:] if nl != -1 else data[3:]).strip()
    for _ in range(3):
        data = data.strip()
        if data.endswith("```"):
            data = data[:-3].rstrip()
    start, end = data.find("{"), data.rfind("}")
    if start != -1 and end != -1 and end > start:
        data = data[start:end + 1]
    return data

# -------------------- HTTP handler --------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to suppress logs unless needed
        return

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_file(UI_DIR / "index.html", "text/html")
        elif parsed.path == "/api/health":
            self._set_headers()
            self.wfile.write(json.dumps({
                "provider": PROVIDER,
                "model": MODEL,
                "has_key": HAS_KEY,
                "status": "ok"
            }).encode())
        elif parsed.path == "/api/meta":
            self._handle_meta()
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/analyze":
            self._handle_analyze()
        elif parsed.path == "/api/card":
            self._handle_card()
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def _serve_file(self, path: Path, content_type: str):
        try:
            data = path.read_bytes()
            self._set_headers(200, content_type)
            self.wfile.write(data)
        except Exception:
            self._set_headers(404)
            self.wfile.write(b'{"error":"file not found"}')

    def _handle_meta(self):
        # Return available cohorts/lectures and learning materials
        try:
            cohorts = set()
            lectures = set()
            materials = []
            trans_dir = DATA_DIR / "transcript"
            if trans_dir.is_dir():
                for md in trans_dir.glob("*.md"):
                    cohorts.add(md.stem.split("_")[0])
                    lectures.add(md.stem)
                    # Try to read first few lines for title
                    try:
                        lines = md.read_text(encoding="utf-8").splitlines()
                        title = lines[0] if lines else md.stem
                        materials.append({"id": md.stem, "title": title})
                    except Exception:
                        materials.append({"id": md.stem, "title": md.stem})
            self._set_headers()
            self.wfile.write(json.dumps({
                "cohorts": sorted(cohorts),
                "lectures": sorted(lectures),
                "materials": materials
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _handle_analyze(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            self._set_headers(400)
            self.wfile.write(b'{"error":"empty body"}')
            return
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(b'{"error":"invalid JSON"}')
            return

        # Validate required fields
        required = ["cohort", "lecture", "task"]
        if not all(k in payload for k in required):
            self._set_headers(400)
            self.wfile.write(b'{"error":"missing required fields"}')
            return

        # Filter tutor_turns.csv by cohort and lecture
        try:
            filtered = self._filter_tutor_turns(payload["cohort"], payload["lecture"])
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Failed to filter tutor_turns: {e}"}).encode())
            return

        if not filtered:
            self._set_headers(404)
            self.wfile.write(b'{"error":"no matching tutor turns"}')
            return

        # Build the payload for the AI model
        ai_payload = {
            "task": payload["task"],
            "tutor_turns": filtered,
            "char_budget": payload.get("char_budget", DEFAULT_CHAR_BUDGET),
        }

        # Call the model with tools
        start = datetime.now()
        try:
            final_text, trace, error = call_llm(ai_payload)
            latency_ms = int((datetime.now() - start).total_seconds() * 1000)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Model call failed: {e}"}).encode())
            return

        if error:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": error, "trace": trace}).encode())
            return

        # Extract JSON from model output
        try:
            json_text = extract_json(final_text)
            result = json.loads(json_text)
        except (json.JSONDecodeError, ValueError) as e:
            # If not JSON, wrap in a text response
            result = {"output": final_text}

        self._set_headers()
        self.wfile.write(json.dumps({
            "provider": PROVIDER,
            "model": MODEL,
            "trace": trace,
            "latency_ms": latency_ms,
            "result": result
        }).encode())

    def _handle_card(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            self._set_headers(400)
            self.wfile.write(b'{"error":"empty body"}')
            return
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(b'{"error":"invalid JSON"}')
            return

        # Validate required fields
        required = ["cohort", "lecture", "teacher_confirmed_source"]
        if not all(k in payload for k in required):
            self._set_headers(400)
            self.wfile.write(b'{"error":"missing required fields"}')
            return

        # Filter tutor_turns.csv by cohort and lecture
        try:
            filtered = self._filter_tutor_turns(payload["cohort"], payload["lecture"])
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Failed to filter tutor_turns: {e}"}).encode())
            return

        if not filtered:
            self._set_headers(404)
            self.wfile.write(b'{"error":"no matching tutor turns"}')
            return

        # Build the payload for the AI model
        ai_payload = {
            "task": "review_card",
            "tutor_turns": filtered,
            "teacher_confirmed_source": payload["teacher_confirmed_source"],
            "char_budget": payload.get("char_budget", DEFAULT_CHAR_BUDGET),
        }

        # Call the model with tools
        start = datetime.now()
        try:
            final_text, trace, error = call_llm(ai_payload)
            latency_ms = int((datetime.now() - start).total_seconds() * 1000)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Model call failed: {e}"}).encode())
            return

        if error:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": error, "trace": trace}).encode())
            return

        # Extract JSON from model output
        try:
            json_text = extract_json(final_text)
            result = json.loads(json_text)
        except (json.JSONDecodeError, ValueError) as e:
            # If not JSON, wrap in a text response
            result = {"output": final_text}

        self._set_headers()
        self.wfile.write(json.dumps({
            "provider": PROVIDER,
            "model": MODEL,
            "trace": trace,
            "latency_ms": latency_ms,
            "result": result
        }).encode())

    def _filter_tutor_turns(self, cohort: str, lecture: str) -> list[dict]:
        """Return list of dicts with keys: id, text, user, timestamp."""
        if not CSV_PATH.is_file():
            return []
        results = []
        with CSV_PATH.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Expect columns: cohort, lecture, tutor_turn_id, tutor_turn_text, tutor_turn_timestamp, student_id
                if row.get("cohort") == cohort and row.get("lecture") == lecture:
                    results.append({
                        "id": row.get("tutor_turn_id", ""),
                        "text": row.get("tutor_turn_text", ""),
                        "user": "teacher",  # assuming tutor_turn is from teacher
                        "timestamp": row.get("tutor_turn_timestamp", "")
                    })
        return results

def main():
    global args  # Make args available to the server setup
    # Parse args again inside main to avoid shadowing issues (though we already parsed globally)
    # But we need to use the parsed args for host, port, no_browser
    # We'll reuse the global args set at module level
    print(f"Starting VLearn Pulse on http://{args.host}:{args.port}")
    print(f"Provider: {PROVIDER} | Model: {MODEL} | Has key: {HAS_KEY}")
    if args.no_browser:
        print("Browser auto-open disabled.")
    try:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        if not args.no_browser:
            # Attempt to open the default browser
            import webbrowser
            webbrowser.open(f"http://{args.host}:{args.port}")
        print("Server started. Press Ctrl+C to stop.")
        while True:
            thread.join(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        server.server_close()
        print("Server stopped.")

if __name__ == "__main__":
    main()