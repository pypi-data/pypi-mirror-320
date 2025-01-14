use pyo3::prelude::*;
use unicode_segmentation::UnicodeSegmentation;

/// Split text into words using Unicode word boundaries
#[pyfunction]
fn split_words(text: &str) -> Vec<String> {
    text.split_word_bounds().map(|s| s.to_string()).collect()
}

/// Split text into grapheme clusters (visible characters)
#[pyfunction]
fn split_graphemes(text: &str) -> Vec<String> {
    text.graphemes(true).map(|s| s.to_string()).collect()
}

/// Get word boundary indices in text
#[pyfunction]
fn word_indices(text: &str) -> Vec<usize> {
    text.split_word_bound_indices().map(|(i, _)| i).collect()
}

/// Get grapheme cluster boundary indices in text
#[pyfunction]
fn grapheme_indices(text: &str) -> Vec<usize> {
    text.grapheme_indices(true).map(|(i, _)| i).collect()
}

/// Count grapheme clusters (visible characters) in text
#[pyfunction]
fn grapheme_len(text: &str) -> usize {
    text.graphemes(true).count()
}

/// Check if index is at a word boundary
#[pyfunction]
fn is_word_boundary(text: &str, index: usize) -> bool {
    if index > text.len() {
        return false;
    }
    text.split_word_bound_indices().any(|(i, _)| i == index)
}

/// A Python module implemented in Rust for Unicode text segmentation
#[pymodule]
fn unibreak(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(split_words, m)?)?;
    m.add_function(wrap_pyfunction!(split_graphemes, m)?)?;
    m.add_function(wrap_pyfunction!(word_indices, m)?)?;
    m.add_function(wrap_pyfunction!(grapheme_indices, m)?)?;
    m.add_function(wrap_pyfunction!(grapheme_len, m)?)?;
    m.add_function(wrap_pyfunction!(is_word_boundary, m)?)?;
    Ok(())
}
