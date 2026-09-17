"""Gom câu hỏi thành cụm chủ đề bằng từ khoá (overlap/Jaccard trên unigram + bigram).

Module này là "tool" clustering deterministic, không cần thêm thư viện
(không dùng HDBSCAN / sentence-transformers). Model gọi tool này để có cụm
thô, rồi tự đánh giá / gộp / đặt tên / xếp hạng thành output cuối.

Độ tương đồng mặc định là overlap coefficient: |A ∩ B| / min(|A|, |B|).
Với câu hỏi tiếng Việt ngắn, overlap nhạy hơn Jaccard với quan hệ "câu con
thuộc chủ đề cụm" — nên các câu trùng/lặp từ khoá được gom tự nhiên. Các câu
diễn đạt khác hẳn nhưng cùng chủ đề thì model tự gộp khi tổng hợp.

Thuật toán: single-pass greedy — mỗi câu so với "seed" của từng cụm hiện có;
nếu sim >= threshold thì vào cụm, nếu không thì mở cụm mới. Cụm có số câu
< min_cluster_size bị đẩy vào `unassigned`.
"""

from collections import Counter

from preprocessing.preprocess import VIETNAMESE_STOPWORDS

MIN_TOKEN_LEN = 3


def tokenize(text) -> list:
    """Tách từ khoá: lowercase, bỏ ký tự đặc biệt, lọc từ dừng/ngắn/số thuần.

    Trả về list token bậc 1 (unigram). Dùng stopwords của preprocessing.
    """
    t = (text or "").lower()
    t = t.replace("_", " ").replace("-", " ").replace("/", " ")
    tokens = []
    for tok in _clean_terms(t.split()):
        tokens.append(tok)
    return tokens


def _clean_terms(terms):
    out = []
    for tok in terms:
        tok = "".join(ch for ch in tok if ch.isalnum() or ch in "àáảãạâầấẩẫậăằắẳẵặ"
                      "èéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợ"
                      "ùúủũụưừứửữựỳýỷỹỵđ")
        tok = tok.strip()
        if len(tok) < MIN_TOKEN_LEN:
            continue
        if tok.isdigit():
            continue
        if tok in VIETNAMESE_STOPWORDS:
            continue
        out.append(tok)
    return out


def feature_set(text) -> set:
    """Bộ đặc trưng = unigram + bigram (bỏ trùng)."""
    toks = tokenize(text)
    feats = set(toks)
    for a, b in zip(toks, toks[1:]):
        feats.add(f"{a} {b}")
    return feats


def overlap_coefficient(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


SIM_FUNCS = {"overlap": overlap_coefficient, "jaccard": jaccard}


def cluster(questions, similarity_threshold=0.40, min_cluster_size=2,
            top_terms=5, metric="overlap") -> dict:
    """Gom câu đã chuẩn hoá thành cụm thô.

    questions: list[dict] có `student_question` (đã qua preprocess).
    metric: "overlap" (mặc định) hoặc "jaccard".
    Trả về:
      clusters   — [{cluster_id, concept, question_count, unique_students,
                     top_terms, example_questions, member_indexes}]
      unassigned — câu không đủ min_cluster_size
    """
    sim = SIM_FUNCS.get(metric, overlap_coefficient)
    questions = [q for q in (questions or []) if isinstance(q, dict)]
    if not questions:
        return {"clusters": [], "unassigned": [], "note": "Không có câu hỏi để gom."}

    raw_clusters = []  # [{seed: set, members: [idx]}]
    for i, q in enumerate(questions):
        feats = feature_set(q.get("student_question") or "")
        if not feats:
            continue
        best, best_sim = None, 0.0
        for k, cl in enumerate(raw_clusters):
            s = sim(feats, cl["seed"])
            if s > best_sim:
                best_sim, best = s, k
        if best is not None and best_sim >= similarity_threshold:
            raw_clusters[best]["members"].append(i)
        else:
            raw_clusters.append({"seed": feats, "members": [i]})

    clusters, unassigned = [], []
    cid = 1
    for cl in raw_clusters:
        members = cl["members"]
        if len(members) < min_cluster_size:
            unassigned.extend(members)
            continue
        member_qs = [questions[i] for i in members]
        term_freq = Counter()
        for q in member_qs:
            term_freq.update(tokenize(q.get("student_question") or ""))
        bigram_freq = Counter()
        for q in member_qs:
            toks = tokenize(q.get("student_question") or "")
            bigram_freq.update(f"{a} {b}" for a, b in zip(toks, toks[1:]))

        top = [t for t, _ in term_freq.most_common(top_terms)]
        top_big = [t for t, _ in bigram_freq.most_common(top_terms)]
        # concept ưu tiên bigram xuất hiện >= 2 lần, rồi mới unigram.
        concept = next((t for t, n in bigram_freq.items() if n >= 2), None) \
            or (top[0] if top else "")
        students = {q.get("student") for q in member_qs if q.get("student")}
        clusters.append({
            "cluster_id": f"C{cid}",
            "concept": concept,
            "question_count": len(members),
            "unique_students": len(students),
            "top_terms": top_big[:top_terms] if not concept else [concept] + top[:top_terms],
            "example_questions": [q.get("student_question") for q in member_qs[:3]],
            "member_indexes": members,
        })
        cid += 1

    return {
        "clusters": clusters,
        "unassigned": [questions[i] for i in unassigned],
        "unassigned_count": len(unassigned),
        "similarity_threshold": similarity_threshold,
        "min_cluster_size": min_cluster_size,
        "metric": metric,
        "note": f"Gom thô bằng {metric} trên unigram+bigram, single-pass; model tự đánh "
                "giá, gộp, đặt tên và xếp hạng khi tổng hợp output cuối.",
    }


def run(args: dict) -> dict:
    """Entry point khi model gọi tool `cluster_questions`."""
    if not isinstance(args, dict) or not isinstance(args.get("questions"), list):
        raise ValueError("cluster_questions cần args.questions là mảng câu đã chuẩn hoá.")
    return cluster(
        args["questions"],
        similarity_threshold=float(args.get("similarity_threshold", 0.40)),
        min_cluster_size=int(args.get("min_cluster_size", 2)),
        top_terms=int(args.get("top_terms", 5)),
        metric=str(args.get("metric", "overlap")),
    )