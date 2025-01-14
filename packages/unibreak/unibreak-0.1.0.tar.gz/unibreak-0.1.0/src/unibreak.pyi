"""A Python module implemented in Rust for Unicode text segmentation"""

from typing import List

def split_words(text: str) -> List[str]:
    """Split text into words using Unicode word boundaries"""
    ...

def split_graphemes(text: str) -> List[str]:
    """Split text into grapheme clusters (visible characters)"""
    ...

def word_indices(text: str) -> List[int]:
    """Get word boundary indices in text"""
    ...

def grapheme_indices(text: str) -> List[int]:
    """Get grapheme cluster boundary indices in text"""
    ...

def grapheme_len(text: str) -> int:
    """Count grapheme clusters (visible characters) in text"""
    ...

def is_word_boundary(text: str, index: int) -> bool:
    """Check if index is at a word boundary"""
    ...
