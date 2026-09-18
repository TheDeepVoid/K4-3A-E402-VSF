# AI Spec — VLearn Pulse

> **Deliverable trung tâm** theo template `03-ai-spec-template.md`

## 1. Tổng quan sản phẩm

### Tên sản phẩm
**VLearn Pulse** — Bản đồ điểm nghẽn học tập cho giảng viên

### Mô tả ngắn gọn
VLearn Pulse biến hàng nghìn câu hỏi rời rạc thành 5 điểm lớp đang kẹt, có bằng chứng từ học liệu để giảng viên quyết định ôn gì tiếp theo.

### Người dùng mục tiêu
- **Chính**: Giảng viên, TA (trợ giảng)
- **Phụ**: Học viên (được hưởng lợi gián tiếp từ việc ôn đúng trọng tâm)

## 2. Bài toán AI cốt lõi

### Input
- Chatlog từ `tutor_turns.csv`: câu hỏi học viên + phản hồi AI tutor
- Metadata: `cohort_hint`, `lecture_code`, `is_preset`, `student`, `asked_at_vn`
- Học liệu: slide PDF + transcript có mã `[Txx-NNN]`

### Output
- **Top 5 điểm nghẽn**: tên khái niệm + nguồn học liệu + số học viên unique + ví dụ câu hỏi ẩn danh
- **Thẻ ôn 5 phút**: mục tiêu + hiểu nhầm phổ biến + trích đoạn + ví dụ + câu kiểm tra

### Xử lý AI
1. **Lọc nhiễu**: loại `is_preset`, dedup theo `student`
2. **Semantic clustering**: gom câu hỏi cùng ý nghĩa
3. **Grounding**: liên kết cluster với slide/transcript
4. **Ranking**: ưu tiên theo số học viên unique + tần suất
5. **Generation**: tạo thẻ ôn từ cluster được chọn

## 3. Kiến trúc kỹ thuật

### Pipeline chính
```
Raw chatlog → Preprocessing → Semantic Clustering → Grounding → Ranking → UI Display
```

### Công nghệ đã dùng (theo tiến độ thực tế)

- **Clustering + Grounding + Ranking**: một system prompt LLM duy nhất
  (`codebase/src/prompting/system_prompt.md` v1.2) thực hiện gom nhóm theo khái niệm, liên kết
  transcript `[Txx-NNN]`, xếp hạng theo số học viên unique và tạo thẻ ôn.
- **LLM**: gọi qua router OmniRoute (giao thức OpenAI-compatible), model `kiro/deepseek-3.2`
  (verified working; ~3–19s/case). Runner `run_cases.py` chọn provider bằng `--provider`
  (`openai | openrouter | omniroute | gemini`) — không hard-code vào OmniRoute.
- **Preprocessing** (lọc `is_preset`, loại câu rỗng, dedup theo học viên): hiện nằm trong prompt
  với đếm `excluded_preset_count`/`excluded_empty_count`; chưa chuyển về code (xem MVP).
- **Đánh giá**: golden set 50 câu label thủ công → 19 case; mỗi phiên bản prompt chạy đủ 19 case
  qua API thật, chấm tay + auto-check (schema, citation ⊆ materials, không lộ định danh,
  không mã nguồn giả). Chi tiết: `eval/`.

### Công nghệ dự kiến ban đầu (chưa dùng)

- Embedding `sentence-transformers` + HDBSCAN/K-means cho semantic clustering: **chưa dùng** —
  nhóm chốt phương án gom bằng LLM prompt vì dữ liệu thật là câu hỏi ngắn tiếng Việt, dễ gom theo
  nghĩa hơn theo vector.
- GPT-3.5/4: **chưa dùng** — dùng `kiro/deepseek-3.2` qua OmniRoute (rẻ, ổn định, verified).
- Backend FastAPI + frontend React/Streamlit: **chưa làm** — hiện có CLI runner +
  `ui/mockup.html` (xem MVP).

