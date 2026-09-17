"""Tiền xử lý câu hỏi: lọc is_preset / câu rỗng, chuẩn hoá, dedupe theo học viên.

Module này là "tool" tiền xử lý dữ liệu: deterministic, không cần thêm thư viện.
Model có thể gọi qua cơ chế function calling (xem codebase/src/tools/).
"""

import re

# Các cụm câu mẫu bấm sẵn của giao diện (theo DATA_DICTIONARY.md).
PRESET_PATTERNS = [
    re.compile(r"giải\s*thích\s*đoạn\s*bôi\s*đen", re.I),
    re.compile(r"giải\s*thích\s*rõ\s*đoạn\s*này", re.I),
    re.compile(r"tóm\s*tắt\s*nội\s*dung\s*chính", re.I),
]

# Tiền tố ngữ cảnh mà giao diện chèn vào câu hỏi, ví dụ:
#   (Trang 2, đoạn được chọn: "...") / (Trang 1) hoặc (Đang học phần "...")
CONTEXT_PREFIX_RE = re.compile(
    r"^\s*\(\s*(?:Trang\s*\d+|Đang\s*học\s*phần)[^)]*\)")

LEAD_NOISE_RE = re.compile(r"^\s*(?:[-*•]\s*|\d{1,2}[.)]\s*|[`'\"]+|```+)")

# Từ dừng tiếng Việt phổ biến — loại khỏi vector từ khoá trong clustering/grounding.
VIETNAMESE_STOPWORDS = frozenset("""
các và của là có không một những được cho để trong với thì như nên khi bởi
từ vì mà này đó nào ai gì cái vậy sao tại qua về ra vào lên xuống rồi đã đang
sẽ cũng vẫn cứ lại còn nữa cả mọi mỗi chính ngay nhất thôi hơn hà hả ạ
chứ đâu đây kia nọ đúng hay hoặc theo nếu nhưng bạn em tôi chúng ta mình anh
chị thầy cô người học sinh viên câu hỏi trả lời bài giảng giáo viên giảng viên
xin hãy giúp ơi nhé đấy mấy bao nhiêu bấy nhiêu sao thế thê nào nhiều ít vài
giải thích đoạn giúp hiểu biết muốn cần nói nghĩa thấy tổng hợp tóm tắt nội
dung bôi đen chọn phần trang trích dẫn đọc xem ghi nhớ thắc mắc lo lắng
""".split())


def is_preset_question(text: str, flag=None) -> bool:
    """Nhận diện câu mẫu bấm sẵn.

    flag: nếu caller truyền cột is_preset (bool) thì dùng luôn; ngược lại dò regex.
    """
    if flag is not None:
        return bool(flag)
    t = text or ""
    return any(p.search(t) for p in PRESET_PATTERNS)


def normalize_question(text: str) -> str:
    """Chuẩn hoá câu hỏi cho cluster: bỏ tiền tố ngữ cảnh, rác đầu dòng, khoảng trắng thừa."""
    t = (text or "").strip()
    t = CONTEXT_PREFIX_RE.sub("", t)
    t = LEAD_NOISE_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = t.strip().strip('"').strip("'")
    return t


def preprocess_questions(questions, dedupe_by_student=True) -> dict:
    """Lọc + chuẩn hoá + dedupe.

    questions: list[dict] với khoá `student_question` (bắt buộc), tuỳ chọn
    `student`, `asked_at_vn`, `is_preset`.

    Trả về dict kết quả (dùng làm nội dung tool message cho model):
      valid_questions         — câu hợp lệ đã chuẩn hoá
      excluded_preset_count   — đã loại do is_preset
      excluded_empty_count    — đã loại do rỗng/sau chuẩn hoá không còn nội dung
      dedupe_removed_count    — bản trùng (student, câu) đã loại
      valid_question_count
      unique_student_count
      total_input / skipped_invalid_count
    """
    questions = questions or []
    order, excluded_preset, excluded_empty, skipped = [], 0, 0, 0

    for q in questions:
        if not isinstance(q, dict):
            skipped += 1
            continue
        raw = str(q.get("student_question") or "")
        flag = q.get("is_preset")
        flag = flag if flag is None else bool(flag)
        if is_preset_question(raw, flag):
            excluded_preset += 1
            continue
        norm = normalize_question(raw)
        if not norm:
            excluded_empty += 1
            continue
        order.append({
            "student": (q.get("student") or "").strip() or None,
            "asked_at_vn": str(q.get("asked_at_vn") or "")[:16],
            "raw_question": raw,
            "student_question": norm,
        })

    dup = 0
    valid = []
    if dedupe_by_student:
        last_idx = {}
        for it in order:
            key = (it["student"] or "**anon**", it["student_question"])
            idx = last_idx.get(key)
            if idx is None:
                last_idx[key] = len(valid)
                valid.append(it)
            else:
                # Giữ bản mới nhất theo thời gian hỏi.
                if it["asked_at_vn"] >= valid[idx]["asked_at_vn"]:
                    valid[idx] = it
                dup += 1
    else:
        valid = order

    students = {v["student"] for v in valid if v["student"]}
    return {
        "valid_questions": valid,
        "excluded_preset_count": excluded_preset,
        "excluded_empty_count": excluded_empty,
        "dedupe_removed_count": dup,
        "valid_question_count": len(valid),
        "unique_student_count": len(students),
        "total_input": len(questions),
        "skipped_invalid_count": skipped,
        "note": "Lọc is_preset (flag hoặc regex), loại câu rỗng, chuẩn hoá (bỏ tiền tố "
                "ngữ cảnh), dedupe (student, câu) giữ bản mới nhất — làm bằng code, "
                "deterministic.",
    }


def run(args: dict) -> dict:
    """Entry point khi model gọi tool `preprocess_questions`."""
    if not isinstance(args, dict) or not isinstance(args.get("questions"), list):
        raise ValueError("preprocess_questions cần args.questions là một mảng câu hỏi.")
    return preprocess_questions(args["questions"],
                                dedupe_by_student=bool(args.get("dedupe_by_student", True)))