import unittest

from evoagent.diff_parser import parse_unified_diff
from evoagent.reviewer import LocalRuleReviewer


class LocalReviewerTests(unittest.TestCase):
    def test_detects_security_findings_only_on_added_lines(self):
        diff = """--- a/app.py
+++ b/app.py
@@ -1,2 +1,3 @@
-eval(old_input)
+password = "super-secret"
+df['close'].shift(-1)
 safe = True
"""
        findings = LocalRuleReviewer().review(diff, parse_unified_diff(diff))
        self.assertEqual({"QUANT-SEC-HARDCODED-KEY", "QUANT-FF-SHIFT-NEG"}, {item.rule_id for item in findings})
        self.assertTrue(all(item.line in {1, 2} for item in findings))


if __name__ == "__main__":
    unittest.main()

