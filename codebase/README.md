# VLearn Pulse - Codebase

## Cấu trúc thư mục

```
codebase/
├── README.md           ← file này
├── data/              ← dữ liệu mẫu và processed
├── notebooks/         ← Jupyter notebooks cho EDA và thử nghiệm
├── src/               ← source code chính
│   ├── preprocessing/ ← làm sạch và chuẩn hóa data
│   ├── clustering/    ← thuật toán gom nhóm câu hỏi
│   ├── grounding/     ← liên kết với học liệu
│   └── ui/           ← giao diện người dùng
├── tests/            ← unit tests
└── requirements.txt  ← dependencies

```

## Cách chạy

### 1. Cài đặt
```bash
cd codebase
pip install -r requirements.txt
```

### 2. Chạy pipeline
```bash
python src/main.py --input data/sample_chatlog.csv --output results/
```

### 3. Chạy UI
```bash
streamlit run src/ui/app.py
```

## Phần Mock trong MVP

- **Grounding tự động**: Hiện tại mapping thủ công slide → cluster
- **Real-time processing**: Batch processing file CSV
- **Full transcript**: Chỉ dùng mẫu 2-3 transcript

## TODO
- [ ] Implement semantic clustering
- [ ] Build Streamlit UI
- [ ] Add confidence scoring
- [ ] Integration testing

*Cập nhật: 16/9/2026*