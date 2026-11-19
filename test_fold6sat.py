# SPDX-License-Identifier: Apache-2.0
# Tests for fold6sat.py (vuza-canons 0.5.1). Pure Python: the solver is never called.
# Made by MV2 of Munim, Inc., with AI agents.
import unittest

import fold6sat


class TestPlan(unittest.TestCase):
    def test_one_profile_and_one_phi6_case_each(self):
        for row in fold6sat.plan():
            self.assertEqual(row["profiles"], [[4, 5, 9]], row["cfg"])
            self.assertEqual(row["phi6_cases"], 1, row["cfg"])
            self.assertEqual(row["decided"], 0, row["cfg"])

    def test_periods(self):
        got = {c["name"]: c["M"] for c in fold6sat.configs()}
        self.assertEqual(got["S180-k6"], 1080)
        self.assertEqual(got["S180-k9"], 1620)
        self.assertEqual(got["S180-k30"], 5400)
        self.assertEqual(got["C180-k30"], 5400)

    def test_labels_follow_the_proposition(self):
        import foldlemma
        for c in fold6sat.configs():
            row = foldlemma.table_row(c["k"]) if c["k"] in (6, 30) else None
            if c["label"] == "hard-negative":
                self.assertNotEqual(c["k"] % 5, 0)
            else:
                self.assertEqual(c["k"], 30)
            if row is not None:
                self.assertTrue(row["fold_allows_phi6_failure"])


if __name__ == "__main__":
    unittest.main()
