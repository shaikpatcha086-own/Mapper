import unittest

from matcher import Matcher


class TestMatcherSmoke(unittest.TestCase):

    def test_matcher_picks_exact_match(self):
        matcher = Matcher()

        source_metadata = [
            {"field": "CustomerAccount", "description": "Customer account"},
            {"field": "WorkerId", "description": "Worker identifier"},
        ]

        target = {
            "row": 1,
            "field": "CustomerAccount",
            "description": "Customer account",
        }

        result = matcher.match_target(target, source_metadata)

        self.assertIsNotNone(result)
        self.assertEqual(result["source_field"], "CustomerAccount")
        self.assertIn(result["status"], {"Auto Accept", "Review"})


if __name__ == "__main__":
    unittest.main()
