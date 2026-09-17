"""Thử nghiệm Noise Resistance: chạy tuned prompt trên input đã dedup.

Cases có lượt hỏi lặp: edge_002 (3 lượt "Context window là gì?" giống hệt),
miss_002 (2 câu giống hệt nhau). So sánh ranking cluster trước/sau dedup
bằng Spearman rho trên thứ tự rank + unique_students + question_count.

Output: eval/results/cases/run_003_dedup_<case>.json
        eval/results/dedup_experiment.json
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = os.environ.get("OMNIROUTE_BASE_URL")
if not BASE_URL:
    raise SystemExit("Thiếu OMNIROUTE_BASE_URL trong môi trường.")
API_KEY = os.environ.get("OMNIROUTE_API_KEY")
if not API_KEY:
    raise SystemExit("Thiếu OMNIROUTE_API_KEY trong môi trường.")
MODEL = os.environ.get("OMNIROUTE_MODEL", "kiro/deepseek-3.2")
PROMPT_FILE = ROOT / "codebase/src/prompting/system_prompt_v1_1.md"


def load_system_prompt(path):
    content = path.read_text(encoding="utf-8-sig")
    lines, inside = [], False
    for line in content.splitlines():
        if not inside:
            if line.strip() == "```text":
                inside = True
            continue
        if line.strip() == "```":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def extract_json(text):
    data = text.strip()
    if data.startswith("```"):
        nl = data.find("\n")
        data = (data[nl + 1:] if nl != -1 else data[3:]).strip()
    while data.startswith("```"):
        nl = data.find("\n")
        data = (data[nl + 1:] if nl != -1 else data[3:]).strip()
    for _ in range(3):
        data = data.strip()
        if data.endswith("```"):
            data = data[:-3].rstrip()
    s, e = data.find("{"), data.rfind("}")
    if s != -1 and e != -1 and e > s:
        data = data[s:e + 1]
    return data


def dedup_questions(payload):
    """Bỏ các lượt hỏi trùng (cùng student + cùng văn bản), giữ lượt đầu."""
    payload = dict(payload)
    seen, kept = set(), []
    for q in payload.get("questions", []):
        key = (q.get("student"), (q.get("student_question") or "").strip())
        if key in seen:
            continue
        seen.add(key)
        kept.append(q)
    payload["questions"] = kept
    return payload


def spearman_rank(values):
    """Rank tăng dần (xử lý bằng hạng trung bình). values: list số."""
    import math
    ranked = [0] * len(values)
    order = sorted(range(len(values)), key=lambda i: values[i])
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranked[order[k]] = avg
        i = j + 1
    return ranked


def spearman(a, b):
    n = len(a)
    if n < 2:
        return 1.0 if a == b else 0.0
    ra, rb = spearman_rank(a), spearman_rank(b)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    sa = (sum((x - ma) ** 2 for x in ra) ** 0.5)
    sb = (sum((y - mb) ** 2 for y in rb) ** 0.5)
    if sa == 0 or sb == 0:
        return 1.0 if ra == rb else 0.0
    return cov / (sa * sb)


def main():
    system_prompt = load_system_prompt(PROMPT_FILE)
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=330.0,
                    max_retries=0)
    cases = ["edge_002", "miss_002"]
    out_dir = ROOT / "eval/results/cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    experiment = {"provider": "omniroute", "model": MODEL,
                  "prompt_version": "v1.1",
                  "method": "Spearman rho giữa ranking cluster raw và dedup",
                  "cases": {}}
    for cid in cases:
        payload = json.loads(
            (ROOT / f"eval/golden_set/{cid}.json").read_text(
                encoding="utf-8-sig"))
        deduped = dedup_questions(payload)
        result = {
            "test_id": cid, "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "omniroute", "requested_model": MODEL,
            "prompt_version": "v1.1-dedup",
            "prompt_file": str(PROMPT_FILE.relative_to(ROOT)),
            "input": deduped,
            "status": "NEEDS_REVIEW", "passed": None, "reason": "",
        }
        started = time.perf_counter()
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user",
                       "content": json.dumps(deduped, ensure_ascii=False)}],
            temperature=0.3, max_tokens=6000, timeout=300.0)
        out = resp.choices[0].message.content or ""
        result["actual_output"] = out
        result["actual_model"] = resp.model
        result["response_status"] = resp.choices[0].finish_reason
        result["usage"] = resp.usage.model_dump() if resp.usage else None
        result["latency_ms"] = round((time.perf_counter() - started) * 1000)
        try:
            result["parsed_output"] = json.loads(extract_json(out))
            result["status"] = "NEEDS_REVIEW"
        except Exception as exc:
            result["status"] = "FAIL"
            result["passed"] = False
            result["reason"] = f"JSON lỗi: {type(exc).__name__}"
            result["parsed_output"] = None
        (out_dir / f"run_003_dedup_{cid}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        # Tính Spearman với bản tuned gốc
        orig = json.loads((out_dir / f"run_002_tuned_{cid}.json").read_text(
            encoding="utf-8-sig"))
        def rank_vec(o):
            clusters = (o.get("parsed_output") or {}).get("clusters") or []
            rows = sorted(
                ((c.get("rank", i + 1), c.get("unique_students", 0),
                  c.get("question_count", 0), (c.get("concept") or ""))
                 for i, c in enumerate(clusters)),
                key=lambda r: (r[0], -r[1], -r[2]))
            return [r[0] for r in rows], [r[1] for r in rows], \
                   [r[2] for r in rows], [r[3] for r in rows]

        rr, ru, rq, rc = rank_vec(orig)
        dr, du, dq, dc = rank_vec(result)
        experiment["cases"][cid] = {
            "orig_clusters": [
                {"rank": a, "unique_students": b, "question_count": c,
                 "concept": d} for a, b, c, d in zip(rr, ru, rq, rc)],
            "dedup_clusters": [
                {"rank": a, "unique_students": b, "question_count": c,
                 "concept": d} for a, b, c, d in zip(dr, du, dq, dc)],
            "rho_rank": round(spearman(rr, dr), 4),
            "rho_unique_students": round(spearman(ru, du), 4),
            "rho_question_count": round(spearman(rq, dq), 4),
            "concepts_unchanged": rc == dc,
        }
        print(cid, "->", experiment["cases"][cid])

    rho_list = [v["rho_rank"] for v in experiment["cases"].values()]
    experiment["avg_rho_rank"] = round(sum(rho_list) / len(rho_list), 4)
    out = ROOT / "eval/results/dedup_experiment.json"
    out.write_text(json.dumps(experiment, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print("DA LUU:", out, "| avg rho_rank =", experiment["avg_rho_rank"])


if __name__ == "__main__":
    main()