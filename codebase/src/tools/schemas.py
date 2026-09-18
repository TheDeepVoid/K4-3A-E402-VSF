"""OpenAI tool schemas (function calling) cho VLearn Pulse.

Ba tool xử lý dữ liệu doe model gọi qua cơ chế function calling:
  - preprocess_questions: lọc/chuẩn hoá/dedupe câu hỏi
  - cluster_questions:    gom câu thành cụm chủ đề (deterministic)
  - ground_clusters:      tìm segment [Txx-NNN] khớp từ khoá cụm
"""

_question_item = {
    "type": "object",
    "properties": {
        "student": {"type": "string", "description": "Mã ẩn danh S#### (nếu có)."},
        "asked_at_vn": {"type": "string", "description": "Thời điểm hỏi YYYY-MM-DD HH:MM."},
        "is_preset": {"type": "boolean", "description": "Câu mẫu bấm sẵn của giao diện (nếu đã biết)."},
        "student_question": {"type": "string", "description": "Câu hỏi nguyên văn.",
                             "minLength": 1},
    },
    "required": ["student_question"],
}

_material_item = {
    "type": "object",
    "properties": {
        "source_id": {"type": "string", "description": "Mã nguồn, ví dụ [T04-051]."},
        "source_type": {"type": "string", "description": "Loại nguồn, ví dụ transcript."},
        "content": {"type": "string", "description": "Nội dung đoạn."},
    },
    "required": ["source_id", "content"],
}

_cluster_item = {
    "type": "object",
    "properties": {
        "cluster_id": {"type": "string"},
        "concept": {"type": "string"},
        "question_count": {"type": "integer"},
        "unique_students": {"type": "integer"},
        "top_terms": {"type": "array", "items": {"type": "string"}},
        "example_questions": {"type": "array", "items": {"type": "string"}},
    },
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "preprocess_questions",
            "description": (
                "Lọc và chuẩn hoá câu hỏi TRƯỚC khi gom cụm. Loại câu mẫu bấm sẵn "
                "(is_preset: dùng flag nếu có, nếu không thì regex 'giải thích đoạn "
                "bôi đen' / 'giải thích rõ đoạn này' / 'tóm tắt nội dung chính'), "
                "loại câu rỗng sau chuẩn hoá, bỏ tiền tố ngữ cảnh '(Trang N, ...)' / "
                "'(Đang học phần ...)', dedupe (student, câu) giữ bản mới nhất. "
                "Hãy gọi tool này thay vì tự đếm preset/rỗng trong đầu — kết quả là "
                "valid_questions + các bộ đếm chính xác."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "description": "Toàn bộ câu hỏi gốc của phạm vi cần phân tích.",
                        "items": _question_item,
                    },
                    "dedupe_by_student": {
                        "type": "boolean",
                        "description": "Dedupe (student, câu) giữ bản mới nhất. Mặc định true.",
                    },
                },
                "required": ["questions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_questions",
            "description": (
                "Gom các câu hỏi ĐÃ CHUẨN HOÁ thành cụm chủ đề thô bằng độ tương đồng "
                "từ khoá (Jaccard trên unigram + bigram, single-pass greedy). Trả về "
                "clusters có concept gợi ý, question_count, unique_students, "
                "top_terms, example_questions; các câu không đủ min_cluster_size nằm "
                "trong unassigned. Bạn vẫn là người đánh giá cuối: gộp, đặt tên, xếp "
                "hạng và chỉ giữ cụm thực sự là điểm nghẽn phổ biến."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "description": "Câu đã qua preprocess_questions (dùng valid_questions).",
                        "items": {"type": "object",
                                  "properties": {"student_question": {"type": "string"},
                                                 "student": {"type": "string"}},
                                  "required": ["student_question"]},
                    },
                    "similarity_threshold": {"type": "number", "default": 0.40,
                                            "description": "Overlap coefficient tối thiểu để gom (mặc định 0.40)."},
                    "min_cluster_size": {"type": "integer", "default": 2},
                },
                "required": ["questions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ground_clusters",
            "description": (
                "Tìm đoạn học liệu [Txx-NNN] trong materials khớp với từ khoá của từng "
                "cụm (tf-idf, chuẩn hoá 0..1). Trả về matches kèm score và snippet, chỉ "
                "trả nguồn CÓ THẬT trong materials — không bịa citation. Dùng kết quả "
                "này để điền citations và xác định grounding_status cho các cụm."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "clusters": {
                        "type": "array",
                        "description": "Các cụm cần tìm nguồn (kết quả cluster_questions).",
                        "items": _cluster_item,
                    },
                    "materials": {
                        "type": "array",
                        "description": "Các segment học liệu đang có (transcripts).",
                        "items": _material_item,
                    },
                    "top_k": {"type": "integer", "default": 3},
                },
                "required": ["clusters", "materials"],
            },
        },
    },
]

TOOL_NAMES = [s["function"]["name"] for s in TOOL_SCHEMAS]