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

    def test_duplicate_source_field_names_across_sources_can_both_map(self):
        matcher = Matcher()

        source_metadata = [
            {
                "field": "CustomerAccount",
                "description": "Customer account",
                "source_id": "file1.xlsx::Sheet1::2",
                "source_entity": "CustTable"
            },
            {
                "field": "CustomerAccount",
                "description": "Customer account",
                "source_id": "file2.xlsx::SheetA::2",
                "source_entity": "CustomerView"
            },
        ]

        target1 = {
            "row": 1,
            "field": "CustomerAccount",
            "description": "Customer account",
        }

        target2 = {
            "row": 2,
            "field": "CustomerAccount",
            "description": "Customer account",
        }

        result1 = matcher.match_target(target1, source_metadata)
        result2 = matcher.match_target(target2, source_metadata)

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertNotEqual(result1.get("source_id"), result2.get("source_id"))


if __name__ == "__main__":
    unittest.main()
