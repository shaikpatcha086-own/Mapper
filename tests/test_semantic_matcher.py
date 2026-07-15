import unittest

from semantic_matcher import semantic_matches, semantic_score


class TestSemanticMatcher(unittest.TestCase):

    def test_semantic_score_returns_number_without_crashing(self):
        score = semantic_score("WorkerId", "EmployeeResponsibleNumber")
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_semantic_matches_returns_list(self):
        matches = semantic_matches("ClientId", "CustomerAccount")
        self.assertIsInstance(matches, list)


if __name__ == "__main__":
    unittest.main()
