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

from prompting.prompts import SYSTEM_PROMPT  # noqa: E402  (bản đang giữ — v1.2)
from tools.engine import (  # noqa: E402
    get_engine_config, call_llm_with_tools,
)

DATA_DIR = ROOT / "codebase/data/vlearn-pack"
CSV_PATH = DATA_DIR / "chatlog/tutor_turns.csv"
TRANS_DIR = DATA_DIR / "transcript"
UI_DIR = Path(__file__).resolve().parent

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
# Cấu hình provider/client + vòng lặp function calling nằm ở tools/engine.py;
# ở đây chỉ giữ extract_json dùng chung cho analyze/card.


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
    start = data.find("{")
    if start == -1:
        raise ValueError("Không tìm thấy dấu { trong output của model")
    # Quét cặp ngoặc cân bằng (bỏ qua ngoặc trong chuỗi) để không nuốt prose phía sau.
    depth, in_str, esc, end = 0, False, False, None
    for i in range(start, len(data)):
        ch = data[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ValueError("JSON không đóng ngoặc đúng cách trong output của model")
    return json.loads(data[start:end + 1])


# ---------------- dữ liệu ----------------

_dataset = None
_dataset_lock = threading.Lock()


def dataset():
    """Một lần đọc toàn bộ tutor_turns.csv (13.494 dòng)."""
    global _dataset
    with _dataset_lock:
        if _dataset is None:
            with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
                _dataset = list(csv.DictReader(f))
    return _dataset


def _is_preset(row):
    return (row.get("is_preset") or "").strip().lower() == "true"


def _asked(row):
    raw = (row.get("asked_at_vn") or "").strip()
    try:
        return datetime.strptime(raw[:16], "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def build_meta():
    """Thông tin để dựng giao diện: cohort/lecture/time range/học liệu."""
    rows = dataset()

    cohorts = {}
    lectures = {}
    for r in rows:
        c = (r.get("cohort_hint") or "").strip() or "(trống)"
        cohorts.setdefault(c, {"rows": 0, "students": set()})
        cohorts[c]["rows"] += 1
        if r.get("student"):
            cohorts[c]["students"].add(r["student"])
        key = (r.get("cohort_hint") or "").strip(), \
              (r.get("lecture_code") or "").strip(), \
              (r.get("lecture_title") or "").strip()
        lectures.setdefault(key, 0)
        lectures[key] += 1

    date_min, date_max, k4_min, k4_max = None, None, None, None
    for r in rows:
        d = _asked(r)
        if d is None:
            continue
        if date_min is None or d < date_min:
            date_min = d
        if date_max is None or d > date_max:
            date_max = d
        if (r.get("cohort_hint") or "").strip() == "K4":
            if k4_min is None or d < k4_min:
                k4_min = d
            if k4_max is None or d > k4_max:
                k4_max = d

    transcripts = []
    for path in sorted(TRANS_DIR.glob("transcript-*-clean.md")):
        segs = parse_transcript(path)
        title = next((ln.strip("# ") for ln in path.read_text(
            encoding="utf-8-sig").splitlines() if ln.strip().startswith("# ")),
            path.stem)
        transcripts.append({
            "id": path.name,
            "title": title or path.stem,
            "segments": len(segs),
            "chars": sum(len(s["content"]) for s in segs),
            "first": segs[0]["source_id"] if segs else "",
            "last": segs[-1]["source_id"] if segs else "",
        })

    lec_list = sorted(
        ({"cohort": k[0], "code": k[1], "title": k[2], "rows": n}
         for k, n in lectures.items()),
        key=lambda x: (x["cohort"], x["code"], x["title"]))

    return {
        "cohorts": [
            {"cohort": c, "rows": v["rows"], "students": len(v["students"])}
            for c, v in sorted(cohorts.items(), key=lambda kv: -kv[1]["rows"])
        ],
        "lectures": lec_list,
        "date_min": date_min.strftime("%Y-%m-%d") if date_min else "",
        "date_max": date_max.strftime("%Y-%m-%d") if date_max else "",
        "k4_start": k4_min.strftime("%Y-%m-%d") if k4_min else "",
        "k4_end": k4_max.strftime("%Y-%m-%d") if k4_max else "",
        "transcripts": transcripts,
        "default_char_budget": DEFAULT_CHAR_BUDGET,
        "max_char_budget": MAX_CHAR_BUDGET,
        "default_sample_size": DEFAULT_SAMPLE_SIZE,
        "max_sample_size": MAX_SAMPLE_SIZE,
    }


_transcripts_cache = {}


def parse_transcript(path: Path) -> list[dict]:
    """Tách transcript thành các đoạn [Txx-NNN], nội dung đã strip."""
    key = str(path)
    if key not in _transcripts_cache:
        segs, cur = [], None
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.rstrip()
            m = SEG_RE.match(line)
            if m:
                if cur and cur["content"]:
                    segs.append(cur)
                cur = {"source_id": f"[{m.group(1)}]", "source_type": "transcript",
                       "content": m.group(2).strip()}
            elif cur is not None:
                extra = line.strip()
                if extra:
                    cur["content"] = (cur["content"] + " " + extra).strip()
        if cur and cur["content"]:
            segs.append(cur)
        _transcripts_cache[key] = segs
    return _transcripts_cache[key]


def select_materials(ids, budget):
    """Chọn đoạn transcript sao cho tổng budget chia theo tỷ lệ từng file.

    Trả về (segments, chars) — segments theo thứ tự file, cắt phần đầu mỗi file.
    """
    budget = max(1_000, min(int(budget or DEFAULT_CHAR_BUDGET), MAX_CHAR_BUDGET))
    chosen = []
    total = 0
    sizes = {}
    for tid in ids:
        segs = parse_transcript(TRANS_DIR / tid)
        sizes[tid] = sum(len(s["content"]) for s in segs)
        total += sizes[tid]
    if total == 0:
        return [], 0
    used_total = 0
    for tid in ids:
        segs = parse_transcript(TRANS_DIR / tid)
        alloc = int(budget * sizes[tid] / total)
        used = 0
        taken = 0
        for s in segs:
            if taken > 0 and used + len(s["content"]) > alloc:
                break
            chosen.append(s)
            used += len(s["content"])
            taken += 1
        used_total += used
    return chosen, used_total


def filter_questions(cohort, code, title, time_mode):
    """Lọc câu hỏi theo scope (khoá / bài giảng / thời gian) — KHÔNG lọc preset.

    Preset/rỗng/dedupe giờ do tool `preprocess_questions` của model xử lý.
    Trả về list row đã sắp theo thời gian (mới nhất cuối).
    """
    rows = dataset()
    date_min, date_max = None, None
    now_max = None
    for r in rows:
        d = _asked(r)
        if d is None:
            continue
        now_max = d if now_max is None or d > now_max else now_max
    if time_mode == "last7" and now_max is not None:
        date_min, date_max = now_max - timedelta(days=7), now_max
    elif time_mode == "k4":
        date_min, date_max = now_max - timedelta(days=7), now_max if now_max else None
    else:
        date_min, date_max = None, None

    scoped = []
    for r in rows:
        if cohort and (r.get("cohort_hint") or "").strip() != cohort:
            continue
        if code and (r.get("lecture_code") or "").strip() != code:
            continue
        if title and (r.get("lecture_title") or "").strip() != title:
            continue
        d = _asked(r)
        if date_min is not None and (d is None or d < date_min):
            continue
        if date_max is not None and (d is None or d > date_max):
            continue
        scoped.append(r)
    scoped.sort(key=lambda r: (r.get("asked_at_vn") or ""))
    return scoped


def _to_question_row(r):
    """Chuyển 1 dòng CSV thành object câu hỏi cho payload (giữ is_preset)."""
    return {
        "student": (r.get("student") or "").strip() or None,
        "is_preset": _is_preset(r),
        "asked_at_vn": (r.get("asked_at_vn") or "").strip()[:16],
        "student_question": (r.get("student_question") or "").strip(),
    }


def trace_tools_used(trace):
    """Tên tool đã chạy, theo thứ tự xuất hiện, không trùng lặp."""
    seen, out = set(), []
    for t in trace or []:
        name = t.get("tool") or ""
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def scope_label(cohort, code, title, time_mode):
    parts = []
    parts.append(cohort or "Tất cả khoá")
    parts.append(f"{code} — {title}" if code and title else (title or code or "Tất cả bài"))
    if time_mode == "last7":
        parts.append("7 ngày gần nhất")
    elif time_mode == "k4":
        parts.append("Khoá K4 (tuần gần nhất)")
    else:
        parts.append("Toàn bộ thời gian")
    return " · ".join(parts)


def build_analyze(req) -> dict:
    cohort = (req.get("cohort") or "").strip()
    code = (req.get("lecture_code") or "").strip()
    title = (req.get("lecture_title") or "").strip()
    time_mode = (req.get("time_range") or "all").strip()
    transcripts = [t for t in (req.get("transcripts") or []) if t]
    budget = int(req.get("char_budget") or DEFAULT_CHAR_BUDGET)
    sample = int(req.get("sample_size") or DEFAULT_SAMPLE_SIZE)
    sample = max(1, min(sample, MAX_SAMPLE_SIZE))

    if not transcripts:
        return {"ok": False, "error": "Chưa chọn nguồn học liệu nào."}

    scoped = filter_questions(cohort, code, title, time_mode)
    materials, chars = select_materials(transcripts, budget)
    sent_rows = scoped[-sample:]
    sent = [_to_question_row(r) for r in sent_rows]

    if not sent:
        return {
            "ok": True,
            "status": "no_valid_questions",
            "data": {
                "scope_rows": len(scoped),
                "sent": 0,
                "materials_segments": len(materials),
                "materials_chars": chars,
                "tools_used": [],
            },
            "output": None,
        }

    payload = {
        "task": "analyze_clusters",
        "scope": {
            "cohort": cohort,
            "lecture": f"{code} — {title}".strip(" —") if (code or title) else "",
            "time_range": scope_label(cohort, code, title, time_mode),
        },
        "questions": sent,
        "materials": materials,
        "teacher_confirmed_source": False,
    }

    raw, trace, err = call_llm(payload)
    if err:
        return {"ok": False, "error": f"Lỗi gọi model: {err}"}
    try:
        parsed = extract_json(raw)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False,
                "error": f"Output không phải JSON hợp lệ: {type(exc).__name__}: {exc}",
                "preview": raw[:300]}

    return {
        "ok": True,
        "status": parsed.get("status", ""),
        "output": parsed,
        "data": {
            "scope_rows": len(scoped),
            "sent": len(sent),
            "preset_in_sent": sum(1 for q in sent if q["is_preset"]),
            "materials_segments": len(materials),
            "materials_chars": chars,
            "tools_used": trace_tools_used(trace),
        },
    }


def build_card(req) -> dict:
    cluster = req.get("cluster") or {}
    transcripts = [t for t in (req.get("transcripts") or []) if t]
    budget = int(req.get("char_budget") or DEFAULT_CHAR_BUDGET)
    scope = req.get("scope") or {}

    if not transcripts:
        return {"ok": False, "error": "Chưa xác nhận nguồn học liệu cho thẻ."}
    if not (cluster.get("concept") or "").strip():
        return {"ok": False, "error": "Thiếu tên nội dung để tạo thẻ."}

    materials, chars = select_materials(transcripts, budget)
    visible = {s["source_id"] for s in materials}
    citations = [c for c in (cluster.get("citations") or []) if c in visible] \
        or [c for c in (cluster.get("citations") or [])]

    selected_cluster = {
        "cluster_id": "manual",
        "concept": (cluster.get("concept") or "").strip(),
        "unique_students": cluster.get("unique_students") or 0,
        "question_count": cluster.get("question_count") or 1,
        "example_questions": (cluster.get("example_questions") or [])[:2],
        "citations": citations,
    }

    payload = {
        "task": "review_card",
        "scope": {"cohort": scope.get("cohort", ""),
                  "lecture": scope.get("lecture", ""),
                  "time_range": scope.get("time_range", "")},
        "questions": [],
        "materials": materials,
        "selected_cluster": selected_cluster,
        "teacher_confirmed_source": True,
    }

    raw, trace, err = call_llm(payload)
    if err:
        return {"ok": False, "error": f"Lỗi gọi model: {err}"}
    try:
        parsed = extract_json(raw)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False,
                "error": f"Output không phải JSON hợp lệ: {type(exc).__name__}: {exc}",
                "preview": raw[:300]}

    return {
        "ok": True,
        "status": parsed.get("status", ""),
        "output": parsed,
        "data": {"materials_segments": len(materials), "materials_chars": chars,
                 "tools_used": trace_tools_used(trace)},
    }


