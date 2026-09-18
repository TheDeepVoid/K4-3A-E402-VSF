# Reflection cá nhân — Bùi Thị Ngọc Trân - 02529

### 1. Vai trò và công việc đảm nhận

Trong dự án VLearn Pulse, tôi tập trung vào khảo sát nhu cầu, xây dựng workflow và kiểm thử để cải thiện prompt.

- **Khảo sát:** Cùng nhóm thu thập và tổng hợp 23 phản hồi, tìm hiểu khó khăn khi xác định nội dung lớp cần ôn và yêu cầu để người dùng tin tưởng kết quả AI.
- **Workflow:** Tham gia xây dựng luồng chọn phạm vi, xem điểm nghẽn, đối chiếu nguồn, tạo và duyệt thẻ ôn.
- **Kiểm thử và cải thiện prompt:** Phối hợp thu thập, ghi chú golden set; đối chiếu đầu ra với test case, ghi log PASS/FAIL, phân tích lỗi và điều chỉnh prompt rồi kiểm thử lại.

Mức độ đóng góp của tôi ước tính khoảng 25% tổng khối lượng công việc của nhóm, tập trung vào kiểm thử, ghi log và cải thiện prompt, đồng thời tham gia khảo sát và xây dựng workflow.

### 2. Thách thức gặp phải

- **Kỹ thuật:** Đầu ra AI có thể diễn đạt hợp lý nhưng vẫn gom nhóm hoặc xếp hạng sai. Sửa một lỗi trong prompt cũng có thể làm case từng đạt trở thành FAIL, nên cần kiểm thử lại cả bộ.
- **Teamwork:** Cần thống nhất kết quả kỳ vọng và phiên bản prompt giữa các thành viên. Tôi phải ghi rõ lỗi và lý do chưa đạt để nhóm có căn cứ điều chỉnh.
- **Thời gian và phạm vi:** Thời gian hackathon hạn chế trong khi cần nhiều vòng kiểm thử. Khảo sát chủ yếu là học viên, chỉ có 5/23 phản hồi từ giảng viên và TA/Mentor/Lab Coach, nên chưa phản ánh đầy đủ nhu cầu người dùng chính.

### 3. Học được gì

Tôi học được cách chuyển phản hồi khảo sát thành tiêu chí kiểm thử. Chẳng hạn, 22/23 người yêu cầu dẫn nguồn chính xác và 12/23 người yêu cầu đếm học viên độc lập, giúp tôi chú ý hơn đến nguồn trích dẫn và ảnh hưởng của câu hỏi lặp.

Tôi hiểu rằng cải thiện prompt phải dựa trên log và kết quả đối chiếu. Tỷ lệ PASS của nhóm tăng từ 10/19 lên 15/19 case, nhưng vẫn còn lỗi gom nhóm và xếp hạng. AI cần hỗ trợ giảng viên kiểm tra, chỉnh sửa và quyết định sử dụng nội dung.

Về làm việc nhóm, tôi học cách phản hồi bằng case cụ thể thay vì nhận xét chung rằng kết quả chưa tốt.

### 4. Điều muốn làm khác

- Khảo sát thêm giảng viên, TA và tổ chức dùng thử sớm để kiểm chứng nhu cầu cùng mức độ hữu ích thực tế.
- Chốt tiêu chí PASS/FAIL từ đầu, lưu phiên bản prompt cùng log và chạy lại bộ test sau mỗi thay đổi.
- Kiểm thử nhiều lượt với case quan trọng; đánh giá riêng các bước lọc, đếm dữ liệu và phần suy luận của model để xác định nguyên nhân lỗi.

### 5. Đánh giá sản phẩm

- **Điểm mạnh:** Có mục tiêu rõ ràng, giúp giảng viên tổng hợp câu hỏi thành nội dung cần ôn, có nguồn đối chiếu và bản nháp thẻ ôn để chỉnh sửa.
- **Điểm yếu:** Gom nhóm và xếp hạng chưa ổn định. Kết quả eval prompt trên 19 case chưa đại diện cho toàn bộ ứng dụng; phản hồi khảo sát cũng chưa thay thế được kết quả dùng thử.
- **Khả năng ứng dụng:** Phù hợp để thử nghiệm trong lớp có nhiều dữ liệu hỏi đáp qua chat. Cần tiếp tục đánh giá với giảng viên/TA, đo hiệu quả thực tế và giữ bước kiểm tra, duyệt nội dung trước khi sử dụng.
