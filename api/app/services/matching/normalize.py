import re
import unicodedata


def normalize(text: str) -> str:
    """Lowercase, strip accents, drop punctuation, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9\s+]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
