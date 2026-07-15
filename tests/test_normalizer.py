import unittest

from normalizer import contains


class TestNormalizerContains(unittest.TestCase):

    def test_contains_returns_false_for_empty_left(self):
        self.assertFalse(contains("", "CustomerAccount"))

    def test_contains_returns_false_for_empty_right(self):
        self.assertFalse(contains("CustomerAccount", ""))

    def test_contains_returns_true_for_partial_match(self):
        self.assertTrue(contains("Customer", "CustomerAccount"))


if __name__ == "__main__":
    unittest.main()
