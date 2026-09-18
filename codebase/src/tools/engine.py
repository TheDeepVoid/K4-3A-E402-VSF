"""Engine function calling: gắn tool vào model và vòng lặp gọi-chạy-trả kết quả.

Luồng:
  1. Gọi chat.completions với `tools=TOOL_SCHEMAS`, tool_choice="auto".
  2. Nếu model trả tool_calls → chạy từng tool (registry), đưa kết quả về qua
     message role="tool", gọi tiếp.
  3. Nếu vòng đầu model KHÔNG tự gọi tool (model/route không hỗ trợ function
     calling ổn định), `auto_run_pipeline` sẽ tự "inject" chuỗi tool hợp lệ
     (preprocess → cluster → ground) dưới dạng tool_calls thật và trả kết quả
     deterministic cho model. Nhờ vậy 3 tool LUÔN được dùng, model chỉ xử lý
     phần phán đoán/tổng hợp cuối cùng.
"""

import json
import os
import re
import threading
import time

from openai import OpenAI

from env import get_api_key
from tools.registry import TOOL_SCHEMAS, execute_tool

PROVIDERS = ("openai", "openrouter", "omniroute", "gemini")
MODEL_DEFAULTS = {
    "openai": "gpt-5-nano",
    "openrouter": "openai/gpt-4o-mini",
    "omniroute": "kiro/deepseek-3.2",
    "gemini": "gemini-2.0-flash",
}
BASE_URL_DEFAULTS = {
    "openai": None,
    "openrouter": "https://openrouter.ai/api/v1",
    "omniroute": None,  # lấy từ <PROVIDER>_BASE_URL — ví dụ local router
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
}

TOOLS_SYSTEM_HINT = """\
Công cụ có sẵn (function calling): thay vì tự gom nhóm / đếm / đoán nguồn trong \
đầu, hãy gọi các tool để có dữ liệu chính xác:
- preprocess_questions(questions): lọc is_preset + câu rỗng, chuẩn hoá, dedupe \
theo học viên → trả valid_questions và các bộ đếm.
- cluster_questions(questions): gom câu (đã chuẩn hoá) thành cụm chủ đề thô \
(Jaccard trên từ khoá) → trả clusters + unassigned.
- ground_clusters(clusters, materials): tìm đoạn [Txx-NNN] khớp từ khoá từng cụm \
(tf-idf) → trả matches kèm score + snippet.
Quy trình khuyến nghị: (1) preprocess các câu gốc, (2) cluster trên valid_questions, \
(3) ground các cụm trên materials (đừng bịa citation ngoài nguồn có thật), (4) dùng \
kết quả đó để tổng hợp output cuối đúng schema. Kết quả tool là số liệu thật — dùng \
chúng, không thay thế bằng con số tự ước lượng."""


def resolve_config(provider: str = None, model: str = None,
                   base_url: str = None, api_key: str = None) -> dict:
    """Provider/model/key/base_url giống run_cases.py; ưu tiên omniroute (local)."""
    prov = (provider or os.environ.get("UI_PROVIDER")
            or os.environ.get("DEFAULT_PROVIDER") or "").lower()
    if prov not in PROVIDERS:
        prov = "omniroute" if get_api_key("omniroute") else "openai"
    key = api_key or get_api_key(prov)
    url = (base_url or os.environ.get(f"{prov.upper()}_BASE_URL")
           or BASE_URL_DEFAULTS.get(prov))
    mod = (model or os.environ.get(f"{prov.upper()}_MODEL")
           or os.environ.get("DEFAULT_MODEL") or MODEL_DEFAULTS.get(prov))
    return {"provider": prov, "model": mod, "api_key": key,
            "base_url": url}


_config = None
_conf_lock = threading.Lock()
_client = None
_cli_lock = threading.Lock()


def set_engine_config(config: dict) -> None:
    """Ghi đè cấu hình engine (dùng khi UI/CLI chỉ định provider/model)."""
    global _config, _client
    with _conf_lock, _cli_lock:
        _config = dict(config)
        _client = None


def get_engine_config() -> dict:
    global _config
    with _conf_lock:
        if _config is None:
            _config = resolve_config()
        return _config


