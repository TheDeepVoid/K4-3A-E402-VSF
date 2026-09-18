"""Đăng ký tool: tên → hàm thực thi; wrapper an toàn cho function calling."""

import json
from typing import Any

from preprocessing.preprocess import run as run_preprocess
from clustering.cluster import run as run_cluster
from grounding.ground import run as run_ground

from tools.schemas import TOOL_SCHEMAS, TOOL_NAMES

TOOLS = {
    "preprocess_questions": run_preprocess,
    "cluster_questions": run_cluster,
    "ground_clusters": run_ground,
}


def execute_tool(name: str, args: Any) -> dict:
    """Chạy tool; luôn trả dict JSON-serializable để làm tool message.

    Kết quả:
      {"ok": true, "result": {...}}          — thành công
      {"ok": false, "error": "..."}          — tool không tồn tại / lỗi khi chạy
    """
    fn = TOOLS.get(name)
    if fn is None:
        return {"ok": False, "error": f"Tool không tồn tại: {name}. Các tool có sẵn: "
                                      + ", ".join(TOOL_NAMES)}
    try:
        if isinstance(args, str):
            args = json.loads(args or "{}")
        result = fn(args if isinstance(args, dict) else {})
        return {"ok": True, "result": result}
    except Exception as exc:  # noqa: BLE001 — lỗi phải về được cho model
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


__all__ = ["TOOLS", "TOOL_SCHEMAS", "TOOL_NAMES", "execute_tool"]