import unibreak

# Test text with various Unicode characters
text = "Hello 👋 World! नमस्ते"

print("Words:", unibreak.split_words(text))
print("Graphemes:", unibreak.split_graphemes(text))
print("Word indices:", unibreak.word_indices(text))
print("Grapheme indices:", unibreak.grapheme_indices(text))
print("Grapheme length:", unibreak.grapheme_len(text))
print(
    "Is word boundary at 5?", unibreak.is_word_boundary(text, 5)
)  # Space after "Hello"
print("Is word boundary at 6?", unibreak.is_word_boundary(text, 6))  # Middle of emoji
