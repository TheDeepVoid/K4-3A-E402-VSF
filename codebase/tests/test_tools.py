"""Unit test cho 3 module tool: preprocessing / clustering / grounding + registry.

Chạy:
    .venv/bin/python -m unittest discover -s codebase/tests -v
hoặc:
    .venv/bin/python -m unittest codebase.tests.test_tools
"""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from preprocessing.preprocess import (  # noqa: E402
    is_preset_question, normalize_question, preprocess_questions,
)
from clustering.cluster import cluster, tokenize  # noqa: E402
from grounding.ground import ground_clusters  # noqa: E402
from tools.registry import TOOLS, TOOL_NAMES, execute_tool  # noqa: E402
from tools.schemas import TOOL_SCHEMAS  # noqa: E402


class TestPreprocess(unittest.TestCase):
    def test_preset_detection_regex(self):
        self.assertTrue(is_preset_question("Giải thích đoạn bôi đen giúp em"))
        self.assertTrue(is_preset_question("tóm tắt nội dung chính"))
        self.assertTrue(is_preset_question("giải thích rõ đoạn này"))
        self.assertFalse(is_preset_question("Transformer là gì?"))

    def test_flag_overrides_regex(self):
        self.assertFalse(is_preset_question("Giải thích đoạn bôi đen", flag=False))
        self.assertTrue(is_preset_question("Temperature là gì?", flag=True))

    def test_normalize_strips_context_prefix(self):
        q = '(Trang 2, đoạn được chọn: "Day 1 giới thiệu những chủ đề nào?") ' \
            "Day 1 giới thiệu những chủ đề nào?"
        self.assertEqual(normalize_question(q),
                         "Day 1 giới thiệu những chủ đề nào?")
        # Dạng ngắn không có dấu phẩy cũng phải bị bỏ.
        self.assertEqual(normalize_question("(Trang 1) Attention là gì?"),
                         "Attention là gì?")
        self.assertEqual(normalize_question('(Đang học phần "Transformer") X là gì?'),
                         'X là gì?')

    def test_preprocess_counts_and_dedupe(self):
        raw = [
            {"student": "S001", "is_preset": True,
             "student_question": "Giải thích đoạn bôi đen"},
            {"student": "S001", "is_preset": False,
             "student_question": "   (Trang 1)  Attention là gì?  "},
            {"student": "S001", "is_preset": False,
             "student_question": "Attention là gì?"},          # trùng câu, cũ hơn
            {"student": "S002", "is_preset": False,
             "student_question": "Temperature dùng để làm gì?"},
            {"student": "S003", "is_preset": False,
             "student_question": "   "},                        # rỗng
        ]
        res = preprocess_questions(raw)
        self.assertEqual(res["excluded_preset_count"], 1)
        self.assertEqual(res["excluded_empty_count"], 1)
        self.assertEqual(res["valid_question_count"], 2)   # S001 giữ 1 bản sau dedupe
        self.assertEqual(res["unique_student_count"], 2)   # S001, S002 (S003 bị rỗng)
        self.assertEqual(res["dedupe_removed_count"], 1)
        self.assertEqual(res["total_input"], 5)
        # Câu giữ lại của S001 là bản mới nhất, đã chuẩn hoá (bỏ tiền tố).
        texts = [v["student_question"] for v in res["valid_questions"]]
        self.assertIn("Attention là gì?", texts)
        self.assertNotIn("(Trang 1)  Attention là gì?", texts)


