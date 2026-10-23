import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.ai import AIClient


class AIClientTests(unittest.TestCase):
    def setUp(self):
        self.ai = AIClient.__new__(AIClient)
        self.ai.client = Mock()
        self.ai.model = "test-model"

    def test_summarize_patch_handles_missing_contents(self):
        result = self.ai.summarize_patch("Patch", None)

        self.assertEqual(result, "No content available to summarize.")
        self.ai.client.chat.completions.create.assert_not_called()

    def test_summarize_patch_reports_missing_model_content(self):
        self.ai.client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
        )

        result = self.ai.summarize_patch("Patch", "Patch notes")

        self.assertEqual(
            result, "AI summary failed: the model returned no summary content."
        )

    def test_chat_reports_missing_model_content(self):
        self.ai.client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
        )

        result = self.ai.chat_about_patch("Patch notes", "What changed?")

        self.assertEqual(
            result, "Chat failed: the model returned no response content."
        )


if __name__ == "__main__":
    unittest.main()
