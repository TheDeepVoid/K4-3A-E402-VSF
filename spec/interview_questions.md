# Câu Hỏi Phỏng Vấn Live — VLearn Pulse (Đề tài A2)

> Dùng cho vòng demo/chấm điểm. Mỗi câu hỏi bao gồm mục đích kiểm tra và gợi ý đáp án kỳ vọng.

---

## Nhóm 1: Hiểu vấn đề & Pain Point

**Q1. Tại sao không dùng `rating` hay `understanding_level` làm tín hiệu chính để xác định điểm nghẽn?**

> Kiểm tra: nhóm có thực sự đọc và hiểu dữ liệu không.

Kỳ vọng: Rating chỉ có 177/13.494 lượt (1,3%), `understanding_level` gần như trống với 20 lượt — cả hai đều quá thưa để đại diện cho toàn bộ lớp. Dùng chúng sẽ tạo kết luận sai lệch.

---

**Q2. Pain thực sự của giảng viên là gì? Tại sao họ không đọc chatlog thủ công?**

> Kiểm tra: nhóm có bắt đầu từ người dùng thực tế không.

Kỳ vọng: 3.097 lượt hỏi từ 448 học viên chỉ trong 1 tuần — không thể đọc hết thủ công. Giảng viên cần biết *lớp kẹt ở đâu*, không phải *từng học viên hỏi gì*.

---

**Q3. Sự khác biệt giữa A1 và A2 là gì? Tại sao VLearn Pulse là A2 chứ không phải A1?**

> Kiểm tra: nhóm có định vị đúng phạm vi không.

Kỳ vọng: A1 là tối ưu câu trả lời của tutor hiện có. A2 là xây tính năng *mới*, phục vụ người dùng khác (giảng viên/TA), xuất phát từ data pain thực tế.

---

## Nhóm 2: Xử lý dữ liệu & Chống nhiễu

**Q4. Câu hỏi preset (`is_preset`) chiếm 22,7%. Nếu không lọc, điều gì xảy ra với top-5 cluster của bạn?**

> Kiểm tra: nhóm có xử lý noise cụ thể không, hay chỉ nói lý thuyết.

Kỳ vọng: Các chủ đề được gợi sẵn sẽ phình to, làm distort ranking. Một cluster có thể nổi lên không phải vì học viên thực sự thắc mắc mà vì đó là câu preset phổ biến.

---

**Q5. Nếu một học viên hỏi cùng một khái niệm 20 lần, làm sao không để họ chi phối kết quả?**

> Kiểm tra: cơ chế deduplication cụ thể.

Kỳ vọng: Đánh trọng số theo số học viên *unique* — mỗi học viên chỉ đóng góp tối đa 1 phiếu cho một cluster, bất kể hỏi bao nhiêu lần.

---

**Q6. Hai trang slide khác nhau cùng giải thích một khái niệm — cluster của bạn xử lý thế nào?**

> Kiểm tra: thiết kế semantic clustering và liên kết đa nguồn.

Kỳ vọng: Một cluster có thể gắn với nhiều nguồn (trang slide + mã transcript). Không chia tách cluster chỉ vì khác trang — ngữ nghĩa mới là tiêu chí gom nhóm.

---

**Q7. Khi lớp hỏi rất ít về một chủ đề, bạn kết luận "lớp đã hiểu" không? Tại sao?**

> Kiểm tra: nhóm có tránh false confidence không.

Kỳ vọng: Không. Ít câu hỏi có thể do lớp chưa học đến, không dám hỏi, hoặc câu hỏi bị lọc ra. Hiển thị "chưa đủ signal" kèm độ phủ học viên thay vì kết luận.

---

## Nhóm 3: Thiết kế sản phẩm & UX

**Q8. Mỗi điểm nghẽn hiển thị những thông tin gì? Tại sao cần có "ví dụ câu hỏi đã ẩn danh"?**

> Kiểm tra: nhóm có thiết kế output cụ thể không.

