# Đề tài A2 — VLearn Pulse

## VLearn Pulse — Bản đồ điểm nghẽn học tập cho giảng viên

> **VLearn Pulse biến hàng nghìn câu hỏi rời rạc thành 5 điểm lớp đang kẹt, có bằng chứng từ học liệu để giảng viên quyết định ôn gì tiếp theo.**

---

## 1. Phạm vi đề bài

Đề tài thuộc **Track A — VLearn Tutor, bài A2: Tính năng AI mới trên VLearn**.

Mục tiêu không phải tối ưu câu trả lời của tutor hiện có (A1), mà là xây dựng một tính năng mới cho giảng viên/TA hoặc học viên, xuất phát từ pain thực tế trong data.

### Bối cảnh dữ liệu

Data pack `data/vlearn-pack/` có:

- 13.494 lượt hỏi–đáp thật giữa học viên và AI tutor, từ 22/07 đến 15/09/2026.
- 1.617 học viên; trong đó **K4 là khoá hiện tại**: 3.097 lượt hỏi từ 448 học viên, từ 09/09 đến 15/09.
- 6 transcript bài giảng có mã đoạn trích dẫn `[Txx-NNN]`.
- 2 bộ slide hackathon.

### Các lưu ý khi mining data

- Tập trung phân tích **K4** vì đây là khoá hiện tại.
- Loại hoặc tách riêng câu hỏi mẫu (`is_preset`) trước khi kết luận về nhu cầu tự nhiên của học viên. Câu preset chiếm 22,7% toàn bộ log.
- Không dùng rating làm signal chính vì chỉ có 177 lượt rating, tương đương 1,3%.
- Không dùng `understanding_level` làm ground truth vì gần như trống: chỉ có 20 lượt.
- Chống nhiễu từ trường hợp một học viên hỏi lặp lại nhiều lần.
- Gộp các trang/cách diễn đạt khác nhau nhưng cùng nói về một khái niệm.
- Không để lộ học viên nào hỏi gì cho người khác; giảng viên là người quyết định nội dung ôn lại.

---

## 2. Pain cần giải quyết

Tutor hiện có nhiều lượt tương tác, nhưng giảng viên/TA chưa có cách tin cậy để trả lời các câu hỏi:

- Lớp đang kẹt ở **khái niệm nào**, thay vì chỉ nhìn thấy một luồng chat rời rạc?
- Điểm kẹt này liên quan đến **trang slide hoặc đoạn transcript nào**?
- Đây là khó khăn phổ biến của nhiều học viên, hay chỉ do một người hỏi nhiều lần / câu hỏi mẫu?
- Buổi sau nên ôn lại nội dung nào, với bằng chứng ngắn gọn và có căn cứ?

Dữ liệu chatlog đang chứa những tín hiệu này, nhưng chưa được tổng hợp thành insight có thể hành động cho giảng viên.

---

## 3. Giải pháp: VLearn Pulse

**VLearn Pulse** là tính năng AI tổng hợp chatlog sau buổi học thành bản đồ các điểm lớp đang gặp khó khăn.

Thay vì yêu cầu giảng viên đọc từng đoạn chat, hệ thống tự nhóm các câu hỏi có ý nghĩa tương tự, liên kết chúng với học liệu, và hiển thị các điểm cần xem lại.

### Người dùng chính

- Giảng viên.
- Trợ giảng / TA.

### Lát cắt demo

**Một giảng viên, sau buổi học, mở VLearn Pulse để xem 5 điểm lớp đang kẹt nhất; chọn một điểm và tạo thẻ ôn tập cho buổi sau.**

---

## 4. Luồng trải nghiệm

1. Giảng viên chọn bài giảng hoặc phạm vi thời gian cần xem.
2. Hệ thống lọc câu preset và các tín hiệu nhiễu.
3. AI chuẩn hoá, nhóm các câu hỏi cùng ý theo khái niệm và nguồn học liệu.
4. Hệ thống hiển thị **Top 5 điểm nghẽn học tập**.
5. Giảng viên chọn một điểm để xem bằng chứng và tạo **thẻ ôn 5 phút**.
6. Giảng viên duyệt, sửa hoặc bỏ đề xuất trước khi sử dụng trong buổi học tiếp theo.

---

## 5. Mỗi điểm nghẽn hiển thị gì?

Mỗi insight/cluster nên có:

- **Tên khái niệm** do AI gợi ý, giảng viên có thể sửa.
- **Nguồn học liệu liên quan**: trang slide và/hoặc mã đoạn transcript.
- **Số học viên duy nhất** đã hỏi về điểm này.
- **Số lượt hỏi** và mức độ lặp lại theo thời gian.
- 1–2 **ví dụ câu hỏi đã ẩn danh**, được rút gọn.
- **Mức tin cậy** hoặc cảnh báo nếu data quá thưa.
- Nút để giảng viên **gộp, tách, đổi tên hoặc bỏ qua** cluster.

