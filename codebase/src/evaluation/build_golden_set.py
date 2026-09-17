"""Tạo golden_set theo layout eval/README.md từ 19 case JSON thật.

Output:
  eval/golden_set/sample_questions.csv      <- 50 câu hỏi, mỗi câu có label
  eval/golden_set/expected_clusters.json    <- cluster mong đợi theo case
  eval/golden_set/ground_truth_mapping.csv  <- liên kết câu hỏi -> nguồn đúng

Expected được gõ thủ công từ thiết kế case và luật của system prompt;
không tự sinh. Câu hỏi và mã nguồn lấy trực tiếp từ case JSON.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GOLDEN = ROOT / "eval/golden_set"

# --- Bảng expected theo case -------------------------------------------------
# cluster: (concept, question_indices, unique_students, question_count,
#           citations, grounding_status)
# status có thể là "ok" | "no_valid_questions" | "missing_scope"
EXPECTED = {
    "norm_001": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Transformer/RNN và cơ chế attention",
             "qidx": [0, 1, 2], "unique_students": 3, "question_count": 3,
             "citations": ["[T04-039]", "[T04-040]"],
             "grounding_status": "grounded"},
        ],
    },
    "norm_002": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "LLM dự đoán token và hallucination",
             "qidx": [0, 1, 2, 3], "unique_students": 2, "question_count": 4,
             "citations": ["[T04-047]", "[T04-048]"],
             "grounding_status": "grounded"},
        ],
    },
    "norm_003": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Context window",
             "qidx": [0, 1, 2], "unique_students": 3, "question_count": 3,
             "citations": ["[T04-051]"],
             "grounding_status": "grounded"},
            {"concept": "Token",
             "qidx": [3, 4, 5, 6, 7], "unique_students": 1, "question_count": 5,
             "citations": ["[T04-049]"],
             "grounding_status": "grounded"},
        ],
    },
    "norm_004": {
        "task": "review_card", "expected_status": "draft_ready",
        "teacher_confirmed_source": True,
        "concept": "Quản lý context khi làm việc với LLM",
        "sources": ["[T04-051]", "[T04-052]", "[T04-053]"],
    },
    "miss_001": {
        "task": "analyze_clusters", "expected_status": "missing_scope",
        "clusters": [],
    },
    "miss_002": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Embedding và fine-tuning",
             "qidx": [0, 1], "unique_students": 2, "question_count": 2,
             "citations": [], "grounding_status": "insufficient_evidence",
             "warnings": ["source_not_found"]},
        ],
    },
    "miss_003": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Cơ chế attention",
             "qidx": [0, 1], "unique_students": 1, "question_count": 2,
             "citations": ["[T04-040]"], "grounding_status": "grounded"},
        ],
    },
    "noans_001": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Thiết kế mạch lượng tử",
             "qidx": [0, 1, 2], "unique_students": 3, "question_count": 3,
             "citations": [], "grounding_status": "insufficient_evidence",
             "warnings": ["source_not_found"]},
        ],
    },
    "noans_002": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Context window",
             "qidx": [10, 11], "unique_students": 2, "question_count": 2,
             "citations": ["[T04-051]"], "grounding_status": "grounded"},
        ],
        "excluded_preset_count": 10,
    },
    "noans_003": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Token",
             "qidx": [0], "unique_students": 1, "question_count": 1,
             "citations": ["[T04-049]"], "grounding_status": "grounded",
             "warnings": ["data_sparse"], "confidence": "low"},
        ],
    },
    "diff_001": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Context window, attention và hallucination",
             "qidx": [0], "unique_students": 1, "question_count": 1,
             "citations": ["[T04-051]", "[T04-052]", "[T04-053]", "[T04-048]"],
             "grounding_status": "grounded",
             "warnings": ["data_sparse"], "confidence": "low",
             "notes": "Phân biệt các ý; quan hệ với attention/hallucination "
                      "chưa có bằng chứng đủ."},
        ],
    },
    "diff_002": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Hành vi model (token prediction/hallucination)",
             "qidx": [0], "unique_students": 1, "question_count": 1,
             "citations": [], "grounding_status": "insufficient_evidence",
             "warnings": ["ambiguous_question", "data_sparse"],
             "confidence": "low"},
        ],
    },
    "diff_003": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Token và tokenization",
             "qidx": [0, 1, 2], "unique_students": 3, "question_count": 3,
             "citations": ["[T04-049]", "[T04-050]"],
             "grounding_status": "grounded"},
        ],
    },
    "diff_004": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Cơ chế attention trong Transformer",
             "qidx": [0, 1], "unique_students": 2, "question_count": 2,
             "citations": ["[T04-040]"], "grounding_status": "grounded"},
        ],
    },
    "edge_001": {
        "task": "analyze_clusters", "expected_status": "no_valid_questions",
        "clusters": [], "excluded_empty_count": 1,
    },
    "edge_002": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Context window",
             "qidx": [0, 1, 2, 3], "unique_students": 2, "question_count": 4,
             "citations": ["[T04-051]"], "grounding_status": "grounded"},
        ],
    },
    "edge_004": {
        "task": "analyze_clusters", "expected_status": "ok",
        "clusters": [
            {"concept": "Token",
             "qidx": [0], "unique_students": 1, "question_count": 1,
             "citations": ["[T04-049]"], "grounding_status": "grounded",
             "warnings": ["data_sparse"], "confidence": "low"},
        ],
    },
    "edge_005": {
        "task": "review_card", "expected_status": "source_confirmation_required",
        "teacher_confirmed_source": False,
    },
    "edge_006": {
        "task": "review_card", "expected_status": "draft_ready",
        "teacher_confirmed_source": True,
        "concept": "Context window",
        "sources": ["[T04-051]", "[T04-052]", "[T04-053]"],
    },
}


def main():
    case_paths = sorted(
        p for p in GOLDEN.glob("*.json")
        if p.name not in {"expected_clusters.json"})
    rows_csv = []            # sample_questions.csv
    rows_gt = []             # ground_truth_mapping.csv
    expected = {}
    total_questions = 0

    for path in case_paths:
        case_id = path.stem
        case = json.loads(path.read_text(encoding="utf-8-sig"))
        spec = EXPECTED[case_id]
        questions = case.get("questions", [])
        qids = [f"{case_id}_q{i}" for i in range(len(questions))]
        material_ids = [m["source_id"] for m in case.get("materials", [])]

        # Ánh xạ qidx -> expected cluster id
        cluster_of_q = {}
        expected_cluster_labels = {}
        exp = {"case_id": case_id, "task": spec["task"],
               "expected_status": spec.get("expected_status"),
               "teacher_confirmed_source": case.get("teacher_confirmed_source"),
               "materials": material_ids, "clusters": []}
        if spec["task"] == "review_card":
            exp["concept"] = spec.get("concept")
            exp["sources"] = spec.get("sources", material_ids)
        for c in spec.get("clusters", []):
            cid = f"{case_id}_c{len(exp['clusters']) + 1}"
            member_ids = [qids[i] for i in c["qidx"]]
            exp["clusters"].append({
                "cluster_id": cid,
                "concept": c["concept"],
                "question_ids": member_ids,
                "unique_students": c.get("unique_students"),
                "question_count": c.get("question_count"),
                "citations": c.get("citations", []),
                "grounding_status": c.get("grounding_status"),
                "warnings": c.get("warnings", []),
                "confidence": c.get("confidence"),
                "notes": c.get("notes"),
            })
            for i in c["qidx"]:
                cluster_of_q[qids[i]] = cid
                expected_cluster_labels[qids[i]] = c["concept"]
        expected[case_id] = exp

        for i, q in enumerate(questions):
            qid = qids[i]
            text = (q.get("student_question") or "").strip()
            is_preset = bool(q.get("is_preset"))
            student = q.get("student")
            total_questions += 1
            gt_sources = []
            if not text:
                label = "EXCLUDED_EMPTY"
                cluster_id = ""
                concept = ""
            elif is_preset:
                label = "EXCLUDED_PRESET"
                cluster_id = ""
                concept = ""
            elif qid in cluster_of_q:
                label = "VALID"
                cluster_id = cluster_of_q[qid]
                concept = expected_cluster_labels[qid]
            else:
                label = "VALID"
                cluster_id = ""
                concept = ""

            # Ground truth: nguồn của cluster expected nếu có
            if cluster_id:
                for c in exp["clusters"]:
                    if c["cluster_id"] == cluster_id:
                        gt_sources = c["citations"]
                        break
            if label.startswith("VALID") and not cluster_id:
                gt_sources = []

            rows_csv.append({
                "case_id": case_id, "question_id": qid, "student": student or "",
                "is_preset": "1" if is_preset else "0",
                "student_question": text, "label": label,
                "expected_cluster_id": cluster_id,
                "expected_concept": concept,
                "expected_sources": "|".join(gt_sources),
            })
            rows_gt.append({
                "case_id": case_id, "question_id": qid,
                "student_question": text,
                "expected_cluster_id": cluster_id,
                "expected_sources": "|".join(gt_sources),
                "grounding_status": next(
                    (c["grounding_status"] for c in exp["clusters"]
                     if c["cluster_id"] == cluster_id), ""),
            })

    # Ghi sample_questions.csv
    csv_path = GOLDEN / "sample_questions.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_csv[0]))
        writer.writeheader()
        writer.writerows(rows_csv)

    # Ghi ground_truth_mapping.csv
    gt_path = GOLDEN / "ground_truth_mapping.csv"
    with gt_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_gt[0]))
        writer.writeheader()
        writer.writerows(rows_gt)

    # Ghi expected_clusters.json
    exp_path = GOLDEN / "expected_clusters.json"
    exp_path.write_text(
        json.dumps({"total_questions": total_questions, "cases": expected},
                   ensure_ascii=False, indent=2),
        encoding="utf-8")

    print("sample_questions.csv:", csv_path, "-", len(rows_csv), "dòng")
    print("ground_truth_mapping.csv:", gt_path, "-", len(rows_gt), "dòng")
    print("expected_clusters.json:", exp_path, "-", len(expected), "case")
    print("TONG CAU HOI:", total_questions)


if __name__ == "__main__":
    main()