# Reflection Cá Nhân - Nguyễn Thị Mừng

- **Họ và tên:** Nguyễn Thị Mừng
- **Mã học viên:** 2A202602575
- **Nhóm:** VFS
- **Dự án:** VLearn Pulse

---

### 1. Vai trò và công việc đảm nhận
Trong dự án Hackathon lần này, tôi đảm nhận cả các công việc liên quan đến nghiên cứu sản phẩm (Product) lẫn lập trình kỹ thuật (Engineering), cụ thể:
- **Lên bộ câu hỏi phỏng vấn và trực tiếp đi phỏng vấn:** Đóng vai trò thu thập thông tin để tìm ra "nỗi đau" (pain point) thực sự của người dùng.
- **Chốt đề tài cùng nhóm:** Dựa trên kết quả phỏng vấn, cùng nhóm phân tích Cost-of-error và chốt giải pháp *VLearn Pulse - Thẻ ôn tập 5 phút*.
- **Thiết kế Workflow:** Xây dựng tài liệu quy trình luồng hoạt động chuẩn của hệ thống.
- **Xây dựng Backend Demo:** Trực tiếp tham gia code phần API Backend (`app.py`), đặc biệt là tính năng nhận diện và xử lý mảng "nhiều nguồn học liệu" (multiple sources) từ Frontend gửi xuống.
- **Review Slide:** Hỗ trợ check lại nội dung Slide thuyết trình cuối kỳ để đảm bảo bám sát luật *"Không có bằng chứng thì không có slide"*.

*(Thời gian đầu tư: Đóng góp khoảng 25-30% tổng khối lượng công việc của nhóm)*

### 2. Thách thức gặp phải
- **Khó khăn về teamwork và quản lý thời gian (Time Management):** Mới đầu khi chọn track, nhóm phân vân quá nhiều và quyết định hơi lâu. Sự thiếu quyết đoán này dẫn đến việc quỹ thời gian dành cho khâu làm kịch bản và đi phỏng vấn thực tế bị rút ngắn lại quá nhiều. Phỏng vấn gấp gáp khiến nhóm gặp khó khăn trong việc căn chỉnh lịch họp chung và làm khâu tổng hợp dữ liệu bị dồn ứ.
- **Khó khăn kỹ thuật (Backend & Demo):** 
  - Khi nâng cấp tính năng từ "chọn 1 tài liệu" lên "chọn nhiều tài liệu" (Multi-select) để đáp ứng Feedback của user, tôi đã phải vật lộn với việc thiết kế lại Data Schema (Pydantic) sao cho Backend không bị lỗi `422 Unprocessable Entity`.
  - Quản lý mã nguồn (Git): Gặp tình huống Merge Conflict khá căng thẳng sát giờ G khi ghép code Backend của tôi với phần giao diện (UI) mới do thành viên khác viết lại trên nhánh `main`.

### 3. Học được gì
- **Kỹ năng mới:** Cứng cáp hơn trong việc thao tác với Git/Github (xử lý Merge Conflict) và kỹ năng thiết kế API giao tiếp giữa Frontend - Backend.
- **Hiểu biết về AI/Product Development:** Bài học lớn nhất là tư duy thiết kế "Human-in-the-loop" và "Cost of error". Nhờ có quá trình phỏng vấn, tôi nhận ra không phải cứ tự động hóa (Automate) 100% là tốt. Việc ép AI phải nhường quyền quyết định "chọn nguồn tài liệu" cho Giảng viên (Augment) mới là chìa khóa để sản phẩm sống sót trong môi trường Giáo dục.
- **Làm việc nhóm:** Hiểu được tầm quan trọng của việc chốt chuẩn giao thức giao tiếp (Data Contract) giữa người làm Frontend và người làm Backend từ sớm để tránh việc tích hợp bị gãy.

### 4. Điều muốn làm khác
- **Về Process:** Nếu được làm lại, tôi và nhóm sẽ chốt track và đề tài quyết đoán hơn ngay từ đầu, nhằm căn chỉnh thời gian hợp lý và dành quỹ thời gian rộng rãi hơn cho khâu Khám phá (Discovery - Phỏng vấn). Phỏng vấn trong trạng thái gấp gáp khiến nhóm bị cuốn theo tiến độ và suýt bỏ lỡ một vài insight đắt giá.
- **Về Technical:** Sẽ thiết lập một quy trình Git Workflow rõ ràng hơn từ ngày đầu tiên (ai làm nhánh nào, merge vào đâu) để không bị hoảng hốt khi phải xử lý conflict code Backend vào phút chót.

### 5. Đánh giá sản phẩm
- **Điểm mạnh của VLearn Pulse:** Bám cực kỳ sát thực tế, giải đúng "nỗi đau" tốn thời gian lướt log Discord của Giảng viên. Hướng tiếp cận kỹ thuật rất thông minh: nhờ Giảng viên đóng vai trò là "bộ lọc" chọn tài liệu, hệ thống tiết kiệm được một lượng Token và Latency khổng lồ so với việc bắt AI tự đi search trong kho dữ liệu.
- **Điểm yếu cần cải thiện:** Giao diện Demo hiện tại chỉ dừng ở việc sinh ra bản nháp. Cần phải bổ sung thêm tính năng "Inline Edit" (cho phép Giảng viên click vào chữ trên Thẻ Ôn Tập và sửa trực tiếp nội dung AI sinh ra) để tối ưu trải nghiệm duyệt bài.
- **Khả năng ứng dụng:** Rất cao. Có thể tích hợp ngay vào hệ thống LMS hiện tại của nhà trường như một tool nội bộ (Internal Tool) cho đội ngũ TA và Giảng viên.