class TestCluster(unittest.TestCase):
    def test_grouping_and_unassigned(self):
        # Nhóm 1: câu giống nhau/bao hàm nhau về từ khoá (transformer/attention).
        # Nhóm 2: câu cùng dùng "temperature" + "top-p". Một câu lạc đề đơn lẻ.
        questions = [
            {"student": "S001",
             "student_question": "Attention là cơ chế gì trong transformer và "
                                 "hoạt động ra sao?"},
            {"student": "S002",
             "student_question": "Attention là cơ chế gì trong transformer?"},
            {"student": "S003",
             "student_question": "Attention là cơ chế gì trong transformer và "
                                 "hoạt động ra sao?"},
            {"student": "S004", "student_question": "Temperature và top-p khác nhau ra sao?"},
            {"student": "S005", "student_question": "Temperature và top-p dùng thế nào?"},
            {"student": "S006", "student_question": "Một câu hỏi lạc đề duy nhất"},
        ]
        res = cluster(questions, similarity_threshold=0.40, min_cluster_size=2)
        clusters = res["clusters"]
        # 2 cụm ≥ 2 câu; câu lạc đề rơi vào unassigned.
        self.assertEqual(len(clusters), 2)
        self.assertEqual(res["unassigned_count"], 1)
        total = sum(c["question_count"] for c in clusters) + res["unassigned_count"]
        self.assertEqual(total, len(questions))
        big = max(clusters, key=lambda c: c["question_count"])
        self.assertEqual(big["question_count"], 3)
        self.assertEqual(big["unique_students"], 3)  # S001, S002, S003 mỗi người một câu
        self.assertTrue(big["concept"])
        self.assertGreaterEqual(len(big["top_terms"]), 1)

    def test_empty_input(self):
        res = cluster([])
        self.assertEqual(res["clusters"], [])
        self.assertEqual(res["unassigned"], [])

    def test_tokenize_filters_stopwords(self):
        toks = tokenize("các khái niệm về attention và transformer cơ bản")
        self.assertNotIn("các", toks)
        self.assertIn("attention", toks)
        self.assertIn("transformer", toks)


class TestGrounding(unittest.TestCase):
    def _materials(self):
        return [
            {"source_id": "[T04-010]", "source_type": "transcript",
             "content": "Trong phần này giảng viên giải thích temperature và top-p "
                        "dùng để kiểm soát độ ngẫu nhiên khi sinh văn bản."},
            {"source_id": "[T04-030]", "source_type": "transcript",
             "content": "Attention mechanism là cơ chế trọng số giúp mô hình biết "
                        "phần nào của câu quan trọng hơn."},
        ]

    def test_finds_matching_segment(self):
        clusters = [{"cluster_id": "C1", "concept": "temperature sinh văn bản",
                     "top_terms": ["temperature", "top-p"],
                     "example_questions": ["Top-p và temperature ảnh hưởng gì?"]}]
        res = ground_clusters(clusters, self._materials(), top_k=2)
        g = res["groundings"][0]
        self.assertTrue(g["grounded"])
        self.assertEqual(g["best_source_id"], "[T04-010]")
        self.assertIn("temperature", g["matches"][0]["matched_terms"])
        self.assertTrue(g["matches"][0]["score"] > 0)

    def test_no_match_reports_empty(self):
        clusters = [{"cluster_id": "C9", "concept": "nhập môn AI kinh doanh",
                     "top_terms": ["kinh doanh"], "example_questions": []}]
        res = ground_clusters(clusters, self._materials(), top_k=2)
        g = res["groundings"][0]
        self.assertFalse(g["grounded"])
        self.assertEqual(g["best_source_id"], "")
        self.assertEqual(g["matches"], [])

    def test_no_materials(self):
        res = ground_clusters([{"cluster_id": "C1", "concept": "x"}], [])
        self.assertEqual(res["groundings"], [])
        self.assertEqual(res["materials_scanned"], 0)