Kỳ vọng: Tên khái niệm, nguồn học liệu, số học viên unique, số lượt hỏi, 1–2 ví dụ ẩn danh, mức tin cậy. Ví dụ ẩn danh giúp giảng viên kiểm chứng AI không đoán sai — grounding quan trọng hơn chỉ có con số.

---

**Q9. Tại sao giảng viên phải là người phê duyệt thay vì AI tự tạo thẻ ôn và gửi thẳng cho học viên?**

> Kiểm tra: hiểu về human-in-the-loop.

Kỳ vọng: AI có thể gán nhầm cluster, đoán quá mức, hoặc bỏ sót ngữ cảnh sư phạm. Giảng viên nắm toàn bộ bức tranh của lớp. Mục đích là *hỗ trợ quyết định*, không thay thế quyết định.

---

**Q10. "Thẻ ôn 5 phút" có những thành phần gì? Mục tiêu mỗi thành phần là gì?**

> Kiểm tra: nhóm đã nghĩ qua UX output cụ thể.

Kỳ vọng: Mục tiêu ôn → Hiểu nhầm phổ biến → Trích đoạn nguồn → Ví dụ giải thích → Câu kiểm tra hiểu. Mỗi thành phần phục vụ một bước trong quy trình dạy lại ngắn.

---

## Nhóm 4: Đo lường & KPI

**Q11. Bạn đo thành công của VLearn Pulse bằng chỉ số nào? Tại sao không dùng rating?**

> Kiểm tra: nhóm có KPI thực tế gắn với mục tiêu sản phẩm.

Kỳ vọng: Cluster usefulness (giảng viên xác nhận hữu ích), Grounding (insight có liên kết đúng nguồn), Noise resistance (dedup trước/sau), Actionability (thời gian tạo thẻ ôn), Privacy (không lộ cá nhân). Rating quá thưa (1,3%) và dễ bias.

---

**Q12. Làm thế nào để kiểm chứng rằng top-5 của bạn không bị "làm phồng" bởi một học viên duy nhất?**

> Kiểm tra: nhóm có test noise resistance cụ thể không.

Kỳ vọng: So sánh top-5 trước và sau khi dedup theo học viên. Nếu thứ hạng thay đổi mạnh, cần điều chỉnh trọng số hoặc cơ chế đếm.

---

## Nhóm 5: Quyền riêng tư & Rủi ro

**Q13. Tại sao không hiển thị mã học viên trên giao diện giảng viên, dù giảng viên chính là người dạy họ?**

> Kiểm tra: hiểu về privacy by design.

Kỳ vọng: Mục tiêu là phát hiện *điểm nghẽn của lớp*, không phải profile từng cá nhân. Lộ tên/mã học viên tạo risk: giảng viên có thể vô tình thiên vị, học viên sẽ ngại hỏi AI nếu biết câu hỏi bị trace về mình.

---

**Q14. Nếu AI gán một câu hỏi vào sai cluster, hệ thống của bạn recover thế nào?**

> Kiểm tra: cơ chế human override cụ thể.

Kỳ vọng: Giảng viên có nút gộp, tách, đổi tên, hoặc bỏ qua cluster. Mỗi insight có ví dụ câu hỏi nguồn để giảng viên tự phán đoán. AI không phải nguồn duy nhất của sự thật.

---

## Nhóm 6: Câu hỏi thử thách (cho nhóm mạnh)

**Q15. Nếu hai nhóm học viên hỏi cùng một khái niệm nhưng với góc độ hoàn toàn khác nhau, bạn tách hay gộp cluster? Tiêu chí quyết định là gì?**

**Q16. Với 3.097 lượt hỏi trong 1 tuần, chi phí tính toán để cluster real-time sau mỗi buổi học là bao nhiêu? Bạn có cần cache hay batch processing không?**

**Q17. Nếu giảng viên liên tục bỏ qua (dismiss) một cluster mà AI cứ đề xuất lại, hệ thống học được gì từ feedback đó?**

---

*Ngày tạo: 16/09/2026 — dùng nội bộ cho vòng phỏng vấn demo nhóm K4-3A-E402-VSF.*
