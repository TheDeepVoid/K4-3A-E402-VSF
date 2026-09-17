"""Selftest: kiểm thử function calling với API thật (OmniRoute local).

Chạy:
    .venv/bin/python codebase/src/tools/selftest.py

Sẽ gọi model với tools, dùng ~60 câu thật từ K4 D01 (Day01) + 1 transcript,
in ra trace function calling và output cuối. Không in câu hỏi học viên ra màn
hình (chỉ số liệu).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "codebase/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prompting.prompts import SYSTEM_PROMPT  # noqa: E402
from tools.engine import call_llm_with_tools, get_engine_config  # noqa: E402
from tools.registry import execute_tool  # noqa: E402
from ui.app import dataset, extract_json, select_materials  # noqa: E402
from preprocessing.preprocess import is_preset_question  # noqa: E402


def load_sample() -> dict:
    rows = [r for r in dataset()
            if (r.get("cohort_hint") or "").strip() == "K4"
            and r.get("lecture_code") == "D01"
            and (r.get("lecture_title") or "").strip() == "Day01"]
    rows.sort(key=lambda r: (r.get("asked_at_vn") or ""))
    scope_rows = [
        {
            "student": (r.get("student") or "").strip() or None,
            "is_preset": is_preset_question(r.get("student_question"),
                                            bool((r.get("is_preset") or "").strip().lower() == "true")),
            "asked_at_vn": (r.get("asked_at_vn") or "").strip()[:16],
            "student_question": (r.get("student_question") or "").strip(),
        }
        for r in rows[-60:]
    ]
    materials, chars = select_materials(["transcript-04-clean.md"], 30000)
    return {"questions": scope_rows, "materials": materials, "chars": chars}


def main():
    cfg = get_engine_config()
    print(f"provider={cfg['provider']} model={cfg['model']} key={'CÓ' if cfg['api_key'] else 'THIẾU'}")

    if not cfg["api_key"]:
        print("Thiếu API key — không thể test. Kiểm tra .env.")
        return

    sample = load_sample()
    presets = sum(1 for q in sample["questions"] if q["is_preset"])
    print(f"mẫu: {len(sample['questions'])} câu (gồm {presets} preset) · "
          f"materials {sample['chars']:,} ký tự — chỉ in số liệu, không in câu hỏi.")

    # 1) Test 3 tool trực tiếp (deterministic).
    pp = execute_tool("preprocess_questions", {"questions": sample["questions"]})
    valid = pp["result"]["valid_questions"]
    print(f"\n[direct] preprocess: {pp['result']['valid_question_count']} hợp lệ / "
          f"{pp['result']['excluded_preset_count']} preset / "
          f"{pp['result']['excluded_empty_count']} rỗng / "
          f"{pp['result']['dedupe_removed_count']} trùng")
    cl = execute_tool("cluster_questions", {"questions": valid})
    clusters = cl["result"]["clusters"]
    print(f"[direct] cluster: {len(clusters)} cụm, unassigned={cl['result']['unassigned_count']}")
    for c in clusters[:3]:
        print(f"         {c['cluster_id']} {c['concept'][:48]!r} q={c['question_count']} st={c['unique_students']}")
    gr = execute_tool("ground_clusters",
                      {"clusters": clusters, "materials": sample["materials"], "top_k": 2})
    ok = sum(1 for g in gr["result"]["groundings"] if g["grounded"])
    print(f"[direct] ground: {ok}/{len(gr['result']['groundings'])} cụm có nguồn")

    # 2) Test vòng lặp function calling với model thật.
    payload = {
        "task": "analyze_clusters",
        "scope": {"cohort": "K4", "lecture": "D01 — Day01",
                  "time_range": "Toàn bộ dữ liệu K4"},
        "questions": sample["questions"],
        "materials": sample["materials"],
        "teacher_confirmed_source": False,
    }
    print("\n[model] gọi function calling... (có thể mất 15–60s)")
    text, trace, err = call_llm_with_tools(payload, SYSTEM_PROMPT)
    if err:
        print("LỖI:", err)
        return
    print(f"[model] trace có {len(trace)} tool call:")
    for t in trace:
        print(f"        - {t['tool']:<22} injected={t['injected']} ok={t['ok']} args={t['args_keys']}")

    try:
        parsed = extract_json(text)
        summary = parsed.get("summary") or {}
        print(f"[model] status={parsed.get('status')} · summary={json.dumps(summary, ensure_ascii=False)}")
        print(f"[model] clusters={len(parsed.get('clusters') or [])} "
              f"(duyệt tối đa 3):")
        for c in (parsed.get("clusters") or [])[:3]:
            print(f"         - {c.get('concept', '')[:52]!r} st={c.get('unique_students')} "
                  f"q={c.get('question_count')} grounding={c.get('grounding_status')} "
                  f"cites={len(c.get('citations') or [])}")
        print(f"[model] warnings={parsed.get('warnings')}")
    except Exception as exc:  # noqa: BLE001
        print("Không parse được output cuối:", exc)
        print(text[:500])


if __name__ == "__main__":
    main()