def get_client() -> OpenAI:
    global _client
    with _cli_lock:
        if _client is None:
            cfg = get_engine_config()
            kwargs = {"api_key": cfg["api_key"], "timeout": 330.0, "max_retries": 0}
            if cfg.get("base_url"):
                kwargs["base_url"] = cfg["base_url"]
            _client = OpenAI(**kwargs)
        return _client


def _prep_step(call_id: str, name: str, args: dict) -> dict:
    return {"id": call_id, "name": name, "args": args, "result": None}


# ---------------- content-xml function calling (DeepSeek/ApiMoose style) ----------------
# Một số route/version trả function call dạng XML *trong content* thay vì field
# tool_calls chuẩn, nhất là khi nội dung có đoạn văn dẫn trước <function_calls>.
# Engine tự giải nén để model vẫn dùng được tools.

_INVOKE_RE = re.compile(r"<invoke\s+name=\"([^\"]+)\">(.*?)</invoke>", re.S)
_PARAM_RE = re.compile(
    r"<(?:parameter|argument|list)\s+name=\"([^\"]+)\""
    r"(?:\s+type=\"[^\"]*\")?[^>]*>(.*?)</(?:parameter|argument|list)>", re.S)
_FUNC_CALLS_BLOCK_RE = re.compile(r"<function_calls>.*?</function_calls>", re.S)


def _parse_json_arg(raw) -> object:
    raw = (raw or "").strip()
    if not raw:
        return None
    for candidate in (raw,):
        try:
            return json.loads(candidate)
        except Exception:  # noqa: BLE001
            pass
    # Một số route bọc JSON trong dấu nháy kép ở value.
    for candidate in (raw.strip('"'), raw.strip("'"),):
        try:
            return json.loads(candidate)
        except Exception:  # noqa: BLE001
            continue
    return raw  # giữ nguyên chuỗi nếu không parse được


def parse_function_calls(content) -> list:
    """Giải nén <function_calls><invoke name=...><parameter name=...>...</invoke></function_calls>.

    Trả về list {"name", "arguments"} (arguments là JSON string, đúng chuẩn).
    """
    if not content or "<function_calls" not in content:
        return []
    calls = []
    for m in _INVOKE_RE.finditer(content):
        name, body = m.group(1), m.group(2)
        args = {}
        for pm in _PARAM_RE.finditer(body):
            args[pm.group(1)] = _parse_json_arg(pm.group(2))
        calls.append({"name": name,
                      "arguments": json.dumps(args, ensure_ascii=False)})
    return calls


def strip_call_blocks(content) -> str:
    """Bỏ khối <function_calls>…</function_calls> khỏi nội dung; nếu block mở
    nhưng chưa đóng (bị cắt), cắt từ `<function_calls` đến hết."""
    out = _FUNC_CALLS_BLOCK_RE.sub("", content or "")
    idx = out.find("<function_calls")
    if idx != -1:
        out = out[:idx]
    return out.strip()


def plan_injected_pipeline(user_content) -> list:
    """Chuỗi tool tự chạy nếu model không gọi tool ở vòng đầu.

    Chạy deterministic (preprocess → cluster → ground) và nhúng sẵn kết quả để
    engine ghi các message role=tool đúng chuẩn function calling.
    """
    try:
        payload = json.loads(user_content)
    except (TypeError, ValueError):
        return []
    if not isinstance(payload, dict):
        return []

    materials = payload.get("materials") or []
    questions = payload.get("questions") or []
    steps = []

    if questions:
        st = _prep_step("call_inj_pre", "preprocess_questions", {"questions": questions})
        st["result"] = execute_tool("preprocess_questions", st["args"])
        steps.append(st)
        if not st["result"].get("ok"):
            return steps
        valid = st["result"]["result"]["valid_questions"]
        if valid:
            st2 = _prep_step("call_inj_clu", "cluster_questions",
                             {"questions": valid, "similarity_threshold": 0.40,
                              "min_cluster_size": 2})
            st2["result"] = execute_tool("cluster_questions", st2["args"])
            steps.append(st2)
            clusters = st2["result"]["result"]["clusters"] if st2["result"].get("ok") else []
        else:
            clusters = []
        if materials and clusters:
            st3 = _prep_step("call_inj_grd", "ground_clusters",
                             {"clusters": clusters, "materials": materials, "top_k": 3})
            st3["result"] = execute_tool("ground_clusters", st3["args"])
            steps.append(st3)
        return steps

    # Luồng review_card (không có questions): chỉ ground selected_cluster.
    sel = payload.get("selected_cluster") or {}
    if not materials or not sel:
        return steps
    synth = [{
        "cluster_id": "selected_cluster",
        "concept": sel.get("concept") or "",
        "top_terms": [],
        "example_questions": sel.get("example_questions") or [],
    }]
    st = _prep_step("call_inj_grd", "ground_clusters",
                    {"clusters": synth, "materials": materials, "top_k": 3})
    st["result"] = execute_tool("ground_clusters", st["args"])
    steps.append(st)
    return steps


