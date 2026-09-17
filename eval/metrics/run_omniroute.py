"""Chạy evaluation qua OmniRoute (local router, OpenAI-compatible).

Cách dùng:
    .venv/bin/python eval/metrics/run_omniroute.py \
        --prompt-file codebase/src/prompting/system_prompt.md \
        --prompt-version v1.0 \
        --tag run_001_baseline \
        --model kiro/deepseek-3.2 \
        --base-url <OMNIROUTE_BASE_URL> \
        --api-key sk-...

Mỗi case trong golden_set/*.json được gọi một lượt; kết quả ghi ra
eval/results/cases/<tag>_<case_id>.json. Run tổng hợp được ghi ở
eval/results/<tag>.json do --combine tạo sau khi tất cả case xong.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]


def load_system_prompt(prompt_path) -> str:
    """Đọc khối ```text trong file prompt (giống eval_one.py)."""
    content = Path(prompt_path).read_text(encoding="utf-8-sig")
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
    system_prompt = "\n".join(prompt_lines).strip()
    if not closed or not system_prompt:
        raise SystemExit("Không đọc được khối system prompt hoàn chỉnh.")
    return system_prompt


def extract_json(text):
    """Lấy JSON từ text output; chịu được khối code fence ```json ... ```."""
    data = text.strip()
    if data.startswith("```"):
        newline = data.find("\n")
        if newline != -1:
            data = data[newline + 1:]
        else:
            data = data[3:]
        data = data.strip()
    # Hỗ trợ nhiều fence mở đầu lẫn nhau
    while data.startswith("```"):
        newline = data.find("\n")
        data = (data[newline + 1:] if newline != -1 else data[3:]).strip()
    # Cắt fence đóng và bất kỳ prose phía sau (lấy từ '{' đầu tới '}' cuối)
    for _ in range(3):
        data = data.strip()
        if data.endswith("```"):
            data = data[:-3].rstrip()
    start, end = data.find("{"), data.rfind("}")
    if start != -1 and end != -1 and end > start:
        data = data[start:end + 1]
    return data


def run_case(client, payload: dict, system_prompt: str, model: str):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0.3,
        max_tokens=6000,
        timeout=300.0,
    )
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--prompt-version", default="v1.0")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--model", default="kiro/deepseek-3.2")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--golden-dir", default="eval/golden_set")
    parser.add_argument("--only", default=None,
                        help="Chỉ chạy case này (tên file không đuôi .json)")
    args = parser.parse_args()

    system_prompt = load_system_prompt(ROOT / args.prompt_file)

    client = OpenAI(
        api_key=args.api_key,
        base_url=args.base_url,
        timeout=330.0,
        max_retries=0,
    )

    case_paths = sorted((ROOT / args.golden_dir).glob("*.json"))
    if args.only:
        case_paths = [p for p in case_paths if p.stem == args.only]

    out_dir = ROOT / "eval/results/cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in case_paths:
        case_id = path.stem
        out_path = out_dir / f"{args.tag}_{case_id}.json"

        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        result = {
            "test_id": case_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "omniroute",
            "requested_model": args.model,
            "prompt_version": args.prompt_version,
            "prompt_file": args.prompt_file,
            "system_prompt": system_prompt,
            "input": payload,
            "status": "NEEDS_REVIEW",
            "passed": None,
            "reason": "",
            "actual_output": "",
        }

        print(f"=== {case_id} / {args.prompt_version} ===", flush=True)
        started = time.perf_counter()
        try:
            response = run_case(client, payload, system_prompt, args.model)
            result["actual_output"] = response.choices[0].message.content or ""
            result["actual_model"] = response.model
            result["response_status"] = response.choices[0].finish_reason
            result["usage"] = (
                response.usage.model_dump() if response.usage else None
            )
            parsed, json_error = None, None
            try:
                parsed = json.loads(extract_json(result["actual_output"]))
            except json.JSONDecodeError as exc:
                json_error = f"{type(exc).__name__}: {exc}"
            result["parsed_output"] = parsed
            if json_error:
                result["status"] = "FAIL"
                result["passed"] = False
                result["reason"] = f"Output không phải JSON hợp lệ: {json_error}"
            else:
                result["status"] = "NEEDS_REVIEW"
                result["reason"] = (
                    f"JSON hợp lệ; cần chấm schema và tiêu chí {case_id}."
                )
        except Exception as exc:
            result["status"] = "ERROR"
            result["reason"] = f"Lỗi gọi API: {type(exc).__name__}"
            result["error"] = str(exc)[:500]

        result["latency_ms"] = round((time.perf_counter() - started) * 1000)
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  {case_id}: {result['status']} ({result['latency_ms']} ms)",
              flush=True)

    print("DA CHAY:", len(case_paths), "case ->", out_dir)


if __name__ == "__main__":
    main()