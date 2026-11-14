import json
import string
import unittest
from unittest import mock

import ex1


class SearchMemoryTest(unittest.TestCase):
    def test_returns_live_memory_and_skips_retired(self):
        mem, span = ex1.search_memory("how does the customer want invoices")
        self.assertIs(mem, ex1.STORE["mem-a"])
        attrs = span["attributes"]
        self.assertEqual(attrs["app.memory.id"], "mem-a")
        self.assertEqual(attrs["std.memory.content"], "Customer prefers invoices by email")
        self.assertEqual(attrs["std.memory.type"], "semantic")
        self.assertEqual(attrs["std.memory.query"], "how does the customer want invoices")
        self.assertEqual(attrs["app.memory.retired_ids"], ["mem-b"])

    def test_retired_never_returned_even_if_better_match(self):
        mem, span = ex1.search_memory("Customer prefers invoices by post")
        self.assertEqual(span["attributes"]["app.memory.id"], "mem-a")
        self.assertFalse(mem["retired"])

    def test_relevance_score_and_age(self):
        q = "how does the customer want invoices"
        _, span = ex1.search_memory(q)
        attrs = span["attributes"]
        self.assertAlmostEqual(attrs["app.memory.relevance"],
                               ex1.relevance(q, ex1.STORE["mem-a"]["text"]))
        self.assertTrue(0.0 <= attrs["app.memory.relevance"] <= 1.0)
        self.assertGreaterEqual(attrs["app.memory.age_seconds"], 0.0)

    def test_relevance_case_insensitive(self):
        self.assertEqual(ex1.relevance("ABC", "abc"), 1.0)
        self.assertEqual(ex1.relevance("abc", "xyz"), 0.0)

    def test_span_shape(self):
        _, span = ex1.search_memory("invoices")
        self.assertEqual(span["name"], "memory.search")
        self.assertLessEqual(span["start"], span["end"])
        # OpenTelemetry span IDs are 8 bytes -> 16 lowercase hex chars.
        self.assertEqual(len(span["span_id"]), 16)
        self.assertTrue(set(span["span_id"]) <= set(string.hexdigits.lower()))
        _, span2 = ex1.search_memory("invoices")
        self.assertNotEqual(span["span_id"], span2["span_id"])
        json.dumps(span)  # serialisable, as the __main__ block relies on

    def test_no_live_memories(self):
        store = {"x": {"type": "semantic", "text": "t", "created": 0, "retired": True}}
        with mock.patch.object(ex1, "STORE", store):
            mem, span = ex1.search_memory("t")
        self.assertIsNone(mem)
        attrs = span["attributes"]
        for k in ("std.memory.type", "std.memory.content", "app.memory.id",
                  "app.memory.relevance", "app.memory.age_seconds"):
            self.assertIsNone(attrs[k])
        self.assertEqual(attrs["app.memory.retired_ids"], ["x"])


if __name__ == "__main__":
    unittest.main()