# ---------------- HTTP ----------------

INDEX_HTML = UI_DIR / "index.html"


class Handler(BaseHTTPRequestHandler):
    server_version = "VLearnPulse/1.0"

    def log_message(self, fmt, *args):
        print(f"[ui] {self.address_string()} {fmt % args}", flush=True)

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8"))

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:  # noqa: BLE001
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            try:
                body = INDEX_HTML.read_bytes()
            except FileNotFoundError:
                self._send(500, b"index.html khong tim thay", "text/plain; charset=utf-8")
                return
            self._send(200, body, "text/html; charset=utf-8")
        elif path == "/api/health":
            self._json(200, {
                "ok": True,
                "provider": PROVIDER,
                "model": MODEL,
                "has_key": HAS_KEY,
            })
        elif path == "/api/meta":
            self._json(200, {"ok": True, "meta": build_meta()})
        else:
            self._json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        req = self._read_json()
        if path == "/api/analyze":
            self._json(200, build_analyze(req))
        elif path == "/api/card":
            self._json(200, build_card(req))
        else:
            self._json(404, {"ok": False, "error": "Not found"})


def main():
    parser = argparse.ArgumentParser(description="VLearn Pulse functional web UI.")
    parser.add_argument("--host", default=None, help="UI_HOST (mặc định 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="UI_PORT (mặc định 8701)")
    parser.add_argument("--no-browser", action="store_true",
                        help="Không tự mở trình duyệt")
    args = parser.parse_args()

    import os
    host = args.host or os.environ.get("UI_HOST") or "127.0.0.1"
    port = args.port or int(os.environ.get("UI_PORT") or 8701)

    if not CSV_PATH.exists():
        print("THIEU data pack:", CSV_PATH)
        return
    meta = build_meta()
    print("VLearn Pulse UI")
    print("  data   :", CSV_PATH.name, f"({sum(1 for _ in dataset())} dong)")
    print("  prompt :", SYSTEM_PROMPT[:60].replace("\n", " ") or "(doc tu codebase/src/prompting/system_prompt.md)")
    print("  provider:", PROVIDER, "| model:", MODEL,
          "| key:", "co" if HAS_KEY else "THIEU",
          "| tools: preprocess_questions, cluster_questions, ground_clusters")
    print("  meta   :", len(meta["cohorts"]), "cohort,",
          sum(1 for c in meta["cohorts"] if c["cohort"]) , "khoa, ",
          len(meta["lectures"]), "bai giang,", len(meta["transcripts"]), "transcript")
    if not HAS_KEY:
        print("  CANH BAO: thieu API key — /api/analyze va /api/card se loi.")
    print("  URL    : http://%s:%d/" % (host, port))

    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDung server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()