class TestEngineParsing(unittest.TestCase):
    def test_parse_function_calls_xml(self):
        from tools.engine import parse_function_calls, strip_call_blocks
        content = ("Bây giờ tôi sẽ tìm nguồn:\n\n"
                   "<function_calls>\n"
                   '<invoke name="ground_clusters">\n'
                   '<parameter name="clusters">[{"cluster_id": "C1", "concept": "x"}]</parameter>\n'
                   '<parameter name="materials">[{"source_id": "[T04-010]", "content": "hi"}]</parameter>\n'
                   '<parameter name="top_k">3</parameter>\n'
                   "</invoke>\n"
                   "</function_calls>")
        calls = parse_function_calls(content)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "ground_clusters")
        args = json.loads(calls[0]["arguments"])
        self.assertEqual(args["top_k"], 3)
        self.assertEqual(args["clusters"][0]["concept"], "x")
        self.assertEqual(args["materials"][0]["source_id"], "[T04-010]")
        stripped = strip_call_blocks(content)
        self.assertNotIn("<function_calls", stripped)
        self.assertIn("Bây giờ tôi sẽ tìm nguồn", stripped)

    def test_strip_unclosed_call_block(self):
        from tools.engine import strip_call_blocks
        out = strip_call_blocks("lời dẫn tồi\n<function_calls\n<invoke name=\"x\">")
        self.assertEqual(out, "lời dẫn tồi")
        self.assertNotIn("<function_calls", out)

    def test_plain_content_untouched(self):
        from tools.engine import strip_call_blocks, parse_function_calls
        text = "đây là output cuối không có tool call"
        self.assertEqual(strip_call_blocks(text), text)
        self.assertEqual(parse_function_calls(text), [])


class _Msg:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, msg, reason):
        self.message = msg
        self.finish_reason = reason


class _Resp:
    def __init__(self, msg, reason):
        self.choices = [_Choice(msg, reason)]


class _Completions:
    def __init__(self, responses):
        self._responses = list(responses)
        self._i = 0

    def create(self, **kwargs):  # noqa: A003 — stub
        msg, reason = self._responses[self._i]
        self._i += 1
        return _Resp(msg, reason)


class _Chat:
    def __init__(self, responses):
        self.completions = _Completions(responses)


class _Client:
    def __init__(self, responses):
        self.chat = _Chat(responses)


def _stub_tool_call(call_id, name, args):
    return {"id": call_id, "type": "function",
            "function": {"name": name,
                         "arguments": json.dumps(args, ensure_ascii=False)}}


class TestRunWithToolsOffline(unittest.TestCase):
    """Kiểm tra vòng lặp engine bằng client giả — không gọi API."""

    SYSTEM = "system"
    PAYLOAD = {
        "task": "analyze_clusters",
        "scope": {"cohort": "K4", "lecture": "D01", "time_range": "K4"},
        "questions": [{"student": "S001", "student_question": "Attention là gì?"},
                      {"student": "S002", "student_question": "Temperature là gì?"}],
        "materials": [{"source_id": "[T04-010]",
                       "content": "temperature sinh văn bản attention"}],
        "teacher_confirmed_source": False,
    }

    def _run(self, responses, **kw):
        from tools.engine import run_with_tools
        return run_with_tools(_Client(responses), model="stub", system_prompt=self.SYSTEM,
                              user_content=self.PAYLOAD, **kw)

    def test_preinject_pipeline(self):
        res = self._run([(_Msg('{"status": "ok"}'), "stop")])
        self.assertTrue(res["ok"])
        names = [t["tool"] for t in res["trace"]]
        # 2 câu không chung từ khoá → cluster không tạo cụm → ground được bỏ qua.
        self.assertEqual(names, ["preprocess_questions", "cluster_questions"])
        self.assertTrue(all(t["injected"] and t["via"] == "injected_pre"
                            for t in res["trace"]))
        self.assertEqual(res["content"], '{"status": "ok"}')

    def test_native_round_then_final(self):
        tc = _stub_tool_call("call_1", "preprocess_questions",
                             {"questions": self.PAYLOAD["questions"]})
        res = self._run([(_Msg("tôi sẽ gom cụm", [tc]), "tool_calls"),
                         (_Msg("[1,2,3]"), "stop")],
                        preinject_pipeline=False)
        self.assertTrue(res["ok"])
        self.assertEqual(res["trace"][0]["tool"], "preprocess_questions")
        self.assertEqual(res["trace"][0]["via"], "native")
        self.assertEqual(res["content"], "[1,2,3]")

    def test_content_xml_round(self):
        xml = ("<function_calls><invoke name=\"ground_clusters\">"
               "<parameter name=\"clusters\">[{\"cluster_id\": \"C1\", \"concept\": \"x\"}]</parameter>"
               "<parameter name=\"materials\">[{\"source_id\": \"[T04-010]\", \"content\": \"hi\"}]</parameter>"
               "</invoke></function_calls>")
        res = self._run([(_Msg("dẫn lời " + xml), "stop"),
                         (_Msg('{"ok": 1}'), "stop")],
                        preinject_pipeline=False)
        self.assertTrue(res["ok"])
        self.assertEqual(res["trace"][0]["tool"], "ground_clusters")
        self.assertEqual(res["trace"][0]["via"], "content_xml")
        self.assertEqual(res["content"], '{"ok": 1}')

    def test_no_tool_support_falls_back_to_inject(self):
        res = self._run([(_Msg("trả lời luôn"), "stop"),
                         (_Msg('{"final": true}'), "stop")],
                        preinject_pipeline=False)
        self.assertTrue(res["ok"])
        self.assertEqual([t["tool"] for t in res["trace"]],
                         ["preprocess_questions", "cluster_questions"])
        self.assertTrue(all(t["via"] == "injected" for t in res["trace"]))
        self.assertEqual(res["content"], '{"final": true}')


