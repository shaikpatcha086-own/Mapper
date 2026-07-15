import unittest

from ai_assistant import NoMapAIAssistant


class TestNoMapAIAssistant(unittest.TestCase):

    def test_returns_suggestions_for_known_business_match(self):
        assistant = NoMapAIAssistant(top_n=2)

        target = {
            "field": "CustomerAccount",
            "description": "Customer account"
        }

        source_metadata = [
            {"field": "WorkerId", "description": "Worker identifier"},
            {"field": "ClientId", "description": "Customer identifier"},
        ]

        suggestions = assistant.suggest_for_nomap(
            target,
            source_metadata
        )

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertIn("source_field", suggestions[0])
        self.assertIn("confidence", suggestions[0])


if __name__ == "__main__":
    unittest.main()
