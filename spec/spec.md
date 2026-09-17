# AI SPEC — VLearn Pulse · Nhóm [??] · Zone [X]
Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ):
  Giảng viên chuẩn bị bài giảng tiếp theo → xem VLearn Pulse để xác định 5 điểm nghẽn → quyết định ôn tập chủ đề nào
- Core JTBD (không tên sản phẩm/AI trong câu):
  Giảng viên cần nhanh chóng xác định các điểm kiến thức mà lớp học đang gặp khó khăn để điều chỉnh kế hoạch giảng dạy.
- Problem statement (KHÔNG chữ AI):
  Giảng viên bỏ ra nhiều thời gian để phân tích hàng nghìn câu hỏi học viên để tìm ra 5 điểm trọng tâm cần ôn tập, mà không có công cụ tự động hóa và có bằng chứng từ học liệu.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = 448 học viên, 3.097 lượt hỏi từ cohort K4):
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    * "Cái này em không hiểu lắm, anh có thể giải thích lại được không?" (tutor_turns.csv, dòng 145)
    * "Slide trang 45 mình chưa nắm rõConcept X" (tutor_turns.csv, dòng 203)
    * "Em không biết làm bài tập này như thế nào" (tutor_turns.csv, dòng 312)
    * "Về phần này em vẫn còn thắc mắc" (tutor_turns.csv, dòng 401)
    * "Có thể giải thích chi tiết hơn về Y không ạ?" (tutor_turns.csv, dòng 558)

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):
  | Ứng viên | Số người affected | Tần suất | Chi phí mỗi lần | Khả thi |
  |---|---|---|---|---|
  | VLearn Pulse ('’idée hiện tại) | 50 giảng viên + 1000 học viên | Mỗi bài giảng | Thấp (sử dụng LLM hiện có) | Cao |
  | Tutor AI cá nhân hóa | 1000 học viên | Mỗi câu hỏi | Trung bình (cần mô hình phức tạp) | Trung bình |
  | Dashboard phân tích học viên | 50 giảng viên | Tuần trung bình | Trung bình (cần ETL) | Cao |
- Ứng viên ĐÃ LOẠI + vì sao:
  - Tutor AI cá nhân hóa: Chi phí cao, khả thi trung bình, không giải quyết trực tiếp vấn đề giảng viên cần biết điểm nghẽn.
  - Dashboard phân tích học viên: Tập trung vào học viên thay vì giảng viên, không cung cấp khuyến nghị hành động cụ thể.
- Ứng viên CHỌN + vì sao (bằng số):
  - VLearn Pulse: Giải quyết trực tiếp JTBD của giảng viên, tác động đến cả giảng viên và học viên, chi phí thấp, khả thi cao. Dựa trên eval: 15/19 case ĐẬU (78,9%) và độ accurarcy grounding 100%.

## §3. Giải pháp tương tự đã nghiên cứu
- [Sản phẩm 1]: Khan Academy Missions — flow: đề xuất bài tập dựa trên lỗi học sinh; đáng học: sử dụng dữ liệu học sinh để cá nhân hóa; đáng né: tập trung vào học sinh, khôngให้ bằng chứng từ giảng dạy; mình khác gì: tập trung vào giảng viên, sử dụng câu hỏi học viên để tìm điểm nghẽn lớp học, có grounding từ học liệu.
- [Sản phẩm 2]: Century Tech AI — flow: phân tích hiệu suất học sinh và đề xuất hành động; đáng học: sử dụng AI để cân bằng tải trabajo giảng viên; đáng né: đắt tiền, cần tích hợp sâu; mình khác gì: giải pháp nhẹ nhàng, chỉ cần chatlog và học liệu hiện có, không thay đổi hệ thống LTS.

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
  Giảng viên muốn biết 5 điểm lớp đang kẹt để quyết định ôn gì tiếp theo → AI phân tích câu hỏi học viên + học liệu → xuất top 5 điểm nghẽn có trích dẫn, số học viên unique và ví dụ ẩn danh.
- Non-goals (≥3 thứ KHÔNG build):
  - So sánh multi-cohort (khác biệt giữa các lớp)
  - Học viên sử dụng trực tiếp (tương tác với AI để hỏi lại)
  - Triển khai production (scaling đến hàng nghìn giảng viên)
- Mức prototype nhắm tới: [ ] Sketch [x] Mock [ ] Working — phần nào mock: UI (mockup.html), phần nào thật: CLI runner, system prompt LLM, eval script.
- Automation: [x] augment [ ] conditional [ ] automate — lý do theo cost-of-error: AI cung cấp gợi ý bằng chứng, nhưng quyết định cuối cùng thuộc về giảng viên; sai sót dẫn đến ôn tập không trọng tâm có thể được sửa trong lớp sau, chi phí lỗi thấp.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | Có cơ sở bằng chứng | Mỗi điểm nghẽn phải có trích dẫn từ slide/transcript có mã [Txx-NNN] |
  | Có con người trong vòng lặp | Giảng viên có thể sửa đổi cluster, xác nhận nguồn trước khi tạo thẻ ôn |
  | Bảo vệ quyền riêng tư | Không hiển thị student ID, chỉ aggregates và ví dụ ẩn danh |
  | Insight có thể hành động | Output là top 5 điểm nghẽn + thẻ ôn 5 phút để giảng viên 즉시 áp dụng |
  | Prompt có thể mở rộng | Một system prompt duy nhất xử lý clustering, grounding, ranking và generation |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]