class TestExtractJson(unittest.TestCase):
    def test_prose_around_json(self):
        from ui.app import extract_json
        text = ("Tôi sẽ tổng hợp:\n"
                "{\"status\": \"ok\", \"summary\": {\"valid_question_count\": 10}}\n"
                "Kết luận xong.")
        self.assertEqual(extract_json(text)["status"], "ok")

    def test_fenced_json(self):
        from ui.app import extract_json
        text = "```json\n{\"status\": \"no_valid_questions\"}\n```"
        self.assertEqual(extract_json(text)["status"], "no_valid_questions")

    def test_braces_inside_string(self):
        from ui.app import extract_json
        text = '{"concept": "ghi chú {trong ngoặc}", "q": 2} thêm prose'
        self.assertEqual(extract_json(text)["q"], 2)


class TestRegistry(unittest.TestCase):
    def test_schemas_are_function_tools(self):
        names = [s["function"]["name"] for s in TOOL_SCHEMAS]
        self.assertEqual(names, ["preprocess_questions", "cluster_questions",
                                 "ground_clusters"])
        for s in TOOL_SCHEMAS:
            self.assertEqual(s["type"], "function")
            self.assertIn("parameters", s["function"])

    def test_execute_each_tool(self):
        r1 = execute_tool("preprocess_questions",
                          {"questions": [{"student_question": "Attention là gì?"}]})
        self.assertTrue(r1["ok"])
        self.assertEqual(r1["result"]["valid_question_count"], 1)

        r2 = execute_tool("cluster_questions",
                          {"questions": [
                              {"student_question": "Attention là gì?"},
                              {"student_question": "Temperature là gì?"},
                          ]})
        self.assertTrue(r2["ok"])
        self.assertIn("clusters", r2["result"])

        r3 = execute_tool("ground_clusters", {
            "clusters": [{"cluster_id": "C1", "concept": "temperature",
                          "top_terms": ["temperature"], "example_questions": []}],
            "materials": [{"source_id": "[T04-010]", "content": "temperature sinh văn bản"}]})
        self.assertTrue(r3["ok"])
        self.assertEqual(r3["result"]["groundings"][0]["best_source_id"], "[T04-010]")

    def test_unknown_tool_and_bad_args(self):
        r = execute_tool("some_tool", {})
        self.assertFalse(r["ok"])
        self.assertIn("tồn tại", r["error"])
        r2 = execute_tool("cluster_questions", {"questions": "not-a-list"})
        self.assertFalse(r2["ok"])


if __name__ == "__main__":
    unittest.main()