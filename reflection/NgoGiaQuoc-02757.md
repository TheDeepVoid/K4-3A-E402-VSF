# Reflection cá nhân — Ngô Gia Quốc (02757)

## 1. Vai trò và công việc đảm nhận

Trong hackathon VLearn Pulse, tôi tập trung vào việc làm rõ định hướng sản phẩm, xây dựng trải nghiệm giao diện ban đầu và hoàn thiện phần prompt/test để hệ thống AI tạo kết quả an toàn, có thể kiểm chứng.

Các công việc cụ thể tôi đã thực hiện:

- Cập nhật tài liệu đề tài, làm rõ bài toán VLearn Pulse hỗ trợ giảng viên/TA phát hiện các nội dung học viên cần ôn lại từ chatlog và học liệu.
- Xây dựng, cập nhật mockup giao diện cho luồng sử dụng chính: chọn phạm vi phân tích, xem các cụm nội dung cần ôn, xác nhận nguồn học liệu và tạo thẻ ôn 5 phút.
- Cập nhật `system_prompt.md` để định nghĩa rõ vai trò của AI là hỗ trợ giảng viên tạo đề xuất/bản nháp, không thay thế quyết định của giảng viên.
- Bổ sung và chỉnh sửa `test_cases.md` với các tình huống normal, thiếu thông tin, dữ liệu thưa, prompt injection, citation giả và bảo vệ quyền riêng tư.
- Tham gia kiểm tra cấu hình gọi model và ghi nhận các lỗi thực tế khi đổi provider/model, đặc biệt là lỗi không tương thích tham số token và vượt context window.

Tôi ước tính thời gian đóng góp khoảng **25%** tổng khối lượng công việc cá nhân của dự án, chủ yếu ở các phần product design, prompt design, test design và kiểm tra tích hợp.

## 2. Thách thức gặp phải

### Khó khăn kỹ thuật

Một thách thức quan trọng là việc các provider/model không hoàn toàn tương thích dù cùng dùng giao diện API gần giống OpenAI. Khi chạy thử, hệ thống gặp lỗi `max_tokens` không được một số model hỗ trợ và cần dùng `max_completion_tokens`. Ngoài ra, có trường hợp request vượt giới hạn context 128.000 tokens do đồng thời gửi nhiều học liệu, câu hỏi, tool schema và ngân sách output lớn.

Điều này cho thấy việc tích hợp LLM không chỉ là thay model trong cấu hình. Cần quản lý rõ provider, endpoint, tham số token, kích thước input và chiến lược cắt/chọn context.

### Khó khăn về teamwork

Dự án có nhiều phần phụ thuộc nhau: UI cần phản ánh đúng output schema; prompt phải thống nhất với test cases; pipeline/tool calling phải bảo đảm số liệu và citation đáng tin cậy. Vì vậy, việc thống nhất contract dữ liệu giữa các thành viên là cần thiết để tránh giao diện kỳ vọng một định dạng nhưng model hoặc backend trả về định dạng khác.

### Khó khăn về thời gian và scope

Trong phạm vi hackathon, nhóm cần vừa làm được luồng sản phẩm trực quan vừa bảo đảm các yêu cầu an toàn như ẩn danh dữ liệu, không bịa citation và yêu cầu giảng viên xác nhận nguồn trước khi tạo thẻ ôn. Scope này khá rộng, nên cần ưu tiên các luồng cốt lõi thay vì cố xây tất cả tính năng nâng cao ngay từ đầu.

## 3. Học được gì

### Kỹ năng mới

Tôi học thêm về cách thiết kế system prompt có ràng buộc rõ ràng: phân biệt dữ liệu đầu vào với chỉ thị, giới hạn citation theo đúng `materials`, và không để dữ liệu chứa prompt injection làm thay đổi hành vi của model.

Tôi cũng hiểu rõ hơn về cách viết test case cho sản phẩm AI. Test không chỉ kiểm tra câu trả lời “đúng” mà còn phải kiểm tra các lỗi nguy hiểm như lộ định danh học viên, đếm sai số học viên unique, bịa nguồn, suy diễn khi dữ liệu thưa và tạo nội dung khi chưa đủ điều kiện xác nhận.

