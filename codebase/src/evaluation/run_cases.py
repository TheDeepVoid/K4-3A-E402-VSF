"""Chạy evaluation cho các case trong golden_set qua provider được chọn.

Provider có thể chọn bằng tham số --provider hoặc để mặc định lấy
DEFAULT_PROVIDER trong .env. Thông tin kết nối theo từng provider đọc từ
biến môi trường (có thể đặt trong .env):
    <PROVIDER>_API_KEY   — ví dụ OMNIROUTE_API_KEY, OPENAI_API_KEY
    <PROVIDER>_BASE_URL  — ví dụ OMNIROUTE_BASE_URL, OPENROUTER_BASE_URL
    <PROVIDER>_MODEL     — model riêng cho provider (tuỳ chọn)
    DEFAULT_PROVIDER     — provider mặc định
    DEFAULT_MODEL        — model mặc định khi provider không có <P>_MODEL

Hỗ trợ provider: openai, openrouter, omniroute, gemini (OpenAI-compatible
endpoint). Anthropic chưa có module/provider tương ứng trong repo.

Cách dùng:
    .venv/bin/python codebase/src/evaluation/run_cases.py \
        --provider omniroute \
        --prompt-file codebase/src/prompting/system_prompt.md \
        --prompt-version v1.0 \
        --tag run_001_baseline \
        --model kiro/deepseek-3.2

Nếu muốn ghi đè key/base URL qua terminal:
    --api-key sk-... --base-url https://...

Mỗi case trong golden_set/*.json được gọi một lượt; kết quả ghi ra
eval/results/cases/<tag>_<case_id>.json. Aggregate run tổng hợp do
score_runs.py tạo lại khi chạy.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]

# Thêm codebase/src vào path để import env (đọc .env, lấy API key).
SRC = ROOT / "codebase/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from env import get_api_key  # noqa: E402  (sau khi thêm SRC vào path)

PROVIDERS = ("openai", "openrouter", "omniroute", "gemini")

# Model mặc định nếu không có --model, <P>_MODEL hay DEFAULT_MODEL.
MODEL_DEFAULTS = {
    "openai": "gpt-5-nano",
    "openrouter": "openai/gpt-4o-mini",
    "omniroute": "kiro/deepseek-3.2",
    "gemini": "gemini-2.0-flash",
}

# Base URL mặc định nếu không có --base-url hay <P>_BASE_URL.
# None = dùng mặc định của OpenAI SDK (api.openai.com).
BASE_URL_DEFAULTS = {
    "openai": None,
    "openrouter": "https://openrouter.ai/api/v1",
    "omniroute": None,  # bắt buộc từ OMNIROUTE_BASE_URL — ví dụ local router
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
}


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
    while data.startswith("```"):
        newline = data.find("\n")
        data = (data[newline + 1:] if newline != -1 else data[3:]).strip()
    for _ in range(3):
        data = data.strip()
        if data.endswith("```"):
            data = data[:-3].rstrip()
    start, end = data.find("{"), data.rfind("}")
    if start != -1 and end != -1 and end > start:
        data = data[start:end + 1]
    return data


def resolve_config(args):
    """Trả về (provider, api_key, base_url, model) theo CLI > .env > default."""
    provider = (args.provider or os.environ.get("DEFAULT_PROVIDER")
                or "openai").lower()
    if provider not in PROVIDERS:
        raise SystemExit(
            f"Provider không hỗ trợ: {provider!r}. Chọn trong: {', '.join(PROVIDERS)}")

    api_key = args.api_key or get_api_key(provider)
    if not api_key:
        raise SystemExit(
            f"Thiếu API key cho provider {provider}: đặt {provider.upper()}_API_KEY "
            "trong .env hoặc truyền --api-key.")

    base_url = (args.base_url or os.environ.get(f"{provider.upper()}_BASE_URL")
                or BASE_URL_DEFAULTS.get(provider))
    if provider == "omniroute" and not base_url:
        raise SystemExit(
            "Thiếu OMNIROUTE_BASE_URL trong .env/môi trường hoặc --base-url "
            "(ví dụ local router OpenAI-compatible).")

    model = (args.model or os.environ.get(f"{provider.upper()}_MODEL")
             or os.environ.get("DEFAULT_MODEL")
             or MODEL_DEFAULTS[provider])
    return provider, api_key, base_url, model


def run_case(client, payload: dict, system_prompt: str, model: str):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0.3,
        max_tokens=6000,
        timeout=300.0,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Chạy golden-set cases qua provider chọn (--provider hoặc "
                    "DEFAULT_PROVIDER trong .env).")
    parser.add_argument("--provider", choices=list(PROVIDERS),
                        default=None,
                        help="Tên provider; mặc định lấy DEFAULT_PROVIDER trong .env")
    parser.add_argument("--model", default=None,
                        help="Model; mặc định <PROVIDER>_MODEL / DEFAULT_MODEL")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--prompt-version", default="v1.0")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--base-url", default=None,
                        help="Ghi đè base URL (mặc định <PROVIDER>_BASE_URL)")
    parser.add_argument("--api-key", default=None,
                        help="Ghi đè API key (mặc định <PROVIDER>_API_KEY)")
    parser.add_argument("--golden-dir", default="eval/golden_set")
    parser.add_argument("--only", default=None,
                        help="Chỉ chạy case này (tên file không đuôi .json)")
    args = parser.parse_args()

    provider, api_key, base_url, model = resolve_config(args)
    system_prompt = load_system_prompt(ROOT / args.prompt_file)

    client_kwargs = {"api_key": api_key, "timeout": 330.0, "max_retries": 0}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    case_paths = sorted((ROOT / args.golden_dir).glob("*.json"))
    if args.only:
        case_paths = [p for p in case_paths if p.stem == args.only]

    out_dir = ROOT / "eval/results/cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Provider: {provider} | model: {model} | base_url: {base_url or '(mặc định)'}",
          flush=True)

    for path in case_paths:
        case_id = path.stem
        out_path = out_dir / f"{args.tag}_{case_id}.json"

        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict) or "task" not in payload:
            print(f"  {case_id}: bỏ qua (không phải case golden set)", flush=True)
            continue
        result = {
            "test_id": case_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "requested_model": model,
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
            response = run_case(client, payload, system_prompt, model)
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