# Bộ Test Cases - Bộ Test Vàng

## Các loại

- **Normal** (4): Câu hỏi tiêu chuẩn có câu trả lời rõ ràng
- **Missing Info** (3): Câu hỏi thiếu thông tin cần thiết
- **No Answer** (3): Câu hỏi không có trong ngữ cảnh
- **Difficult** (3): Cần suy luận/tính toán
- **Edge Case** (2): Trường hợp biên

---

## Normal Cases

### norm_001
- **Context**: Dự án bắt đầu năm 2024 với ngân sách $50,000. Đội gồm 5 lập trình viên và 2 designer.
- **Question**: Dự án bắt đầu khi nào?
- **Expected**: 2024
- **Criteria**: Câu trả lời chứa '2024'
- **Tags**: date, basic

### norm_002
- **Context**: Python được tạo bởi Guido van Rossum năm 1991. JavaScript được tạo bởi Brendan Eich năm 1995.
- **Question**: Ai đã tạo ra Python?
- **Expected**: Guido van Rossum
- **Criteria**: Câu trả lời chứa 'Guido van Rossum'
- **Tags**: person, basic

### norm_003
- **Context**: Ứng dụng hỗ trợ ba phương thức thanh toán: thẻ tín dụng, PayPal, chuyển khoản ngân hàng. Thời gian xử lý 2-3 ngày làm việc.
- **Question**: Các phương thức thanh toán được hỗ trợ là gì?
- **Expected**: thẻ tín dụng, PayPal, chuyển khoản ngân hàng
- **Criteria**: Liệt kê đủ ba phương thức
- **Tags**: list, feature

### norm_004
- **Context**: Nhiệt độ hôm nay là 72°F với độ ẩm 65%. Tốc độ gió 10 mph từ hướng tây bắc.
- **Question**: Nhiệt độ hiện tại là bao nhiêu?
- **Expected**: 72
- **Criteria**: Câu trả lời chứa '72'
- **Tags**: number, weather

---

## Missing Info Cases

### miss_001
- **Context**: Cuộc họp được lên lịch vào thứ Ba tuần sau.
- **Question**: Cuộc học lúc mấy giờ?
- **Expected**: cannot determine
- **Criteria**: Nói rõ không xác định được (không bịa thời gian)
- **Tags**: missing, time

### miss_002
- **Context**: Sản phẩm có giá $99.
- **Question**: Phí vận chuyển là bao nhiêu?
- **Expected**: cannot determine
- **Criteria**: Nói rõ không có thông tin phí vận chuyển
- **Tags**: missing, price

### miss_003
- **Context**: Đánh giá sự hài lòng của người dùng là 4.5/5.
- **Question**: Có bao nhiêu người dùng được khảo sát?
- **Expected**: cannot determine
- **Criteria**: Không bịa số lượng
- **Tags**: missing, count

---

## No Answer Cases

### noans_001
- **Context**: Công ty được thành lập năm 2010. Doanh thu tăng đều đặn trong 5 năm.
- **Question**: Giá cổ phiếu là bao nhiêu?
- **Expected**: cannot determine
- **Criteria**: Nói không xác định được (không bịa giá)
- **Tags**: missing, financial

### noans_002
- **Context**: Cơ sở dữ liệu chứa 1 triệu bản ghi. Tần suất backup hàng ngày lúc nửa đêm.
- **Question**: Ai là CEO?
- **Expected**: cannot determine
- **Criteria**: Nói rõ không có thông tin CEO
- **Tags**: missing, person

### noans_003
- **Context**: Thuật toán có độ phức tạp thời gian O(n log n).
- **Question**: Bộ nhớ sử dụng là bao nhiêu?
- **Expected**: cannot determine
- **Criteria**: Không bịa mức bộ nhớ
- **Tags**: missing, technical

---

## Difficult Cases

### diff_001
- **Context**: Dự án có timeline: Giai đoạn 1 (T1-T3), Giai đoạn 2 (T4-T6), Giai đoạn 3 (T7-T9). Giai đoạn 2 bị chậm 2 tuần.
- **Question**: Giai đoạn 3 bắt đầu khi nào?
- **Expected**: Tháng 7
- **Criteria**: Tính đúng thời gian bắt đầu giữa tháng 7 dù bị chậm
- **Tags**: date, calculation

### diff_002
- **Context**: Cấu trúc giảm giá: 10% cho đơn trên $100, 15% cho đơn trên $500, 20% cho đơn trên $1000. Khách hàng có đơn $1200 nhưng dùng coupon $200.
- **Question**: Giảm giá nào được áp dụng?
- **Expected**: 20%
- **Criteria**: Xử lý đúng tương tác coupon
- **Tags**: logic, edge

### diff_003
- **Context**: Version 2.0 phát hành tháng 3. Version 2.1 tháng 5. Version 3.0 tháng 8. Bug reports: v2.0 (50), v2.1 (30), v3.0 (80).
- **Question**: Phiên bản nào có nhiều bugs nhất?
- **Expected**: 3.0
- **Criteria**: Xác định đúng v3.0 dù là phiên bản mới nhất
- **Tags**: analysis, comparison

---

## Edge Cases

### edge_001
- **Context**: (trống)
- **Question**: Thủ đô của Pháp là gì?
- **Expected**: cannot determine
- **Criteria**: Xử lý ngữ cảnh trống tốt
- **Tags**: empty, boundary

### edge_002
- **Context**: Đáp án là42.
- **Question**: Đáp án là gì?
- **Expected**: 42
- **Criteria**: Xử lý định dạng bất thường (không có dấu cách sau 'là')
- **Tags**: format, parsing