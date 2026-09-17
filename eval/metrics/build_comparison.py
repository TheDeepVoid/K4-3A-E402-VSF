import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "eval/results"

def load_runs(pattern):
    runs = {}
    for path in sorted(RESULTS.glob(pattern)):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        case_id = data["test_id"]
        if case_id in runs:
            raise ValueError(f"Trùng case: {case_id}")
        runs[case_id] = data
    return runs

baseline = load_runs("run_001_baseline*.json")
tuned = load_runs("run_002_tuned_*.json")
rows = []

for case_id, old in sorted(baseline.items()):
    new = tuned.get(case_id)

    if old["status"] == "BLOCKED" and new is None:
        new_status = "NOT_RUN"
        change = "BLOCKED"
        same_input = ""
        same_model = ""
        new_reason = "Chưa chạy: chức năng gộp cụm chưa có."
    else:
        if new is None:
            raise ValueError(f"Thiếu kết quả tuned: {case_id}")

        if old["status"] not in {"PASS", "FAIL"}:
            raise ValueError(f"Baseline chưa chấm xong: {case_id}")
        if new["status"] not in {"PASS", "FAIL"}:
            raise ValueError(f"Tuned chưa chấm xong: {case_id}")

        same_input = old["input"] == new["input"]
        same_model = old["actual_model"] == new["actual_model"]
        if not same_input or not same_model:
            raise ValueError(f"Khác input hoặc model: {case_id}")

        new_status = new["status"]
        new_reason = new["reason"]

        if old["status"] == "FAIL" and new_status == "PASS":
            change = "IMPROVED"
        elif old["status"] == "PASS" and new_status == "FAIL":
            change = "REGRESSED"
        else:
            change = "UNCHANGED"

    rows.append({
        "case_id": case_id,
        "baseline_status": old["status"],
        "tuned_status": new_status,
        "change": change,
        "same_input": same_input,
        "same_model": same_model,
        "baseline_reason": old.get("reason", ""),
        "tuned_reason": new_reason,
    })

output = RESULTS / "comparison.csv"
with output.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print("DA LUU:", output)
print("SO CASE:", len(rows))
print("SO SANH:", dict(Counter(row["change"] for row in rows)))