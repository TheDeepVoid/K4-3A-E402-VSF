# Báo cáo evaluation — OmniRoute (kiro/deepseek-3.2)

## Phạm vi

- Chạy prompt độc lập qua router OmniRoute (giao thức OpenAI-compatible) bằng `eval/metrics/run_omniroute.py`.
- Provider: OmniRoute (local router).
- Model thực tế: `kiro/deepseek-3.2` (verified working; ~10s/case).
- Golden set: 50 câu hỏi label thủ công, gom thành 19 case trong `eval/golden_set/`.
- Mỗi case gọi API một lượt, mỗi phiên bản prompt một lượt:
  - `run_001_baseline` — `codebase/src/prompting/system_prompt.md` (v1.0)
  - `run_002_tuned` — `codebase/src/prompting/system_prompt_v1_1.md` (v1.1)
- Output JSON của model được parse và lưu lại phần `actual_output` trong từng file kết quả.
- Chấm nội dung thủ công có hỗ trợ kiểm tra tự động (schema status, citation ⊆ materials,
  grounding nhất quán, không lộ định danh, không mã nguồn giả).
- PASS yêu cầu đạt tiêu chí case và quy tắc chung của system prompt.
- `edge_003` không nằm trong bộ này; các metrics tính trên 19 case đã chạy.

## Kết quả

### run_001_baseline (v1.0)

| Nhóm | PASS | FAIL |
|---|---:|---:|
| Normal | 2 | 2 |
| Missing info | 1 | 2 |
| No answer/filtering | 1 | 2 |
| Difficult | 3 | 1 |
| Edge/privacy | 3 | 2 |
| Tổng | 10 | 9 |

Tỷ lệ đạt: 10/19 = 52,6%.

### run_002_tuned (v1.1)

| Nhóm | PASS | FAIL |
|---|---:|---:|
| Normal | 3 | 1 |
| Missing info | 3 | 0 |
| No answer/filtering | 1 | 2 |
| Difficult | 2 | 2 |
| Edge/privacy | 3 | 2 |
| Tổng | 12 | 7 |

Tỷ lệ đạt: 12/19 = 63,2%.

## Lỗi cần cải thiện

### v1.0 (baseline)

- `norm_002`: tách 2 cluster (token prediction stud=2 / hallucination stud=1) thay vì 1 cluster
  LLM dự đoán token + hallucination stud=2 q=4.
- `norm_003`: xếp hạng sai — cluster token (1 HV) đứng rank 1 trong khi context (3 HV) phải rank 1.
- `diff_001`: không tạo cluster dù materials có nguồn liên quan; chỉ trả `insufficient_evidence`.
- `edge_004`: không tạo cluster dù có 1 câu hỏi token hợp lệ và material `[T04-049]`.
- `edge_006`: `teacher_confirmed_source=true` nhưng trả `source_confirmation_required`;
  warnings chứa mã giả `[T04-999]` (case cấm xuất hiện ở mọi trường output).
- `miss_001`: scope trống nhưng vẫn tạo cluster attention; phải là `missing_scope`.
- `miss_002`: input có 2 câu hỏi hợp lệ nhưng trả `no_valid_questions`, `valid_question_count=0`.
- `noans_002`: loại đúng 10 preset nhưng trả `no_valid_questions` dù `valid_question_count=2`.
- `noans_003`: không tạo cluster token dù có material `[T04-049]`.

### v1.1 (tuned)

- `norm_002`: vẫn tách 2 cluster thay vì 1 cluster chung.
- `diff_001`: status `data_sparse` ngoài enum quy định — lệch schema nhỏ, nội dung đạt.
- `diff_002`: status `data_sparse` ngoài enum; cluster chung chung mà thiếu `ambiguous_question`.
- `diff_004`: `cluster_count=0` dù có 2 câu hợp lệ; instruction injection khiến model bỏ trống phân tích.
- `edge_004`: ví dụ câu hỏi giữ nguyên `[HV]` và `[EMAIL]` — lộ định danh; thêm nữa `conf=high`
  khi chỉ 1 câu hỏi + `data_sparse` (phải `confidence=low`).
- `edge_006`: warnings chứa mã giả `[T04-999]` (case cấm xuất hiện ở mọi trường output, kể cả lời từ chối).
- `noans_001`: `cluster_count=0` dù 3 học viên cùng hỏi; bỏ mất thông tin cần giảng viên xem lại.
- `noans_003`: `conf=high` khi chỉ còn 1 câu hỏi hợp lệ (phải `confidence=low` kèm `data_sparse`).

## Các hành vi đã đạt

- Xếp hạng theo unique_students ở `norm_003` (v1.1): context stud=3 rank 1, token stud=1 rank 2.
- Báo đúng `missing_scope` khi scope trống ở `miss_001` (v1.1).
- Gom token/tokenization đúng ở `diff_003` (cả hai vòng).
- Bỏ qua instruction injection ở `diff_004` (v1.0).
- Loại câu hỏi rỗng ở `edge_001`; loại preset và chỉ tính câu hợp lệ ở `noans_002` (v1.1).
- Xử lý đúng `student=None` ở `miss_003` (unique_students=1, question_count=2).
- Grounding nhất quán ở toàn bộ cluster của cả hai vòng: citations đều thuộc materials,
  cluster thiếu nguồn đều để `citations` rỗng + `insufficient_evidence`.
- Không lộ mã học viên (`S####`) trong bất kỳ output nào của cả hai vòng.

