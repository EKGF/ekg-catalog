"""Configuration constants for use case documentation processing."""

from pathlib import Path

# Base directories
DOCS_DIR = Path(__file__).parent.parent
USE_CASE_DIR = DOCS_DIR / "use-case"
DIAGRAMS_SRC_DIR = DOCS_DIR / "diagrams" / "src"
DIAGRAMS_OUT_DIR = DOCS_DIR / "diagrams" / "out"
DIAGRAMS_INCLUDE_DIR = DOCS_DIR / "diagrams" / "include"

# Stop words for keyword extraction
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "into",
    "across",
    "about",
    "your",
    "their",
    "they",
    "them",
    "can",
    "our",
    "you",
    "why",
    "how",
    "what",
    "when",
    "where",
    "who",
}
