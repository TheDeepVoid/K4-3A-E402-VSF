"""Grounding: tìm đoạn học liệu [Txx-NNN] khớp với từ khoá của từng cụm.

Module này là "tool" grounding deterministic: chấm điểm từng segment trong
`materials` theo độ phủ của từ khoá cụm (trọng số tf + idf, chuẩn hoá về 0..1),
trả top-k ứng viên kèm snippet để model chọn citation cuối và đánh giá
grounding_status. Không bịa citation: chỉ trả nguồn có thật trong materials.
"""

import math
from collections import Counter

from preprocessing.preprocess import VIETNAMESE_STOPWORDS

SNIPPET_CHARS = 200


def _clean(terms):
    out = []
    for tok in terms:
        tok = "".join(ch for ch in tok.lower() if ch.isalnum() or ch in "àáảãạâầấẩẫậăằắẳẵặ"
                      "èéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợ"
                      "ùúủũụưừứửữựỳýỷỹỵđ").strip()
        if len(tok) >= 3 and not tok.isdigit() and tok not in VIETNAMESE_STOPWORDS:
            out.append(tok)
    return out


def tokenize(text):
    t = (text or "").lower().replace("_", " ").replace("-", " ").replace("/", " ")
    return _clean(t.split())


def term_vector(text) -> Counter:
    return Counter(tokenize(text))


def ground_clusters(clusters, materials, top_k=3) -> dict:
    """Tìm segment khớp từ khoá cho từng cluster.

    clusters:  [{cluster_id, concept, top_terms?, example_questions?}]
    materials: [{source_id, content}] — segment học liệu (đã qua select_materials).
    """
    clusters = [c for c in (clusters or []) if isinstance(c, dict)]
    materials = [m for m in (materials or []) if isinstance(m, dict) and m.get("content")]

    if not materials:
        return {"groundings": [], "materials_scanned": 0,
                "note": "Không có materials → không thể grounding."}

    seg_vectors = []
    df = Counter()  # document frequency của từng từ khoá
    for m in materials:
        sv = term_vector(m.get("content") or "")
        if not sv:
            continue
        seg_vectors.append((m.get("source_id") or "", sv))
        df.update(sv.keys())
    n = max(1, len(seg_vectors))
    by_id = {m.get("source_id"): (m.get("content") or "") for m in materials}

    def idf(term):
        return math.log((n + 1) / (df.get(term, 0) + 0.5))

    groundings = []
    for cl in clusters:
        cv = Counter()
        concept = cl.get("concept") or ""
        if concept:
            cv.update(term_vector(concept))          # khái niệm được đưa ra trước
            cv.update(term_vector(concept))          # nhân đôi trọng số
        for t in (cl.get("top_terms") or []):
            cv.update(term_vector(t))
        for q in (cl.get("example_questions") or []):
            cv.update(term_vector(q))

        scored = []
        for sid, sv in seg_vectors:
            s, matched = 0.0, []
            for term, w in cv.items():
                if sv.get(term):
                    s += w * sv[term] * idf(term)
                    matched.append(term)
            if s > 0:
                scored.append((sid, s, matched))
        scored.sort(key=lambda x: -x[1])
        best = scored[0][1] if scored else 0.0

        matches = []
        for sid, s, matched in scored[:max(1, top_k)]:
            snippet = (by_id.get(sid) or "")[:SNIPPET_CHARS]
            matches.append({
                "source_id": sid,
                "score": round(s / best, 3) if best else 0.0,
                "matched_terms": matched[:8],
                "snippet": snippet,
            })

        groundings.append({
            "cluster_id": cl.get("cluster_id") or "",
            "concept": concept,
            "grounded": bool(matches),
            "best_source_id": matches[0]["source_id"] if matches else "",
            "matches": matches,
        })

    return {
        "groundings": groundings,
        "materials_scanned": len(seg_vectors),
        "note": "Chấm điểm tf-idf trên từ khoá cụm (concept ×2 + top_terms + "
                "example_questions). Chỉ trả nguồn có thật trong materials; model "
                "chọn citation chính xác và đánh giá grounding_status từ đây.",
    }


def run(args: dict) -> dict:
    """Entry point khi model gọi tool `ground_clusters`."""
    if not isinstance(args, dict):
        raise ValueError("ground_clusters cần args là object.")
    if not isinstance(args.get("materials"), list):
        raise ValueError("ground_clusters cần args.materials là mảng materials.")
    if not isinstance(args.get("clusters"), list):
        raise ValueError("ground_clusters cần args.clusters là mảng clusters.")
    return ground_clusters(
        args["clusters"],
        args["materials"],
        top_k=int(args.get("top_k", 3)),
    )