# User Validation - VLearn Pulse

> **R6 Requirement**: Nhật ký cho người ngoài dùng thử (bắt buộc để đạt điểm tối đa)

## Mục tiêu
Thu thập feedback từ giảng viên/TA thực tế về:
- Độ chính xác của top-5 cluster
- Tính hữu dụng của thẻ ôn được tạo
- Trải nghiệm sử dụng UI

## Cấu trúc

```
validation/
├── README.md              ← file này
├── user_sessions/         ← nhật ký từng session
│   ├── session_001.md     ← Giảng viên A - ngày X
│   ├── session_002.md     ← TA B - ngày Y
│   └── session_003.md     ← Giảng viên C - ngày Z
├── feedback_summary.md    ← tổng hợp insights
└── improvements.md        ← action items từ feedback
```

## Template cho session mới

### Thông tin session
- **Người dùng**: [Vai trò - Giảng viên/TA]
- **Ngày**: [DD/MM/YYYY]
- **Thời lượng**: [X phút]
- **Data**: [Mô tả bộ chatlog được dùng]

### Nhiệm vụ
1. Xem top-5 cluster, đánh giá mức độ chính xác
2. Chọn 1 cluster, tạo thẻ ôn
3. Review thẻ ôn, sửa nếu cần
4. Feedback tổng thể

### Kết quả thu được
- Rating từng cluster (1-5)
- Thời gian hoàn thành task
- Verbatim feedback
- Issues gặp phải

## Lịch validation

| Session | User | Planned Date | Status |
|---|---|---|---|
| 001 | Giảng viên A | 17/9 | Planned |
| 002 | TA B | 18/9 | Planned |
| 003 | Giảng viên C | 19/9 | Planned |

## Key Questions

1. **Usefulness**: "Top-5 này có giúp bạn quyết định ôn gì không?"
2. **Accuracy**: "Có cluster nào bạn thấy gom sai không?"
3. **Actionability**: "Thẻ ôn này có dùng được trong buổi học không?"
4. **Time**: "So với đọc chatlog thủ công, cái này nhanh hơn bao nhiêu?"

*Validation plan - R6 compliance*