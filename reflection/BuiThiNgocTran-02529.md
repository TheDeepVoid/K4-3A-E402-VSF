# Reflection cá nhân — Bùi Thị Ngọc Trân - 02529

### 1. Vai trò và công việc đảm nhận

Trong hackathon VLearn Pulse, tôi phụ trách khảo sát nhu cầu, xây dựng workflow, kiểm thử đầu ra, ghi log kết quả và tham gia cải thiện prompt. Tôi tập trung kết nối nhu cầu người dùng với luồng sử dụng và các tiêu chí đánh giá sản phẩm.

Ở phần khảo sát, tôi và các bạn thu thập và tổng hợp 23 phản hồi, gồm 18 học viên, 4 TA/Mentor/Lab Coach và 1 giảng viên. Nội dung khảo sát tập trung vào khó khăn khi xác định điểm nghẽn học tập, chuẩn bị nội dung ôn và những điều kiện để người dùng tin tưởng kết quả AI.

Tôi xây dựng workflow gồm chọn phạm vi phân tích, xem các điểm nghẽn, đối chiếu học liệu, tạo bản nháp thẻ ôn, chỉnh sửa và duyệt. Trong quá trình kiểm thử, tôi đối chiếu đầu ra sau các lần điều chỉnh prompt với kết quả kỳ vọng của test case, ghi nhận PASS/FAIL, phân tích lỗi và tham gia cải thiện prompt trước khi kiểm thử lại.

Phần lớn thời gian của tôi dành cho kiểm thử, ghi log và cải thiện prompt; phần còn lại dành cho khảo sát và xây dựng workflow. Tôi chưa ghi nhận thời gian theo từng nhiệm vụ nên chưa có tỷ lệ phần trăm đáng tin cậy.

### 2. Thách thức gặp phải

**Về kỹ thuật**, khó khăn lớn nhất là đánh giá đầu ra AI một cách nhất quán. Một kết quả diễn đạt rõ ràng và có nguồn trích dẫn vẫn có thể gom sai chủ đề hoặc xếp hạng không đúng nhu cầu của lớp. Tôi phải đối chiếu từng tiêu chí thay vì chỉ đánh giá câu trả lời có vẻ hợp lý.

Trong báo cáo kiểm thử của nhóm, case `norm_003` ghi nhận chủ đề của một học viên hỏi nhiều lần được xếp trên chủ đề có ba học viên khác nhau cùng hỏi. Lỗi này ảnh hưởng trực tiếp đến mục tiêu nhận biết khó khăn chung của lớp. Ngoài ra, việc sửa prompt có thể giải quyết một lỗi nhưng làm xuất hiện lại lỗi khác, nên cần kiểm thử lại cả bộ case.

**Về phối hợp nhóm**, thách thức là thống nhất cách hiểu kết quả kỳ vọng giữa phần workflow, prompt và test case. Tôi cần ghi rõ đầu vào, đầu ra thực tế và lý do chưa đạt để phản hồi có thể được sử dụng cho việc điều chỉnh.

**Về thời gian và phạm vi**, tôi phải cân đối khảo sát với các vòng kiểm thử trong thời lượng hackathon. Mẫu khảo sát cũng chủ yếu là học viên, trong khi người dùng chính là giảng viên và TA. Đây là giới hạn cần thừa nhận khi sử dụng kết quả để định hướng sản phẩm.

### 3. Học được gì

Tôi học được cách chuyển phản hồi khảo sát thành yêu cầu sản phẩm và tiêu chí kiểm thử. Trong 23 phản hồi, 22 người yêu cầu dẫn nguồn chính xác và 12 người yêu cầu đếm theo số học viên độc lập. Những ý kiến này giúp tôi xác định rõ cần chú ý đến nguồn trích dẫn và ảnh hưởng của câu hỏi lặp.

Một phản hồi từ nhóm TA/Mentor/Lab Coach đặt câu hỏi về nguồn chatlog và cho biết nhiều tương tác diễn ra trực tiếp với giảng viên. Tôi nhận ra dữ liệu chat chỉ phản ánh một phần tình hình học tập. Hệ thống cần trình bày kết quả như tín hiệu hỗ trợ để người dạy cân nhắc.

