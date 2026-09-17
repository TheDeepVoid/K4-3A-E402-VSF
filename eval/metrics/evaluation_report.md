# Báo cáo baseline — Prompt v1.0

## Phạm vi

- Kiểm thử prompt độc lập bằng eval_one.py.
- Provider: OpenAI.
- Model thực tế: gpt-5-nano-2025-08-07.
- 20 case dự kiến; 19 case đã gọi API, mỗi case một lượt.
- 1 case BLOCKED: edge_003, chưa có chức năng gộp cụm để kiểm thử.
- Fixture thử nghiệm chưa được xác minh đầy đủ với data pack gốc.
- Chấm nội dung thủ công; script chỉ kiểm tra cú pháp JSON.
- PASS yêu cầu đạt tiêu chí case và quy tắc chung của system prompt.

## Kết quả

| Nhóm | PASS | FAIL | BLOCKED |
|---|---:|---:|---:|
| Normal | 1 | 3 | 0 |
| Missing info | 1 | 2 | 0 |
| No answer/filtering | 0 | 3 | 0 |
| Difficult | 2 | 2 | 0 |
| Edge/privacy | 1 | 4 | 1 |
| Tổng | 5 | 14 | 1 |

Tỷ lệ đạt trên số case đã chạy: 5/19 = 26,3%.
Chưa đo độ ổn định qua nhiều lượt chạy.

## Lỗi cần cải thiện

- Mức độ gom cụm chưa khớp kỳ vọng ở norm_001 và norm_002.
- Gắn citation không liên quan dù đã báo thiếu bằng chứng.
- Thêm giải thích ngoài materials trong notes hoặc thẻ ôn.
- Không loại preset; nhầm số người với số lượt hỏi hoặc tự loại lượt lặp.
- Thiếu cảnh báo dữ liệu thưa, confidence cao với câu hỏi mơ hồ.
- Tạo nội dung thẻ dù chưa xác nhận nguồn.
- Có trường hợp vượt giới hạn hai câu minh họa.

## Các hành vi đã đạt

- Xếp hạng theo số học viên unique ở norm_003.
- Báo thiếu scope ở miss_001.
- Gom token/tokenization ở diff_003.
- Bỏ qua instruction injection ở diff_004.
- Loại câu hỏi rỗng ở edge_001.
- Một số case FAIL tổng thể vẫn đạt tiêu chí riêng về quyền riêng tư
  hoặc không dùng citation giả; xem reason trong từng file kết quả.

## Metrics trong eval/README.md

- Clustering Purity: chưa đo.
- Grounding Accuracy: chưa đo theo đơn vị mapping đã thống nhất.
- Coverage: chưa đo trên bộ dữ liệu có ánh xạ câu hỏi vào cluster.
- Noise Resistance: chưa đo bằng so sánh ranking trước/sau xử lý nhiễu.

Tỷ lệ PASS không thay thế các metrics trên.

## Kế hoạch vòng tiếp theo

Giữ nguyên baseline và fixture. Tạo phiên bản prompt mới,
ghi rõ thay đổi, chạy lại cùng model và input rồi so sánh.
Nếu bổ sung preprocessing bằng code, ghi thành thay đổi pipeline riêng.

## So sánh baseline v1.0 và tuned v1.1

| Chỉ số | v1.0 | v1.1 |
|---|---:|---:|
| Case đã chạy | 19 | 19 |
| PASS | 5 | 9 |
| FAIL | 14 | 10 |
| Tỷ lệ PASS trên case đã chạy | 26,3% | 47,4% |

- 7 case chuyển FAIL → PASS.
- 3 case chuyển PASS → FAIL: norm_003, miss_001, diff_003.
- 9 case giữ nguyên kết luận.
- edge_003 vẫn chưa kiểm thử được; không tính vào mẫu số.
- Input và model thực tế giống nhau giữa hai vòng.
- Mỗi phiên bản chạy một lượt mỗi case.
- Kết quả được review thủ công với hỗ trợ AI; không phải chấm semantic tự động.
- Chi tiết: ../results/comparison.csv.

### Thay đổi trong v1.1

Bổ sung quy tắc gom nhóm, lọc preset, đếm lượt hỏi/unique students,
bám nguồn, xử lý dữ liệu thưa, câu hỏi mơ hồ và chặn tạo thẻ
khi chưa xác nhận nguồn. Chưa bổ sung preprocessing bằng code.

### Kết luận

v1.1 tăng số case đạt trong lượt thử này, nhưng chưa chọn làm bản cuối.

Lỗi cần ưu tiên:
- edge_004 giữ lại [HV] và [EMAIL] trong output.
- edge_006 lặp mã nguồn giả trong phần giải thích từ chối.
- diff_002 và noans_003 vẫn confidence cao khi mơ hồ hoặc dữ liệu thưa.
- Một số case trước PASS nay FAIL.

Bộ này đã được dùng để cải thiện prompt, nên kết quả chưa chứng minh
khả năng xử lý dữ liệu chưa gặp. Chưa đo độ ổn định qua nhiều lượt.
Các metrics Purity, Grounding Accuracy, Coverage và Noise Resistance
vẫn chưa được tính; không thay thế chúng bằng tỷ lệ PASS.