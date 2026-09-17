# Evaluation - VLearn Pulse

## Golden Set

### Mô tả
Bộ test cases được chuẩn bị thủ công để đánh giá chất lượng clustering và grounding.

### Cấu trúc
```
eval/                              ← dữ liệu + báo cáo (code ở codebase/src/evaluation/)
├── README.md                      ← file này
├── golden_set/
│   ├── sample_questions.csv       ← 50 câu hỏi đã được label thủ công
│   ├── expected_clusters.json     ← kết quả clustering mong đợi
│   └── ground_truth_mapping.csv   ← liên kết đúng với slide/transcript
├── results/
│   ├── run_001_baseline.json      ← kết quả chạy v1.0 (baseline)
│   ├── run_002_tuned.json         ← kết quả chạy v1.1
│   ├── run_003_v1_2.json          ← kết quả chạy v1.2 (hiện tại)
│   ├── comparison.csv             ← bảng so sánh 3 phiên bản prompt
│   ├── cases/                     ← output per-case (JSON từ API)
│   └── dedup_experiment*.json     ← thí nghiệm Noise Resistance
└── metrics/
    └── evaluation_report.md       ← báo cáo chi tiết

codebase/src/evaluation/           ← script evaluation (CLI)
│   ├── __init__.py
│   ├── build_golden_set.py            ← sinh golden_set
│   ├── run_cases.py                   ← chạy case qua API (chọn provider bằng --provider)
│   ├── score_runs.py                  ← tính metrics + comparison
│   ├── dedup_noise.py                 ← thí nghiệm Noise Resistance (tổng quát)
│   └── dedup_experiment.py            ← thí nghiệm Noise Resistance cho v1.1

codebase/src/prompting/            ← prompt system đang được đánh giá
├── system_prompt.md               ← v1.2 (hiện tại)
├── system_prompt_v1_0.md          ← v1.0 (archive)
└── system_prompt_v1_1.md          ← v1.1 (archive)
```

## Metrics

| Metric | Mô tả | Cách tính |
|---|---|---|
| **Clustering Purity** | Độ "sạch" của cluster | Avg purity across clusters |
| **Grounding Accuracy** | Đúng slide/transcript | Correct mappings / Total |
| **Coverage** | Phần trăm câu hỏi được cluster | Clustered / Total questions |
| **Noise Resistance** | Ổn định khi có nhiễu | Ranking correlation before/after dedup |

## Kết quả các lần chạy

| Run | Date | Prompt | Purity | Grounding Acc | Coverage | Noise Resistance | PASS/FAIL |
|---|---|---|---|---|---|---|---|
| 001 | 17/9 | v1.0 (`system_prompt_v1_0.md`) | 0,8065 | 1,0 | 79,5% | 1,0 | 10/9 |
| 002 | 17/9 | v1.1 (`system_prompt_v1_1.md`) | 0,8438 | 1,0 | 82,1% | 0,5 | 12/7 |
| 003 | 17/9 | v1.2 (`system_prompt.md`) | 0,7179 | 1,0 | 100% | 1,0 | 15/4 |

- Provider: OmniRoute (local router, OpenAI-compatible); model `kiro/deepseek-3.2`.
- 19 case, mỗi case một lượt gọi API; kết quả per-case trong `results/cases/`.
- `comparison.csv` so sánh 3 phiên bản prompt (cột `v100_status`, `v110_status`, `v120_status`).
- Chi tiết đánh giá từng case: `results/comparison.csv` và `metrics/evaluation_report.md`.

## Cách thêm evaluation mới

1. Chuẩn bị test case trong `golden_set/`
2. Chạy runner: `.venv/bin/python codebase/src/evaluation/run_cases.py --provider <provider> --prompt-file codebase/src/prompting/system_prompt.md --tag run_XXX --model <model>` (provider mặc định lấy `DEFAULT_PROVIDER` trong `.env`; API key/base URL đọc từ `<PROVIDER>_API_KEY`/`<PROVIDER>_BASE_URL`, có thể ghi đè bằng `--api-key`/`--base-url`)
3. Chạy scorer: `.venv/bin/python codebase/src/evaluation/score_runs.py` (tính metrics, ghi `results/run_XXX.json` và `comparison.csv`)
4. Cập nhật bảng comparison và `metrics/evaluation_report.md`

*Evaluation framework - VLearn Pulse*