| Lớp lỗi | Kịch bản |
|---|---|
| Lỗi nhầm lẫn ý nghĩa (semantic error) | AI gom nhóm câu hỏi về "đạo hàm" và "tích phân" vì có từ chung "hàm", dẫn đến cụm nhầm lẫn |
| Lỗi grounding sai | AI liên kết câu hỏi về "luật bảo vệ" với slide về "luật cung cấp" vì mã [Txx-NNN] giống nhau |
| Lỗi ranking biais | AI ưu tiên cluster có nhiều câu hỏi nhưng từ cùng 1-2 học viên thay vì phân tán trên lớp |
| Lỗi sinh ra không chính xác | Thẻ ôn tạo ra mục tiêu không khớp với trích dẫn hoặc ví dụ không liên quan |
| Lỗi lọc không đầy đủ | Các câu hỏi trước định đặt (preset) không được loại bỏ, ảnh hưởng đến việc xếp hạng |
| Lỗi tư liệu thiếu | Học liệu không mã hóa [Txx-NNN] dẫn đến không thể grounding |
| Lỗi định danh rò rỉ | Vертxem trong output accidentally reveals student ID hoặc nội dung tùy chỉnh |
| Lỗi không ổn định | Nhạy cảm đối với sự thay đổi nhỏ trong prompt dẫn đến kết quả khác nhau mỗi lần chạy |

## §6. Bốn đường đi của trải nghiệm
- Happy path: Giảng viên upload tutor_turns.csv → hệ thống tự động lọc, gom nhóm, grounding, rank → hiển thị top 5 điểm nghẽn với trích dẫn và thẻ ôn → giảng viên chọn một điểm để tạo bài giảng Ôn tập.
- Low-confidence (②): Khi điểm số confidence thấp (<0.6) → hệ thống hiển thị cảnh báo "Kết quả có độ tin cậy thấp, gợi ý kiểm tra lại dữ liệu" và gợi ý thu thập thêm câu hỏi.
- Failure/không căn cứ (①): Khi không đủ dữ liệu (ít hơn 5 câu hỏi sau lọc) → hệ thống hiển thị "Không đủ dữ liệu để phân tích" và đề xuất mở rộng thời gian thu thập.
- Correction (user sửa): Giảng viên chỉnh sửa tên cluster hoặc thay đổi trích dẫn → hệ thống cập nhật lại thẻ ôn và ranking tương ứng.
- Khi bị đòi ngoài phạm vi (③): Học viên hỏi trực tiếp về VLearn Pulse → hệ thống chuyển hướng về vai trò của giảng viên và giải thích công cụ là để hỗ trợ giảng viên.
- Case đặc thù domain (④): Trong các lĩnh vực có học liệu chuyên sâu về công nghệ (ví dụ: mã nguồn) → hệ thống đề xuất sử dụng thêm công cụ để phân tích code nếu cần.

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
  - Chất lượng: Độ hữu ích của top 5 cluster (theo đánh giá giảng viên), độ chính xác grounding (trích dẫn phải thuộc materials), không lộ định danh.
  - Kiểm chứng: Schema output phải khớp, citations phải là subset của materials, không có PII, không có mã nguồn giả.
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
  - Có sẵn 19 case trong `eval/golden_set/` (mỗi case: input chatlog + expected output schema). Mục tiêu đạt ≥20 case sau khi hoàn thiện.
- Quality bar (chốt từ hạn chót spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
  - Chốt từ hạn chót spec: Đạt khi ≥70% case ĐẬU (theo eval v1.2) và grounding accuracy ≥90%.
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):
  | Phiên bản | Ngày | % ĐẬU | Grounding accuracy | Noise resistance (Spearman ρ) |
  |---|---|---|---|---|
  | v1.0 | 10/9 | 52,6% | 80% | 0,85 |
  | v1.1 | 12/9 | 63,2% | 85% | 0,90 |
  | v1.2 | 17/9 | 78,9% | 100% | 1,00 |

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
  - Spec: [Nguyễn Hải Đăng, Nguyễn Thị Mừng]
  - Evidence: [Ngô Gia Quốc, Bùi Thị Ngọc Trân] (thu thập và ghi chú golden set)
  - Prompt: [Ngô Gia Quốc, Bùi Thị Ngọc Trân] (thiết kế và cải thiện system prompt)
  - Code: [Nguyễn Hải Đăng, Ngô Gia Quốc] (chạy `run_cases.py`, duy trì CLI)
  - Demo: [Nguyễn Thị Mừng] (xây dựng mockup và chuẩn bị validation)
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
  - Willing users: GS. Nguyễn Văn A (giảng viên Khoa CNTT), ThS. Trần Thị B (TA lớp K4)
  - Kế hoạch vòng validation: Tuần sau spec freeze, triển khai phiên bản beta với 2 lớp học, thu thập phản hồi qua biểu mẫu và phỏng vấn, tiếp tục cải thiện prompt.
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:
  - Không áp dụng (chỉ một phương án được verfolgen).

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 10/9/2026 | Tạo spec phiên bản v1.0 | Khởi tạo dự đoán ban đầu dựa trên buổi sáng |
| 12/9/2026 | Cập nhật spec v1.1 sau eval đầu tiên | Thêm kết quả eval: 12/19 ĐẬU, điều chỉnh chỉ số |
| 17/9/2026 | Cập nhật spec v1.2 sau eval gần nhất | Cập nhật KPI dựa trên 15/19 ĐẬU, thêm chi tiết về preprocessing |
