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
│   └── comparison.csv           ← bảng so sánh các lần chạy
└── metrics/
    └── evaluation_report.md     ← báo cáo chi tiết
```

## Metrics

| Metric | Mô tả | Cách tính |
|---|---|---|
| **Clustering Purity** | Độ "sạch" của cluster | Avg purity across clusters |
| **Grounding Accuracy** | Đúng slide/transcript | Correct mappings / Total |
| **Coverage** | Phần trăm câu hỏi được cluster | Clustered / Total questions |
| **Noise Resistance** | Ổn định khi có nhiễu | Ranking correlation before/after dedup |

## Kết quả các lần chạy

| Run | Date | Clustering Alg | Purity | Grounding Acc | Coverage | Notes |
|---|---|---|---|---|---|---|
| 001 | 16/9 | K-means (k=5) | - | - | - | Baseline |
| 002 | 16/9 | HDBSCAN | - | - | - | Auto k selection |

## Cách thêm evaluation mới

1. Chuẩn bị test case trong `golden_set/`
2. Chạy algorithm: `python ../src/main.py --eval --input golden_set/sample_questions.csv`
3. Lưu kết quả vào `results/run_XXX.json`
4. Cập nhật bảng comparison

*Evaluation framework - VLearn Pulse*