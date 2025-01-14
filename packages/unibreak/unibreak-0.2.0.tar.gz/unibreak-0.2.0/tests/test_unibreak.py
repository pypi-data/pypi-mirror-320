import unittest
import unibreak

class TestUnibreak(unittest.TestCase):
    def test_split_words_basic(self):
        text = "Hello World"
        result = unibreak.split_words(text)
        self.assertEqual(result, ["Hello", " ", "World"])

    def test_split_words_emoji(self):
        text = "Hi👋Bye"
        result = unibreak.split_words(text)
        self.assertEqual(result, ["Hi", "👋", "Bye"])

    def test_split_words_devanagari(self):
        text = "नमस्ते दुनिया"
        result = unibreak.split_words(text)
        self.assertEqual(result, ["नमस्ते", " ", "दुनिया"])

    def test_split_graphemes_combined(self):
        text = "é" # e + acute accent
        result = unibreak.split_graphemes(text)
        self.assertEqual(len(result), 1)  # Should be one grapheme
        self.assertEqual(result[0], "é")

    def test_split_graphemes_emoji(self):
        text = "👨‍👩‍👧‍👦"  # Family emoji (multiple code points)
        result = unibreak.split_graphemes(text)
        self.assertEqual(len(result), 1)  # Should be one grapheme
        
    def test_word_indices(self):
        text = "Hello World"
        result = unibreak.word_indices(text)
        self.assertEqual(result, [0, 5, 6])  # Start, space, and after space

    def test_grapheme_indices(self):
        text = "Hi👋Bye"
        result = unibreak.grapheme_indices(text)
        self.assertEqual(len(result), 6)  # H, i, 👋, B, y, e

    def test_grapheme_len(self):
        text = "é👨‍👩‍👧‍👦नमस्ते"  # Combined character, complex emoji, Devanagari
        result = unibreak.grapheme_len(text)
        self.assertEqual(result, 5)  # é(1) + family(1) + नमस्ते(3)

    def test_is_word_boundary(self):
        text = "Hello World"
        self.assertTrue(unibreak.is_word_boundary(text, 0))  # Start
        self.assertTrue(unibreak.is_word_boundary(text, 5))  # After "Hello"
        self.assertFalse(unibreak.is_word_boundary(text, 2))  # Middle of "Hello"
        self.assertFalse(unibreak.is_word_boundary(text, 20))  # Beyond text

    def test_split_word_bound_indices(self):
        text = "Hi👋Bye"
        result = unibreak.split_word_bound_indices(text)
        expected = [(0, "Hi"), (2, "👋"), (6, "Bye")]
        self.assertEqual(result, expected)

    def test_empty_string(self):
        text = ""
        self.assertEqual(unibreak.split_words(text), [])
        self.assertEqual(unibreak.split_graphemes(text), [])
        self.assertEqual(unibreak.word_indices(text), [])
        self.assertEqual(unibreak.grapheme_indices(text), [])
        self.assertEqual(unibreak.grapheme_len(text), 0)
        self.assertFalse(unibreak.is_word_boundary(text, 0))  # Empty string has no word boundaries
        self.assertEqual(unibreak.split_word_bound_indices(text), [])  # Empty string has no word boundaries

if __name__ == '__main__':
    unittest.main()
