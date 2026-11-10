import contextlib
import io
import unittest

with contextlib.redirect_stdout(io.StringIO()) as _out:
    import ex1
_IMPORT_OUTPUT = _out.getvalue()


class TestEx1(unittest.TestCase):
    def test_printed_demo(self):
        self.assertEqual(
            _IMPORT_OUTPUT,
            "summarize: allowed\nrecord_assessment: needs human approval\n",
        )

    def test_side_effect_with_untrusted_needs_approval(self):
        for tool in ex1.SIDE_EFFECTS:
            self.assertEqual(ex1.decide(tool, ex1.context), "needs human approval")

    def test_side_effect_with_only_operator_allowed(self):
        ctx = [ex1.Content("do it", "operator")]
        for tool in ex1.SIDE_EFFECTS:
            self.assertEqual(ex1.decide(tool, ctx), "allowed")

    def test_read_only_tool_allowed_even_when_tainted(self):
        self.assertEqual(ex1.decide("summarize", ex1.context), "allowed")

    def test_empty_context_allowed(self):
        self.assertEqual(ex1.decide("send_message", []), "allowed")

    def test_content_is_frozen(self):
        c = ex1.Content("x", "operator")
        with self.assertRaises(Exception):
            c.origin = "untrusted"


if __name__ == "__main__":
    unittest.main()
