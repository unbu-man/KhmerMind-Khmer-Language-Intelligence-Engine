"""Text processing shared by retrieval and the neural baselines."""
import math
import re
import unicodedata
import zlib
from collections import Counter


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\u200b", "").casefold()
    text = re.sub(r"[?!.,។៖]+", " ", text)
    return " ".join(text.split())


def ngrams(question: str) -> Counter[str]:
    text = normalize(question)
    return Counter(
        text[index:index + width]
        for width in (2, 3, 4)
        for index in range(len(text) - width + 1)
    )


def hashed_features(question: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for gram, count in ngrams(question).items():
        bucket = zlib.crc32(gram.encode("utf-8")) % dimensions
        vector[bucket] += count
    length = math.sqrt(sum(value * value for value in vector))
    return [value / length for value in vector] if length else vector
