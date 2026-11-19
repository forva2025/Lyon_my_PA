import unittest

from rag_engine import split_into_chunks


class ChunkingTests(unittest.TestCase):
    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(split_into_chunks("   "), [])

    def test_short_text_returns_one_chunk(self):
        self.assertEqual(split_into_chunks("hello world", 100, 10), ["hello world"])

    def test_long_text_is_split_and_overlapped(self):
        text = "0123456789 " * 40
        chunks = split_into_chunks(text, chunk_size=80, overlap=15)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 80 for chunk in chunks))
        self.assertTrue(all(chunk.strip() for chunk in chunks))

    def test_invalid_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            split_into_chunks("some text", chunk_size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
