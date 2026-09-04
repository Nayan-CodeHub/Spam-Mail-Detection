import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def preprocess_text(text):
    """Lowercase text, tokenize it, and remove English stopwords."""
    tokens = re.findall(r"[a-zA-Z]+", str(text).lower())
    return [token for token in tokens if token not in ENGLISH_STOP_WORDS]
