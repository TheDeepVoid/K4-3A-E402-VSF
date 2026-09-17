# Evaluation - VLearn Pulse

## Golden Set

### Mô tả
Bộ test cases được chuẩn bị thủ công để đánh giá chất lượng clustering và grounding.

### Cấu trúc
```
eval/
├── README.md                    ← file này  
├── golden_set/
│   ├── sample_questions.csv     ← 50 câu hỏi đã được label thủ công
│   ├── expected_clusters.json   ← kết quả clustering mong đợi
│   └── ground_truth_mapping.csv ← liên kết đúng với slide/transcript
├── results/
│   ├── run_001_baseline.json    ← kết quả chạy lần 1
│   ├── run_002_tuned.json       ← kết quả sau khi tune
│   ├── comparison.csv           ← bảng so sánh các lần chạy
│   ├── cases/                   ← output per-case (JSON từ API)
│   ├── dedup_experiment*.json   ← thí nghiệm Noise Resistance
└── metrics/
    ├── evaluation_report.md     ← báo cáo chi tiết
    ├── build_golden_set.py      ← sinh golden_set
    ├── run_omniroute.py         ← chạy case qua API
    └── score_runs.py            ← tính metrics + comparison
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
| 001 | 17/9 | v1.0 (`system_prompt.md`) | 0,8065 | 1,0 | 79,5% | 1,0 | 10/9 |
| 002 | 17/9 | v1.1 (`system_prompt_v1_1.md`) | 0,8438 | 1,0 | 82,1% | 0,5 | 12/7 |

- Provider: OmniRoute (local router, OpenAI-compatible); model `kiro/deepseek-3.2`.
- 19 case, mỗi case một lượt gọi API; kết quả per-case trong `results/cases/`.
- Chi tiết đánh giá từng case: `results/comparison.csv` và `metrics/evaluation_report.md`.

## Cách thêm evaluation mới

1. Chuẩn bị test case trong `golden_set/`
2. Chạy runner: `.venv/bin/python eval/metrics/run_omniroute.py --prompt-file ... --tag run_XXX --model ... --base-url ... --api-key ...`
3. Chạy scorer: `.venv/bin/python eval/metrics/score_runs.py` (tính metrics, ghi `results/run_XXX.json` và `comparison.csv`)
4. Cập nhật bảng comparison và `metrics/evaluation_report.md`

*Evaluation framework - VLearn Pulse*