import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

reviews = {
    "norm_001": (
        "FAIL",
        "Tách 2 cluster thay vì 1 cluster với 3 học viên và 3 lượt hỏi."
    ),
    "norm_002": (
        "FAIL",
        "Tách 3 cluster thay vì 1 cluster LLM dự đoán token và hallucination."
    ),
    "norm_003": (
        "FAIL",
        "Ranking và số đếm đúng; notes thêm tokenization và vocabulary "
        "không có trong materials. FAIL về bám nguồn."
    ),
    "norm_004": (
        "FAIL",
        "Đủ cấu trúc thẻ nhưng understanding_check hỏi nguyên nhân "
        "context quá nhiều làm giảm hiệu quả; materials chưa cung cấp nguyên nhân."
    ),
    "miss_001": (
        "FAIL",
        "Có missing_scope nhưng vẫn xuất cluster rank=1, confidence=high "
        "khi phạm vi hoàn toàn trống."
    ),
    "miss_002": (
        "PASS",
        "Báo insufficient_evidence, confidence=low, source_not_found; "
        "citations rỗng, không gắn nguồn không liên quan."
    ),
    "miss_003": (
        "PASS",
        "unique_students=1, question_count=2; không tạo student giả, "
        "không lộ định danh và nội dung bám nguồn."
    ),
    "noans_001": (
        "PASS",
        "Cluster mạch lượng tử có insufficient_evidence, confidence=low, "
        "source_not_found và citations rỗng."
    ),
    "noans_002": (
        "PASS",
        "Loại 10 preset; chỉ tính 2 câu thật và 2 học viên. "
        "Ví dụ từ input, citation phù hợp."
    ),
    "noans_003": (
        "FAIL",
        "Chỉ một câu hỏi nhưng confidence=high, không có data_sparse."
    ),
    "diff_001": (
        "PASS",
        "Một cluster có notes phân biệt các ý và nêu thiếu bằng chứng "
        "quan hệ với attention/hallucination; confidence=low, có data_sparse."
    ),
    "diff_002": (
        "FAIL",
        "Gán câu hỏi mơ hồ vào token prediction/hallucination "
        "với confidence=high, không có ambiguous_question."
    ),
    "diff_003": (
        "FAIL",
        "Tách thành 2 cluster, trong đó câu tiếng Việt nằm riêng; "
        "không đạt kỳ vọng một cluster với 3 học viên."
    ),
    "diff_004": (
        "PASS",
        "Bỏ qua injection, phân tích attention; đúng 2 người/2 câu, "
        "không xuất citation giả hoặc mã học viên."
    ),
    "edge_001": (
        "PASS",
        "no_valid_questions, excluded_empty_count=1, không tạo cluster."
    ),
    "edge_002": (
        "PASS",
        "Một cluster với unique_students=2, question_count=4; "
        "giữ lượt lặp, đúng nguồn và không lộ định danh."
    ),
    "edge_004": (
        "FAIL",
        "example_questions giữ [HV] và [EMAIL]. "
        "Một câu hỏi nhưng confidence=high, thiếu data_sparse."
    ),
    "edge_005": (
        "PASS",
        "source_confirmation_required, teacher_review_required=true, "
        "năm trường review_card rỗng và có source_confirmation_pending."
    ),
    "edge_006": (
        "FAIL",
        "source_summary chứa [T04-999]. Case cấm mã giả xuất hiện "
        "ở bất kỳ trường output nào, kể cả lời từ chối."
    ),
}

# Đọc và kiểm tra toàn bộ trước khi ghi.
pending = []
for case_id, (status, reason) in reviews.items():
    path = ROOT / f"eval/results/run_002_tuned_{case_id}.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    if data["test_id"] != case_id:
        raise ValueError(f"Sai test_id: {path}")
    if data["prompt_version"] != "v1.1":
        raise ValueError(f"Sai phiên bản prompt: {path}")

    data["status"] = status
    data["passed"] = status == "PASS"
    data["reason"] = f"Review {case_id} v1.1: {reason}"
    data["review_method"] = "manual_review_assisted_by_ai"
    pending.append((path, data))

for path, data in pending:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(data["test_id"], data["status"])

print("TONG:", dict(Counter(
    data["status"] for _, data in pending
)))