import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI
from env import get_api_key
# from prompting.prompts import SYSTEM_PROMPT

ROOT = Path(__file__).resolve().parents[2]

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
parser.add_argument(
    "--prompt",
    default="codebase/src/prompting/system_prompt.md",
)
parser.add_argument("--prompt-version", default="v1.0")
args = parser.parse_args()

prompt_path = ROOT / args.prompt
content = prompt_path.read_text(encoding="utf-8-sig")

prompt_lines = []
inside = False
closed = False

for line in content.splitlines():
    if not inside:
        if line.strip() == "```text":
            inside = True
        continue

    if line.strip() == "```":
        closed = True
        break

    prompt_lines.append(line)

SYSTEM_PROMPT = "\n".join(prompt_lines).strip()

if not closed or not SYSTEM_PROMPT:
    raise SystemExit("Không đọc được khối system prompt hoàn chỉnh.")

input_path = ROOT / args.input
case_id = input_path.stem
output_path = ROOT / args.output

# Không ghi đè kết quả của lượt trước.
if output_path.exists():
    raise SystemExit("File output đã tồn tại. Hãy chọn tên output khác.")

payload = json.loads(input_path.read_text(encoding="utf-8-sig"))
api_key = get_api_key("openai")
if not api_key:
    raise SystemExit("Chưa đọc được OPENAI_API_KEY.")

result = {
    "test_id": case_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "provider": "openai",
    "requested_model": args.model,
    "prompt_version": args.prompt_version,
    "prompt_file": args.prompt,
    "system_prompt": SYSTEM_PROMPT,
    "input": payload,
    "status": "NEEDS_REVIEW",
    "passed": None,
    "reason": "",
    "actual_output": "",
}

started = time.perf_counter()
print(f"Đang gọi API cho {case_id}...", flush=True)

try:
    with OpenAI(
        api_key=api_key,
        timeout=120.0,
        max_retries=0,
    ) as client:
        response = client.responses.create(
            model=args.model,
            instructions=SYSTEM_PROMPT,
            input=json.dumps(payload, ensure_ascii=False),
            max_output_tokens=6000,
            store=False,
        )

    result["actual_output"] = response.output_text
    result["actual_model"] = response.model
    result["response_status"] = response.status
    result["usage"] = (
        response.usage.model_dump() if response.usage else None
    )

    if response.status != "completed":
        result["status"] = "ERROR"
        result["reason"] = "API chưa hoàn thành phản hồi."
        result["incomplete_details"] = (
            response.incomplete_details.model_dump()
            if response.incomplete_details else None
        )
    else:
        try:
            json.loads(response.output_text)
            result["reason"] = (
                f"JSON hợp lệ; cần chấm schema và tiêu chí {case_id}."
            )
        except json.JSONDecodeError:
            result["status"] = "FAIL"
            result["passed"] = False
            result["reason"] = "Output không phải JSON hợp lệ."

except Exception as exc:
    result["status"] = "ERROR"
    result["reason"] = f"Lỗi gọi API: {type(exc).__name__}"
    result["http_status"] = getattr(exc, "status_code", None)
    # Không lưu thông báo lỗi thô để tránh ghi thông tin nhạy cảm.

result["latency_ms"] = round(
    (time.perf_counter() - started) * 1000
)
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("TRANG THAI:", result["status"])
print("LY DO:", result["reason"])
print("DA LUU:", output_path)