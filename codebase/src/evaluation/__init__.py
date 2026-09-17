"""Bộ công cụ evaluation: sinh golden set, chạy case, chấm điểm và đo metrics.

Các script là CLI độc lập, đọc/ghi dữ liệu trong eval/ ở gốc repo:
    build_golden_set.py  — sinh eval/golden_set từ case JSON
    run_omniroute.py     — chạy 19 case qua OmniRoute, ghi eval/results/cases/
    score_runs.py        — chấm thủ công + tính 4 metrics, ghi aggregate/comparison
    dedup_noise.py       — thí nghiệm Noise Resistance (tổng quát)
    dedup_experiment.py  — thí nghiệm Noise Resistance cho prompt v1.1
"""