Qua kiểm thử, tôi hiểu rằng cải thiện prompt cần dựa trên bằng chứng. Theo báo cáo evaluation, kết quả chung của nhóm tăng từ 10/19 case đạt ở baseline lên 15/19 ở v1.2, nhưng purity giảm từ 0,8438 ở v1.1 xuống 0,7179 ở v1.2. Điều này cho thấy tỷ lệ PASS tăng chưa có nghĩa mọi khía cạnh đều tốt hơn.

Tôi cũng cải thiện kỹ năng ghi log và trao đổi trong nhóm. Phản hồi có case cụ thể, kết quả kỳ vọng và lý do đánh giá giúp việc sửa lỗi rõ ràng hơn. Tôi học được rằng cần phân biệt nguồn trích dẫn tồn tại với nguồn thực sự hỗ trợ đúng kết luận của AI.

### 4. Điều muốn làm khác

Nếu được làm lại, tôi sẽ ưu tiên khảo sát thêm giảng viên và TA. Tôi sẽ hỏi về một lần chuẩn bị ôn tập gần nhất, cách họ thực hiện và khó khăn cụ thể trước khi giới thiệu giải pháp, nhằm thu thập trải nghiệm thực tế và hạn chế câu hỏi dẫn dắt.

Tôi cũng muốn tổ chức dùng thử sớm hơn. Phản hồi tích cực về ý tưởng chưa chứng minh sản phẩm giúp người dùng hoàn thành công việc tốt hơn. Cần quan sát thao tác, ghi nhận điểm vướng và đo thời gian thực hiện tác vụ.

Về quy trình, tôi sẽ thống nhất tiêu chí PASS/FAIL trước khi chỉnh prompt, lưu phiên bản prompt cùng cấu hình model và log của từng lượt chạy. Sau mỗi thay đổi, cần kiểm thử lại toàn bộ bộ case; các tình huống quan trọng nên chạy nhiều lượt để đánh giá độ ổn định.

Về kỹ thuật, tôi sẽ đề xuất kiểm tra riêng các bước có quy tắc rõ ràng như lọc preset, khử trùng lặp và đếm học viên, sau đó đánh giá phần suy luận của model. Cách này giúp xác định lỗi đến từ xử lý dữ liệu hay từ prompt để lựa chọn cách sửa phù hợp.

### 5. Đánh giá sản phẩm

**Điểm mạnh** của VLearn Pulse là có bài toán và người dùng mục tiêu rõ ràng. Sản phẩm hỗ trợ giảng viên, TA tổng hợp câu hỏi thành các nội dung cần xem xét ôn tập, có học liệu để đối chiếu và bản nháp thẻ ôn để chỉnh sửa. Người dạy vẫn giữ quyền kiểm tra và quyết định sử dụng.

Khảo sát cho thấy sự quan tâm ban đầu: 15/23 người đánh giá bảng điểm nghẽn rất hữu ích và 19/23 người đánh giá bản nháp thẻ ôn rất cần thiết. Tuy nhiên, đây là phản hồi dựa trên mô tả giải pháp, chưa phải kết quả dùng thử.

**Điểm yếu cần cải thiện** là độ ổn định của việc gom nhóm, xếp hạng và xử lý các trường hợp thiếu thông tin. Bộ eval prompt hiện có 19 case, mỗi phiên bản chạy một lượt cho mỗi case, nên chưa đại diện cho chất lượng toàn bộ ứng dụng. Nhóm cũng cần đánh giá sâu hơn mức độ phù hợp của nguồn trích dẫn với nội dung được đề xuất.

**Về khả năng ứng dụng thực tế**, tôi đánh giá VLearn Pulse có tiềm năng trong các lớp có nhiều dữ liệu hỏi đáp qua chat. Để sử dụng thực tế, nhóm cần tiếp tục kiểm thử toàn luồng, thu thập phản hồi từ giảng viên/TA và đo hiệu quả thực hiện tác vụ. Sản phẩm phù hợp với vai trò trợ lý hỗ trợ người dạy, còn nội dung đưa vào lớp học cần được con người kiểm tra và duyệt.
