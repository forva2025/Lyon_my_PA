import unittest

from rag_engine import canonical_ollama_model_name, ollama_model_is_installed


class OllamaModelDetectionTests(unittest.TestCase):
    def test_implicit_latest_tag_is_expanded(self):
        self.assertEqual(
            canonical_ollama_model_name("nomic-embed-text"),
            "nomic-embed-text:latest",
        )

    def test_explicit_tag_is_preserved(self):
        self.assertEqual(
            canonical_ollama_model_name("qwen3:1.7b"),
            "qwen3:1.7b",
        )

    def test_implicit_and_explicit_latest_names_match(self):
        self.assertTrue(
            ollama_model_is_installed(
                "nomic-embed-text",
                ["nomic-embed-text:latest", "qwen3:1.7b"],
            )
        )

    def test_different_tag_does_not_match(self):
        self.assertFalse(
            ollama_model_is_installed("qwen3:1.7b", ["qwen3:0.6b"])
        )


if __name__ == "__main__":
    unittest.main()
