import contextlib
import io
import json
import unittest

with contextlib.redirect_stdout(io.StringIO()) as _out:
    import ex2
_IMPORT_OUTPUT = _out.getvalue()


class TestEx2(unittest.TestCase):
    def setUp(self):
        self.args = {"case": "c1", "position": "contest", "note": "café"}
        self.text = ex2.approval_request("record_assessment", self.args, ["a.pdf", "b.txt"])
        self.lines = self.text.split("\n")

    def test_structure(self):
        self.assertEqual(self.lines[0], "Action: record_assessment")
        self.assertEqual(self.lines[1], "Arguments:")
        self.assertEqual(self.lines[-1], "Approve? [y/N]")
        self.assertEqual(self.lines[-3:-1], ["  - a.pdf", "  - b.txt"])
        self.assertEqual(
            self.lines[-4], "Untrusted content in context when this was proposed:"
        )

    def test_arguments_are_full_round_trippable_json(self):
        start = 2
        end = self.lines.index("Untrusted content in context when this was proposed:")
        block = "\n".join(self.lines[start:end])
        self.assertEqual(json.loads(block), self.args)
        self.assertIn("café", block)  # ensure_ascii=False keeps text readable

    def test_no_sources(self):
        lines = ex2.approval_request("t", {}, []).split("\n")
        self.assertEqual(lines[-2], "Untrusted content in context when this was proposed:")
        self.assertEqual(lines[-1], "Approve? [y/N]")

    def test_demo_output(self):
        self.assertTrue(_IMPORT_OUTPUT.startswith("Action: record_assessment\n"))
        self.assertIn('"reasoning": "Brief objection; no detailed rebuttal."', _IMPORT_OUTPUT)
        self.assertIn("  - petition.pdf (party-submitted)", _IMPORT_OUTPUT)
        self.assertTrue(_IMPORT_OUTPUT.endswith("Approve? [y/N]\n"))


if __name__ == "__main__":
    unittest.main()
