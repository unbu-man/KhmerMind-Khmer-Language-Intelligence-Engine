"""A small byte-pair encoder for the Khmer–English tokenization study."""
import unicodedata
from collections import Counter
from dataclasses import dataclass


def normalize_token_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


def _merge(sequence: tuple[int, ...], left: int, right: int, symbol: int) -> tuple[int, ...]:
    result = []
    index = 0
    while index < len(sequence):
        if index + 1 < len(sequence) and sequence[index:index + 2] == (left, right):
            result.append(symbol)
            index += 2
        else:
            result.append(sequence[index])
            index += 1
    return tuple(result)


@dataclass(frozen=True)
class BytePairEncoder:
    merges: tuple[tuple[int, int], ...]

    @classmethod
    def train(cls, texts: Counter[str], merge_limit: int) -> "BytePairEncoder":
        if merge_limit < 0:
            raise ValueError("Merge limit must be nonnegative.")
        sequences = Counter()
        for text, weight in texts.items():
            if weight > 0:
                sequences[tuple(normalize_token_text(text).encode("utf-8"))] += weight
        rules = []
        for rank in range(merge_limit):
            counts = Counter()
            for sequence, weight in sequences.items():
                for pair in zip(sequence, sequence[1:]):
                    counts[pair] += weight
            if not counts:
                break
            left, right = min(counts, key=lambda pair: (-counts[pair], pair))
            rules.append((left, right))
            updated = Counter()
            for sequence, weight in sequences.items():
                updated[_merge(sequence, left, right, 256 + rank)] += weight
            sequences = updated
        return cls(tuple(rules))

    def encode(self, text: str) -> tuple[int, ...]:
        symbols = tuple(normalize_token_text(text).encode("utf-8"))
        for rank, (left, right) in enumerate(self.merges):
            symbols = _merge(symbols, left, right, 256 + rank)
        return symbols

    def decode(self, tokens: tuple[int, ...]) -> str:
        pieces = [bytes([byte]) for byte in range(256)]
        for left, right in self.merges:
            pieces.append(pieces[left] + pieces[right])
        return b"".join(pieces[token] for token in tokens).decode("utf-8")