## 4. KPI & Đánh giá

| Metric | Cách đo | Target | Kết quả thực tế (17/9) |
|---|---|---|---|
| Cluster usefulness | Giảng viên rating top-5 | ≥80% hữu ích | **Chưa đo** — chờ validation với giảng viên thật (`validation/`) |
| Grounding accuracy | Đúng slide/transcript | ≥90% | **Đạt: 1,0** (18/18 cluster có grounding hợp lệ trên eval v1.2) |
| Noise resistance | Ranking ổn định sau dedup | <20% thay đổi | **Đạt: 1,0** (avg Spearman rho sau dedup, 2 case thí nghiệm) |
| Response time | Từ upload đến kết quả | ≤30s | **Chưa đo chính thức**; mỗi case gọi API ~3–19s trên OmniRoute |
| Tỷ lệ PASS case eval | Review thủ công + auto-check | — | 15/19 = 78,9% (v1.2), tăng từ 52,6% (v1.0) và 63,2% (v1.1) |

Chi tiết cách tính từng metric: `eval/README.md`; báo cáo đầy đủ: `eval/metrics/evaluation_report.md`.

## 5. Rủi ro & Giải pháp

| Rủi ro | Impact | Mitigation |
|---|---|---|
| AI gán sai cluster | Cao | Human-in-the-loop, cho phép chỉnh sửa |
| Data thưa, ít tương tác | Trung bình | Hiển thị confidence score + cảnh báo |
| Privacy leak | Cao | Không hiển thị student ID, chỉ aggregate |
| Clustering không chuẩn | Trung bình | Multiple algorithms, A/B test |

## 6. Phạm vi MVP

### Làm (trong hackathon)
- Clustering câu hỏi K4 (448 học viên, 3.097 lượt hỏi) — **đạt ở mức eval**: hệ thống prompt gom
  cluster + ranking hoạt động trên 19 case golden (15/19 PASS v1.2); chưa chạy end-to-end trên
  toàn bộ 3.097 lượt qua một pipeline code duy nhất
- Liên kết với 2 bộ slide hackathon — **đạt ở mức eval**: grounding theo `[Txx-NNN]` trong
  transcript mẫu; slide đầy đủ chưa nạp vào materials ngoài bộ test
- UI hiển thị top-5 cluster + thông tin chi tiết — **mockup** (`codebase/src/ui/mockup.html`);
  chưa có frontend chạy thật kết nối backend
- Tạo 1 thẻ ôn mẫu — **đạt**: task `review_card` trong eval tạo draft đủ 5 trường
  (`draft_ready`), có chặn tạo khi chưa xác nhận nguồn (`source_confirmation_required`)

### Mock/Giả lập
- Grounding tự động với slide → manual mapping — **đang ở mức "in-prompt + manual check"**:
  model tự gán citation trong `materials`, giảng viên chưa xác nhận hàng loạt
- Real-time processing → batch offline — **đúng như vậy**: eval chạy batch offline từng case
- Full transcript integration → sample transcript — **đúng như vậy**: eval dùng transcript mẫu

### Chưa làm (còn thiếu để hoàn thiện MVP)
- Preprocessing bằng code (lọc preset, dedup, đếm) — hiện phụ thuộc sự tuân thủ của model
- Pipeline CLI/backend từ `tutor_turns.csv` → top-5 cluster → thẻ ôn (chỉ có runner từng case)
- Backend FastAPI + frontend kết nối được (mới có mockup tĩnh)
- Validation với giảng viên/TA thật (`validation/` mới có kế hoạch, chưa có session)
- Đo độ ổn định nhiều lượt chạy (mỗi phiên bản mới chạy 1 lượt/case) và bộ đo noise dày hơn

### Không làm
- Multi-cohort comparison
- Học viên trực tiếp sử dụng
- Production deployment

---

*Tài liệu này tuân thủ template `03-ai-spec-template.md` — cập nhật theo tiến độ phát triển.*