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

### Công nghệ dự kiến
- **Embedding**: sentence-transformers cho semantic similarity
- **Clustering**: HDBSCAN hoặc K-means với dynamic K
- **LLM**: GPT-3.5/4 cho tạo thẻ ôn và đặt tên cluster
- **Backend**: Python FastAPI
- **Frontend**: React/Streamlit (MVP)

## 4. KPI & Đánh giá

| Metric | Cách đo | Target |
|---|---|---|
| Cluster usefulness | Giảng viên rating top-5 | ≥80% hữu ích |
| Grounding accuracy | Đúng slide/transcript | ≥90% |
| Noise resistance | Ranking ổn định sau dedup | <20% thay đổi |
| Response time | Từ upload đến kết quả | ≤30s |

## 5. Rủi ro & Giải pháp

| Rủi ro | Impact | Mitigation |
|---|---|---|
| AI gán sai cluster | Cao | Human-in-the-loop, cho phép chỉnh sửa |
| Data thưa, ít tương tác | Trung bình | Hiển thị confidence score + cảnh báo |
| Privacy leak | Cao | Không hiển thị student ID, chỉ aggregate |
| Clustering không chuẩn | Trung bình | Multiple algorithms, A/B test |

## 6. Phạm vi MVP

### Làm (trong hackathon)
- Clustering câu hỏi K4 (448 học viên, 3.097 lượt hỏi)
- Liên kết với 2 bộ slide hackathon
- UI hiển thị top-5 cluster + thông tin chi tiết
- Tạo 1 thẻ ôn mẫu

### Mock/Giả lập
- Grounding tự động với slide → manual mapping
- Real-time processing → batch offline
- Full transcript integration → sample transcript

### Không làm
- Multi-cohort comparison
- Học viên trực tiếp sử dụng
- Production deployment

---

*Tài liệu này tuân thủ template `03-ai-spec-template.md` — cập nhật theo tiến độ phát triển.*