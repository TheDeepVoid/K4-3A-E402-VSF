# Bộ Test Cases - VLearn Pulse

## Các loại Test

- **Normal** (4): Input hợp lệ, output đúng format
- **Missing Info** (3): Thiếu metadata, input không đầy đủ
- **No Answer** (3): Không tìm được học liệu liên quan
- **Difficult** (3): Câu hỏi mơ hồ, nhiều khái niệm, edge cases
- **Edge Case** (2): Input đặc biệt, boundary conditions

---

## Normal Cases

### norm_001
- **Input**: Câu hỏi: "Em không hiểu cách tính đạo hàm của hàm hợp"
- **Context**: Transcript [T02-015]: "Đạo hàm của hàm hợp f(g(x)) = f'(g(x)) · g'(x)"
- **Expected**: Phân loại đúng khái niệm "chain rule", liên kết [T02-015]
- **Criteria**: Output chứa "chain rule" và mã học liệu

### norm_002
- **Input**: Danh sách 10 câu hỏi từ 5 học viên khác nhau về cùng chủ đề
- **Context**: 5 học viên hỏi về "numpy array indexing" trong 1 tuần
- **Expected**: Gom thành 1 cluster với count=5, unique_students=5
- **Criteria**: Cluster đúng, không trùng lặp

### norm_003
- **Input**: Câu hỏi có mã [T03-022] trong transcript
- **Context**: Slide [T03-022]: "Pandas DataFrame merge types: inner, outer, left, right"
- **Expected**: Ground đúng đến [T03-022] và slide về merge
- **Criteria**: Trích dẫn đúng mã nguồn

### norm_004
- **Input**: Yêu cầu tạo thẻ ôn cho cluster "list comprehension"
- **Context**: 8 câu hỏi về list comprehension, nguồn [T01-030] đến [T01-035]
- **Expected**: Thẻ ôn có: tên, mục tiêu, hiểu nhầm, trích đoạn, câu kiểm tra
- **Criteria**: Đầy đủ 5 thành phần

---

## Missing Info Cases

### miss_001
- **Input**: Câu hỏi không có cohort_hint
- **Context**: Có câu hỏi và transcript nhưng thiếu cohort_hint
- **Expected**: Báo lỗi hoặc warning, không hallucinate
- **Criteria**: Nói rõ thiếu thông tin

### miss_002
- **Input**: Câu hỏi nhưng không có transcript/slide liên quan
- **Context**: Câu hỏi hợp lệ nhưng không tìm được học liệu
- **Expected**: "Không tìm thấy học liệu liên quan"
- **Criteria**: Không bịa đoạn transcript

### miss_003
- **Input**: student ID bị thiếu trong metadata
- **Context**: Có câu hỏi nhưng không biết là học viên nào
- **Expected**: Xử lý được, không crash
- **Criteria**: Vẫn tính được frequency nhưng đánh dấu unknown student

---

## No Answer Cases

### noans_001
- **Input**: Câu hỏi hoàn toàn ngoài syllabus
- **Context**: Hỏi về "quantum computing" trong khóa Python cơ bản
- **Expected**: Không cluster, hoặc cluster với confidence thấp
- **Criteria**: Không gán vào các cluster chính

### noans_002
- **Input**: Câu hỏi tiếng Anh không có phiên bản tiếng Việt
- **Context**: Câu hỏi bằng tiếng Anh không có asked_at_vn
- **Expected**: Vẫn xử lý được, hoặc báo cần human review
- **Criteria**: Không lỗi, handle gracefully

### noans_003
- **Input**: Câu hỏi preset (is_preset=true) cần lọc
- **Context**: Câu hỏi mẫu từ hệ thống, không phải học viên thật
- **Expected**: Được lọc ra, không tính vào cluster
- **Criteria**: Không nằm trong kết quả cuối

---

## Difficult Cases

### diff_001
- **Input**: Câu hỏi về nhiều khái niệm cùng lúc
- **Context**: "Em không hiểu pandas merge và join khác gì nhau?"
- **Expected**: Tách thành 2 cluster riêng hoặc 1 cluster với note
- **Criteria**: Xử lý multi-concept đúng

### diff_002
- **Input**: Câu hỏi mơ hồ, có thể thuộc nhiều cluster
- **Context**: "Hàm này chạy không đúng" - không rõ là syntax hay logic
- **Expected**: Gán confidence thấp hoặc ask clarifying
- **Criteria**: Không gán confidence cao khi không chắc

### diff_003
- **Input**: Cùng khái niệm nhưng từ ngữ khác nhau
- **Context**: "list comprehension" vs "list comprehension trong Python" vs "[x for x in list]"
- **Expected**: Gom thành 1 cluster
- **Criteria**: Semantic similarity hoạt động đúng

---

## Edge Cases

### edge_001
- **Input**: Câu hỏi trống hoặc chỉ có whitespace
- **Context**: ""
- **Expected**: Skip, không crash
- **Criteria**: Handle gracefully

### edge_002
- **Input**: Duplicate câu hỏi từ cùng học viên
- **Context**: Cùng 1 học viên hỏi 3 lần cùng 1 câu
- **Expected**: Chỉ count 1 lần (dedup by student)
- **Criteria**: unique_students đúng, frequency có thể cao hơn

### edge_003
- **Input**: Tên khái quá dài hoặc có ký tự đặc biệt
- **Context**: Cluster name: "The difference between Python's list comprehension and JavaScript's array.map() method"
- **Expected**: Vẫn xử lý được, có thể rút gọn
- **Criteria**: Không lỗi