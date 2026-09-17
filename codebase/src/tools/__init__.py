"""Tool capabilities cho model: preprocess / clustering / grounding qua function calling.

- schemas.py : OpenAI tool schemas (name, description, parameters)
- registry.py: tên tool → hàm thực thi (+ wrapper an toàn)
- engine.py  : vòng lặp function calling + auto-inject deterministic
- selftest.py: kiểm thử tool calling với API thật
"""