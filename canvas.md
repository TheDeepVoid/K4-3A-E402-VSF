# Canvas — VLearn Pulse (Đề tài A2)

> CP1: Canvas 4 ô — Nộp trước 19:30 ngày 16/9

---

## Ô 1: NỖI ĐAU (PAIN)

**Giảng viên/TA đang gặp vấn đề gì?**

- Không có cách tin cậy để biết **lớp đang kẹt ở khái niệm nào** — chỉ nhìn thấy chatlog rời rạc hàng nghìn câu hỏi
- Không biết điểm kẹt này liên quan đến **trang slide hoặc đoạn transcript nào** để chuẩn bị ôn tập
- Không thể phân biệt đây là khó khăn **phổ biến của nhiều học viên** hay chỉ do một người hỏi nhiều lần / câu hỏi mẫu
- Phải đọc thủ công toàn bộ chatlog (3.097 lượt hỏi/tuần từ 448 học viên K4) — mất thời gian, không hiệu quả

**Bằng chứng từ data:**
- 13.494 lượt hỏi-đáp trong data pack, nhưng giảng viên chưa có công cụ tổng hợp
- Rating chỉ 1,3% (177 lượt), `understanding_level` gần như trống — không có tín hiệu đáng tin cậy

---

## Ô 2: GIẢI PHÁP (SOLUTION)

**VLearn Pulse — Tính năng AI tổng hợp chatlog thành bản đồ điểm nghẽn học tập**

- **Tự động nhóm** các câu hỏi có ý nghĩa tương tự theo khái niệm (semantic clustering)
- **Liên kết với học liệu**: trang slide + mã transcript `[Txx-NNN]`
- **Hiển thị Top 5 điểm nghẽn** với:
  - Tên khái niệm (AI gợi ý, giảng viên sửa được)
  - Số học viên unique đã hỏi (trọng số 1 người = 1 phiếu)
  - 1–2 ví dụ câu hỏi đã ẩn danh
  - Mức tin cậy / cảnh báo data thưa
- **Tạo thẻ ôn 5 phút**: mục tiêu + hiểu nhầm phổ biến + trích đoạn nguồn + ví dụ + câu kiểm tra
- **Human-in-the-loop**: giảng viên phê duyệt, có quyền gộp/tách/đổi tên/bỏ cluster

**Xử lý hard tests:**
- Lọc câu preset (`is_preset`) — chiếm 22,7%
- Dedup theo học viên unique — tránh 1 người hỏi 20 lần chi phối
- Semantic clustering gộp các trang khác nhau cùng khái niệm
- Hiển thị "chưa đủ signal" thay vì kết luận khi data thưa

---

## Ô 3: NGƯỜI DÙNG (USERS)

| Người dùng | Nhu cầu chính | Pain hiện tại |
|---|---|---|
| **Giảng viên** | Biết lớp kẹt ở đâu để quyết định ôn gì | Không có tool tổng hợp, phải đọc chatlog thủ công |
| **TA (Trợ giảng)** | Hỗ trợ giảng viên chuẩn bị nội dung | Thiếu data-driven insight, phải đoán |

**Đối tượng phụ:** Học viên (间接受益 từ việc giảng viên ôn đúng chỗ)

**Loại trừ:**
- Không hiển thị mã học viên cá nhân
- Không cho drill-down đến lịch sử của từng học viên
- Chỉ hiển thị aggregate + ví dụ đã ẩn danh

---

## Ô 4: GIÁ TRỊ & KPI (VALUE)

| Metric | Cách đo | Mục tiêu |
|---|---|---|
| **Cluster usefulness** | Tỷ lệ top-5 cluster được giảng viên xác nhận hữu ích | ≥ 80% |
| **Grounding** | Tỷ lệ insight có liên kết đúng slide/transcript | ≥ 90% |
| **Noise resistance** | So sánh top-5 trước/sau dedup theo học viên | Thứ hạng ổn định |
| **Actionability** | Thời gian từ mở báo cáo đến tạo thẻ ôn | ≤ 5 phút |
| **Privacy** | Không lộ định danh cá nhân | 100% |

**Giá trị cốt lõi:**
- Giảm thời gian đọc chatlog thủ công (từ ~2 giờ → 5 phút)
- Phát hiện sớm điểm cả lớp cần ôn lại
- Evidence gắn với slide/transcript thay vì kết luận mơ hồ
- Giữ giảng viên trong vòng quyết định — AI chỉ hỗ trợ, không thay thế

---

## ✅ Checklist CP1

- [x] Canvas điền đủ 4 ô theo mẫu
- [x] Đội trưởng: _____________
- [x] Link repo GitHub công khai: _____________

---

*Ngày tạo: 16/09/2026 — VLearn Pulse (Track A, Bài A2)*