### Hiểu biết về AI và phát triển sản phẩm

VLearn Pulse cho tôi thấy một sản phẩm AI tốt cần đặt con người trong vòng kiểm duyệt. AI phù hợp để tổng hợp tín hiệu và tạo bản nháp, còn giảng viên là người xác minh cụm nội dung, nguồn học liệu và quyết định sử dụng thẻ ôn.

Tôi cũng nhận ra context management là vấn đề quan trọng khi làm việc với LLM. Gửi toàn bộ dữ liệu vào prompt có thể làm vượt giới hạn context, chậm và tốn chi phí. Một hướng tốt hơn là lọc theo phạm vi, chỉ chọn các đoạn học liệu liên quan và đặt giới hạn output phù hợp.

### Làm việc nhóm

Tôi học được rằng tài liệu mô tả sản phẩm, mockup, prompt, schema và test case cần được phát triển đồng bộ. Khi các thành phần này cùng mô tả một workflow thống nhất, việc tích hợp và đánh giá sản phẩm sẽ rõ ràng hơn.

## 4. Điều muốn làm khác

Nếu được làm lại, tôi sẽ ưu tiên xác định sớm một contract kỹ thuật chung cho provider/model, bao gồm endpoint, tham số token hợp lệ, giới hạn context và cấu hình fallback. Điều này sẽ giảm thời gian xử lý lỗi khi chuyển model hoặc provider.

Về process, nhóm có thể thực hiện đánh giá theo test cases sớm hơn và sau mỗi thay đổi lớn của prompt hoặc pipeline. Kết quả eval nên được ghi nhận theo từng model/provider để phát hiện lỗi tương thích và regression.

Về kỹ thuật, tôi sẽ đề xuất tách dữ liệu học liệu thành các đoạn nhỏ có metadata, sau đó truy xuất/chọn các đoạn liên quan trước khi gọi model thay vì gửi một lượng transcript lớn trong mọi request. Cách này giúp giảm lỗi vượt context window, tốc độ phản hồi và chi phí sử dụng API.

## 5. Đánh giá sản phẩm

### Điểm mạnh của VLearn Pulse

- Giải quyết một nhu cầu thực tế: giúp giảng viên nhìn thấy các chủ đề học viên đang cần xem lại từ lượng lớn câu hỏi trong lớp.
- Đặt quyền riêng tư lên trước: không hiển thị mã học viên, thông tin liên hệ hoặc lịch sử của một cá nhân.
- Có cơ chế grounding: cụm nội dung chỉ được gắn citation khi có bằng chứng trong học liệu đã cung cấp.
- Có human-in-the-loop: thẻ ôn chỉ là bản nháp và cần giảng viên xác nhận nguồn, chỉnh sửa rồi phê duyệt.
- Có bộ test bao phủ cả chất lượng đầu ra lẫn các tình huống an toàn và biên.

### Điểm yếu cần cải thiện

- Khả năng tương thích giữa các provider/model vẫn cần được chuẩn hóa tốt hơn, đặc biệt với tham số token và function calling.
- Cần có cơ chế quản lý context hiệu quả hơn để tránh gửi input quá dài.
- Chất lượng clustering và grounding nên được đánh giá thêm trên dữ liệu thực tế đa dạng hơn.
- UI hiện cần tiếp tục cải thiện trạng thái lỗi, phản hồi tiến trình và cách cho giảng viên điều chỉnh/duyệt kết quả.

### Khả năng ứng dụng thực tế

VLearn Pulse có khả năng ứng dụng trong các lớp học có nhiều tương tác qua chat, đặc biệt khi giảng viên khó tự đọc toàn bộ câu hỏi của học viên. Nếu tiếp tục hoàn thiện phần tích hợp dữ liệu, đánh giá chất lượng trên dữ liệu thực và cơ chế quản trị quyền truy cập, sản phẩm có thể trở thành công cụ hỗ trợ giảng dạy hữu ích: giúp giảng viên phát hiện nội dung cần ôn, chuẩn bị micro-learning nhanh hơn và vẫn giữ quyền quyết định cuối cùng cho con người.