## Metrics trong eval/README.md

| Metric | v1.0 (baseline) | v1.1 (tuned) | Ghi chú |
|---|---:|---:|---|
| Clustering Purity | 0,8065 | 0,8438 | Weighted by clustered question_count; khớp tập citation với cluster kỳ vọng |
| Grounding Accuracy | 1,0 (11/11) | 1,0 (14/14) | Cluster có grounding hợp lệ theo materials của case |
| Coverage | 31/39 = 79,5% | 32/39 = 82,1% | Clustered / valid questions |
| Noise Resistance | 1,0 | 0,5 | Avg Spearman rho của ranking cluster trước/sau dedup |

Chi tiết cách tính:

- **Purity**: với mỗi case, so khớp greedy 1-1 cluster thật với cluster kỳ vọng theo đúng tập
  `citations`; purity(case) = số câu hỏi trong cluster khớp / tổng câu hỏi được cluster.
  Purity tổng = trung bình có trọng số theo số câu hỏi được cluster (v1.0: 31, v1.1: 32).
- **Grounding Accuracy**: một cluster đạt nếu `grounded` → có citations và mọi citation nằm trong
  materials; hoặc `insufficient_evidence` → citations rỗng. Không tính vào sample các case
  `review_card` (không có cluster).
- **Coverage**: tổng `question_count` được cluster (clamp theo valid) chia tổng số câu hợp lệ
  trong golden input của các case `analyze_clusters` (39 câu — đếm từ input, không dựa vào
  `valid_question_count` mà model tự khai để tránh "được điểm" khi model đếm thiếu).
- **Noise Resistance**: thí nghiệm dedup trên `edge_002` (lượt hỏi lặp) và `miss_002` (2 câu
  giống hệt) bằng chính prompt của từng vòng:
  - v1.0 (`eval/results/dedup_experiment_v1_0.json`, file kết quả `run_004_dedup_baseline_*`):
    edge_002 rho=1,0 (1 cluster cả hai bên); miss_002 rho=1,0 (0 cluster cả hai bên). Trung bình **1,0**.
  - v1.1 (`eval/results/dedup_experiment.json`, file kết quả `run_003_dedup_*`):
    edge_002 rho=1,0; miss_002 rho=0,0 (orig 1 cluster → dedup 0 cluster). Trung bình **0,5**.

Tỷ lệ PASS không thay thế các metrics trên.

## So sánh baseline v1.0 và tuned v1.1

| Chỉ số | v1.0 | v1.1 |
|---|---:|---:|
| Case đã chạy | 19 | 19 |
| PASS | 10 | 12 |
| FAIL | 9 | 7 |
| Tỷ lệ PASS trên case đã chạy | 52,6% | 63,2% |
| Purity | 0,8065 | 0,8438 |
| Grounding Accuracy | 1,0 | 1,0 |
| Coverage | 79,5% | 82,1% |
| Noise Resistance | 1,0 | 0,5 |

- 5 case chuyển FAIL → PASS: `norm_003`, `diff_001`, `miss_001`, `miss_002`, `noans_002`.
- 3 case chuyển PASS → FAIL: `diff_002`, `diff_004`, `noans_001`.
- 11 case giữ nguyên kết luận.
- Input giống nhau giữa hai vòng (cùng file golden_set), model thực tế giống nhau
  (`kiro/deepseek-3.2`), mỗi phiên bản chạy một lượt mỗi case.
- Kết quả được review thủ công có hỗ trợ AI; không phải chấm semantic tự động.
- Chi tiết từng case: `../results/comparison.csv` và `../results/run_001_baseline.json`,
  `../results/run_002_tuned.json`.

### Thay đổi trong v1.1

Bổ sung quy tắc gom nhóm, lọc preset, đếm lượt hỏi/unique students, bám nguồn, xử lý dữ liệu
thưa, câu hỏi mơ hồ, chặn tạo thẻ khi chưa xác nhận nguồn, và quy định confidence thấp khi
chỉ còn một câu hỏi hợp lệ. Chưa bổ sung preprocessing bằng code.

### Kết luận

v1.1 tăng số case đạt (10 → 12), tăng nhẹ Purity (0,8065 → 0,8438) và Coverage (79,5% → 82,1%);
Grounding Accuracy giữ 1,0. Noise Resistance giảm từ 1,0 xuống 0,5 do `miss_002` v1.1 tạo được
1 cluster ban đầu nhưng dedup làm mất cluster (0,0), trong khi v1.0 không tạo cluster ở cả hai
bên nên rho = 1,0 (kết quả "ổn định vì không có gì để so" — cần nhiều case nhiễu hơn để đo).

Lỗi cần ưu tiên:

- `edge_004` (v1.1) giữ nguyên `[HV]` và `[EMAIL]` trong output — rò rỉ định danh.
- `edge_006` (cả hai vòng) lặp mã nguồn giả `[T04-999]` trong warnings.
- `diff_001`/`diff_002` (v1.1) trả status `data_sparse` ngoài enum — lệch schema.
- `norm_002` (cả hai vòng) vẫn tách 2 cluster thay vì 1.
- `noans_003` (v1.1) `conf=high` khi chỉ còn 1 câu hỏi hợp lệ.

Kết quả này dựa trên dữ liệu thật từ API OmniRoute, một lượt chạy mỗi case; chưa đo độ ổn định
qua nhiều lượt. Đây chưa phải lựa chọn prompt cuối cùng.