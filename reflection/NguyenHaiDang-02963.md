### 1. Vai trò và công việc đảm nhận
- Vai trò chính trong nhóm: Thành viên đóng vai trò lập trình viên backend và DevOps, chịu trách nhiệm thiết lập cơ sở hạ tầng AI provider, tối ưu hóa chi phí mô hình và duy trì chất lượng mã nguồn.
- Các task cụ thể đã làm:
  * Xây dựng lớp trừu tượng cho các nhà cung cấp AI và triển khai cho OpenAI, Gemini, OpenRouter, và OmniRoute.
  * Phát triển hệ thống mẫu cho system prompt và test cases.
  * Xây dựng khung đánh giá để tải test cases và chạy đánh giá.
  * Cấu hình biến môi trường và các phần phụ thuộc.
  * Nghiên cứu và chọn các mô hình có chi phí thấp nhất vẫn còn được cung cấp cho mỗi nhà cung cấp để giảm chi phí trong quá trình demo và đánh giá.
  * Cập nhật tài liệu để phản ánh trạng thái hiện tại của dự án, bao gồm bản dịch tiếng Việt.
  * Loại bỏ các tệp không sử dụng và các phần phụ thuộc để dọn dẹp kho lưu trữ.
  * Sửa nhà cung cấp Gemini để sử dụng thư viện mới nhất và loại bỏ cơ chế retry cũ.
  * Sửa script đánh giá để xử lý đầu ra null và ngăn chặn sự cố.
  * Xác minh công cụ bằng cách chạy các tự kiểm tra và quy trình đánh giá.
- Thời gian đầu tư (ước tính %): 40% cho việc thiết lập ban đầu, 30% cho tối ưu hóa mô hình, 30% cho dọn dẹp và sửa lỗi.

### 2. Thách thức gặp phải
- Khó khăn kỹ thuật:
  * Xử lý các thư viện đã lỗi thời (ví dụ: google.generativeai cho Gemini) và di chuyển sang phiên bản hiện tại.
  * Đảm bảo khả năng tương thích khi chuyển sang các mô hình rẻ nhất có thể có khả năng khác nhau.
  * Quản lý các thay đổi API và sự ngừng cung cấp trên nhiều nhà cung cấp AI khác nhau.
- Khó khăn về teamwork:
  * Điều phối các thay đổi để tránh xung đột khi nhiều thành viên đang làm việc trên các phần interconnected (ví dụ: thay đổi ID mô hình ảnh hưởng đến cả script demo và đánh giá).
  * Giữ tài liệu luôn được cập nhật theo các thay đổi nhanh.
- Khó khăn về thời gian/scope:
  * Cân bằng giữa việc thêm tính năng mới (như nhà cung cấp mới) và ổn định mã nguồn hiện có.
  * Thời gian dành để nghiên cứu giá mô hình và trang ngừng cung cấp bị sott-estimated.

### 3. Học được gì
- Kỹ năng mới:
  * Làm việc với nhiều API của nhà cung cấp AI và hiểu những tinh túy của chúng.
  * Triển khai cơ chế retry lũy thừa mà không cần phụ thuộc ngoài.
  * Quản lý biến môi trường và cấu hình cho các kịch bản triển khai khác nhau.
- Hiểu biết về AI/product development:
  * Tầm quan trọng của việc theo dõi sự ngừng cung cấp và biến động chi phí trong các ứng dụng có AI.
  * Cách thiết kế lớp trừu tượng nhà cung cấp linh hoạt để dễ dàng thay đổi nền tảng AI sau.
  * Kỹ thuật đánh giá cho sản phẩm AI, bao gồm việc thiết lập các test case vàng và chấm điểm các lần chạy.
- Làm việc nhóm:
  * Sử dụng phát triển dựa trên agent tuần tự để chia nhỏ các nhiệm vụ phức tạp.
  * Giá trị của tài liệu rõ ràng và thông báo cam kết cho việc hợp tác bất đồng bộ.
  * Thực hành xem lại mã thông qua pull request để duy trì chất lượng.

### 4. Điều muốn làm khác
- Nếu được làm lại, sẽ thay đổi gì?
  * Giới thiệu tích hợp liên tục sớm để bắt đầu những thay đổi gây vỡ từ các cập nhật của nhà cung cấp.
  * Sử dụng hệ thống quản lý cấu hình cho ID mô hình thay vì hardcoding trong các script.
  * Cấp phát thêm thời gian để kiểm tra tự động cho các triển khai nhà cung cấp.
- Process nào có thể cải thiện?
  * Triển khai mẫu chuẩn untuk bàn giao agent để giảm thiểu mất mát kiến thức.
  * Lên lịch các cuộc họp đồng bộ thường xuyên để thảo luận về những thay đổi đang diễn ra và các sự phụ thuộc.
  * Sử dụng hệ thống theo dõi vấn đề để quản lý công việc và lỗi một cách rõ ràng hơn.
- Technical decision nào có thể khác?
  * Xem xét sử dụng hệ thống cờ tính năng để kiểm tra các mô hình mới mà không thay đổi cấu hình mặc định.
  * Trừu tượng hóa logic lựa chọn mô hình vào một dịch vụ riêng để tránh việc rải rác ID mô hình trên toàn bộ mã nguồn.

### 5. Đánh giá sản phẩm
- Điểm mạnh của VLearn Pulse:
  * Kiến trúc linh hoạt hỗ trợ nhiều nhà cung cấp AI với cơ chế dự phòng.
  * Khung đánh giá toàn diện cho phép đo lường hiệu suất trên các mô hình khác nhau.
  * Tài liệu rõ ràng và hướng dẫn cài đặt giúp bắt đầu nhanh chóng.
- Điểm yếu cần cải thiện:
  * Đánh giá hiện tại có thể không bao gồm các trường hợp biên của truy vấn người dùng.
  * Giao diện người dùng (nếu có) không được chi tiết trong các nhật ký, vì vậy chúng tôi giả sử đây là một nỗ lực riêng; sự tập trung nhiều hơn vào giao diện người dùng có thể cải thiện việc được chấp nhận.
  * Sự phụ thuộc vào API bên ngoài gây ra biến động; việc lưu trữ trong cache hoặc dự phòng cục bộ có thể được xem xét.
- Khả năng ứng dụng thực tế:
  * Sản phẩm thể hiện một nền tảng vững chắc cho một trợ lý học tập được cấp độ AI có thể thích nghi với các phụ trợ AI khác nhau dựa trên chi phí và sự sẵn có.
  * Với sự phát triển tiếp theo, nó có thể được mở rộng để xử lý nhiều môn học và tích hợp với các hệ thống quản lý học tập.