def run_with_tools(client, *, model, system_prompt, user_content, temperature=0.3,
                   max_tokens=6000, timeout=300.0, max_steps=8,
                   auto_run_pipeline=True, preinject_pipeline=True) -> dict:
    """Vòng lặp function calling; trả {ok, content, trace, steps} hoặc {ok:false, error}."""
    debug = os.environ.get("TOOL_ENGINE_DEBUG") == "1"
    hint = system_prompt.rstrip() + "\n\n" + TOOLS_SYSTEM_HINT
    content = user_content if isinstance(user_content, str) \
        else json.dumps(user_content, ensure_ascii=False)
    messages = [{"role": "system", "content": hint},
                {"role": "user", "content": content}]
    trace = []

    preinjected = set()

    def emit_tool_round(tool_calls, via, injected):
        """Ghi assistant(tool_calls) + tool(result) vào messages và trace.
        Trả về False nếu không có tool_calls nào để xử lý."""
        if not tool_calls:
            return False
        assistant_msg = {"role": "assistant",
                         "content": strip_call_blocks(msg.content or ""),
                         "tool_calls": tool_calls}
        messages.append(assistant_msg)
        for i, tc in enumerate(tool_calls):
            call_id = tc["id"] if isinstance(tc, dict) else tc.id
            name = tc["function"]["name"] if isinstance(tc, dict) else tc.function.name
            args_raw = (tc["function"]["arguments"] if isinstance(tc, dict)
                        else tc.function.arguments)
            prev = injected.get(call_id)
            if prev is not None:
                result, injected_flag, arg_keys = prev, True, []
            else:
                injected_flag = False
                if via == "content_xml":
                    args = json.loads(parsed_xml[i]["arguments"])
                else:
                    try:
                        args = json.loads(args_raw or "{}")
                    except Exception:  # noqa: BLE001
                        args = {}
                result = execute_tool(name, args)
                arg_keys = list(args.keys())
            messages.append({"role": "tool", "tool_call_id": call_id,
                             "content": json.dumps(result, ensure_ascii=False)})
            trace.append({"call_id": call_id, "tool": name,
                          "injected": bool(injected_flag), "via": via,
                          "ok": result.get("ok"),
                          "error": result.get("error") or "",
                          "args_keys": arg_keys})
        return True

    # ---- preinject: chạy pipeline deterministic TRƯỚC create đầu tiên ----
    # Vòng model-native thường tốn 3-4 create (~3-4 phút). Cách này chạy sẵn
    # preprocess → cluster → ground, ghi thành tool_calls thật vào lịch sử, rồi
    # model chỉ cần 1 create để tổng hợp output cuối. Tools vẫn nằm trong
    # TOOL_SCHEMAS nên model có quyền gọi thêm nếu muốn.
    if preinject_pipeline:
        steps = plan_injected_pipeline(content)
        if steps:
            calls = [{"id": s["id"], "type": "function",
                      "function": {"name": s["name"],
                                   "arguments": json.dumps(s["args"], ensure_ascii=False)}}
                     for s in steps]
            assistant_msg = {"role": "assistant", "content": "",
                             "tool_calls": calls}
            messages.append(assistant_msg)
            preinjected = {s["id"] for s in steps}
            for s in steps:
                messages.append({"role": "tool", "tool_call_id": s["id"],
                                 "content": json.dumps(s["result"], ensure_ascii=False)})
                trace.append({"call_id": s["id"], "tool": s["name"],
                              "injected": True, "via": "injected_pre",
                              "ok": s["result"].get("ok"),
                              "error": s["result"].get("error") or "",
                              "args_keys": list(s["args"].keys())})

    for step_no in range(max_steps):
        t_round = time.time()
        if debug:
            print(f"[engine] round {step_no + 1}/{max_steps} — create(len(messages)={len(messages)})",
                  flush=True)
        try:
            resp = client.chat.completions.create(
                model=model, messages=messages, temperature=temperature,
                max_tokens=max_tokens, timeout=timeout,
                tools=TOOL_SCHEMAS, tool_choice="auto")
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}",
                    "content": "", "trace": trace}
        if debug:
            elapsed = round(time.time() - t_round, 1)
            print(f"[engine] round {step_no + 1} done in {elapsed}s — "
                  f"finish_reason={resp.choices[0].finish_reason} "
                  f"n_tool_calls={len(resp.choices[0].message.tool_calls or [])} "
                  f"content_len={len(resp.choices[0].message.content or '')}",
                  flush=True)
        msg = resp.choices[0].message
        tool_calls = list(msg.tool_calls or [])
        injected = {}
        via, parsed_xml = "", []

        # 1) Tool call chuẩn (field tool_calls) do router/model trả.
        # 2) Vòng sau: model có thể trả <function_calls>…</function_calls> trong
        #    content (kèm lời dẫn). Giải nén thành tool_calls thật.
        if not tool_calls and msg.content and "<function_calls" in msg.content:
            parsed_xml = parse_function_calls(msg.content)
            if parsed_xml:
                tool_calls = [
                    {"id": f"call_xml_{i}", "type": "function",
                     "function": {"name": c["name"], "arguments": c["arguments"]}}
                    for i, c in enumerate(parsed_xml)
                ]
                via = "content_xml"
        # 3) Vòng đầu model không gọi tool (và chưa preinject) → inject ngay.
        if (not tool_calls and step_no == 0 and auto_run_pipeline
                and not preinjected):
            steps = plan_injected_pipeline(content)
            if steps:
                tool_calls = [
                    {"id": s["id"], "type": "function",
                     "function": {"name": s["name"],
                                  "arguments": json.dumps(s["args"], ensure_ascii=False)}}
                    for s in steps
                ]
                injected = {s["id"]: s.get("result") for s in steps}
                via = "injected"
                preinjected = {s["id"] for s in steps}

        if not tool_calls:
            return {"ok": True, "content": strip_call_blocks(msg.content or ""),
                    "trace": trace, "steps": step_no + 1}

        # Luôn bỏ khối <function_calls> trong content (kể cả khi router đã parse
        # native tool_calls nhưng vẫn giữ block trong content) để không gửi lại
        # block cho vòng sau.
        emit_tool_round(tool_calls, via or "native", injected)

    return {"ok": False,
            "error": f"Quá {max_steps} bước function calling — dừng để tránh loop.",
            "content": "", "trace": trace}


def call_llm_with_tools(payload, system_prompt, temperature=0.3,
                        max_tokens=6000, max_steps=8,
                        preinject_pipeline=True) -> tuple:
    """Tiện ích cho UI/eval: trả (final_text, trace, error).

    preinject_pipeline=True: chạy sẵn chuỗi tool deterministic rồi mới create,
    để model tổng hợp output cuối trong 1 round (nhanh hơn đáng kể).
    """
    try:
        result = run_with_tools(
            get_client(), model=get_engine_config()["model"],
            system_prompt=system_prompt, user_content=payload,
            temperature=temperature, max_tokens=max_tokens, max_steps=max_steps,
            preinject_pipeline=preinject_pipeline)
    except Exception as exc:  # noqa: BLE001
        return "", [], f"{type(exc).__name__}: {exc}"
    if not result.get("ok"):
        return "", result.get("trace", []), result.get("error", "Lỗi function calling.")
    return result["content"], result["trace"], ""


__all__ = ["TOOL_SCHEMAS", "TOOLS_SYSTEM_HINT", "resolve_config", "get_engine_config",
           "set_engine_config", "get_client", "parse_function_calls", "strip_call_blocks",
           "plan_injected_pipeline", "run_with_tools", "call_llm_with_tools"]