### Thẻ ôn 5 phút

Khi giảng viên chọn một điểm nghẽn, AI tạo bản nháp gồm:

- Mục tiêu cần ôn.
- Hiểu nhầm phổ biến mà học viên đang gặp.
- Trích đoạn nguồn từ slide/transcript.
- Một ví dụ giải thích ngắn.
- Một câu kiểm tra hiểu cuối phần ôn.

AI chỉ hỗ trợ đề xuất; giảng viên luôn là người phê duyệt và quyết định nội dung dạy.

---

## 6. Xử lý các hard tests

| Rủi ro dữ liệu | Cách VLearn Pulse xử lý |
|---|---|
| Câu hỏi preset làm phồng một chủ đề | Mặc định loại `is_preset`; có thể bật xem riêng để biết học viên hay dùng loại gợi ý nào. |
| Một học viên hỏi 20 lần | Đánh trọng số theo số học viên duy nhất; mỗi học viên chỉ đóng góp tối đa một phiếu cho một cluster. |
| Hai trang nói cùng một khái niệm | Semantic clustering và liên kết đa nguồn; một cluster có thể gắn nhiều trang/đoạn transcript. |
| Lớp hỏi ít, data thưa | Không kết luận lớp đã hiểu; hiển thị “chưa đủ signal” cùng độ phủ học viên. |
| AI gán nhầm hoặc đoán quá mức | Mỗi insight phải có ví dụ câu hỏi nguồn và trích dẫn học liệu; giảng viên có quyền chỉnh sửa hoặc loại bỏ. |
| Rủi ro riêng tư | Không hiển thị mã học viên, không có drill-down đến lịch sử của cá nhân; chỉ hiển thị aggregate và ví dụ đã ẩn danh. |

---

## 7. Data sử dụng

Nguồn chính: `data/vlearn-pack/chatlog/tutor_turns.csv`.

| Mục đích | Trường dữ liệu |
|---|---|
| Chọn đúng phạm vi phân tích | `cohort_hint`, `lecture_code`, `lecture_title`, `asked_at_vn` |
| Lọc nhiễu | `is_preset` |
| Đo mức độ phổ biến | `student` — chỉ dùng nội bộ để đếm số học viên unique, không hiển thị ra giao diện |
| Gom nhóm theo nội dung | `student_question` |
| Liên kết với nguồn | Ngữ cảnh `(Trang N, đoạn được chọn...)` trong câu hỏi; citation `[trang N]` trong phản hồi |
| Kiểm chứng học liệu | Transcript có mã `[Txx-NNN]` và slide trong pack |

### Insight nền từ data dictionary

- `move_used = review_concept` chiếm khoảng 90% lượt tương tác.
- `ask_probing_question` chỉ có 28/13.494 lượt.

Điều này cho thấy chatlog là tín hiệu hữu ích để phát hiện chỗ người học phải dừng lại để hỏi, nhưng **không đủ để kết luận chắc chắn mức độ hiểu của từng học viên**.

Vì vậy, VLearn Pulse cần gọi các kết quả là **“điểm cần giảng viên xem lại”**, không phải bảng đánh giá năng lực hay mức độ hiểu của học viên.

---

## 8. KPI đánh giá prototype

Không dùng rating làm KPI chính. Các KPI phù hợp hơn:

1. **Cluster usefulness**: tỷ lệ top-5 cluster được giảng viên/TA xác nhận là hữu ích hoặc chỉ cần sửa ít.
2. **Grounding**: tỷ lệ insight có liên kết đúng đến slide hoặc transcript.
3. **Noise resistance**: so sánh top-5 trước/sau khi deduplicate theo học viên; đảm bảo một học viên không chi phối kết quả.
4. **Actionability**: thời gian từ lúc giảng viên mở báo cáo đến lúc tạo được một thẻ ôn.
5. **Privacy**: không hiển thị định danh học viên và không cho phép drill-down theo từng cá nhân.

---

## 9. Giá trị của đề tài

VLearn Pulse không chỉ là dashboard đếm keyword. Sản phẩm biến dữ liệu tương tác rời rạc thành insight có căn cứ, được liên kết trực tiếp với học liệu và hỗ trợ giảng viên ra quyết định.

Giá trị cốt lõi:

- Giảm thời gian đọc chatlog thủ công.
- Giúp giảng viên phát hiện sớm những chỗ cả lớp cần được ôn lại.
- Đưa ra evidence gắn với slide/transcript thay vì kết luận mơ hồ.
- Giữ giảng viên trong vòng quyết định, không để AI tự quyết định nội dung dạy.
- Tôn trọng quyền riêng tư của học viên.
