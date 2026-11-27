"""Character TF-IDF retrieval over released training questions."""
import math
from collections import Counter
from dataclasses import dataclass

from .data import Question
from .text import ngrams


@dataclass(frozen=True)
class Match:
    fact_id: str | None
    score: float
    gap: float
    best_fact_id: str | None


class RetrievalIndex:
    def __init__(self, questions: list[Question]):
        counts = [ngrams(question.text) for question in questions]
        document_frequency = Counter(term for document in counts for term in document)
        self.idf = {
            term: math.log((1 + len(questions)) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }
        self.documents = [
            (question.fact_id, self._vector(document))
            for question, document in zip(questions, counts, strict=True)
        ]

    def _vector(self, counts: Counter) -> dict[str, float]:
        values = {term: value * self.idf[term] for term, value in counts.items()
                  if term in self.idf}
        norm = math.sqrt(sum(value * value for value in values.values()))
        return {term: value / norm for term, value in values.items()} if norm else {}

    def match(self, text: str, min_score: float, min_gap: float) -> Match:
        vector = self._vector(ngrams(text))
        per_fact = {}
        for fact_id, document in self.documents:
            score = sum(value * document.get(term, 0.0) for term, value in vector.items())
            per_fact[fact_id] = max(score, per_fact.get(fact_id, 0.0))
        ranked = sorted(per_fact.items(), key=lambda item: (-item[1], item[0]))
        if not ranked:
            return Match(None, 0.0, 0.0, None)
        fact_id, best = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        gap = best - second
        prediction = fact_id if vector and best >= min_score and gap >= min_gap else None
        return Match(prediction, best, gap, fact_id if vector else None)

    @property
    def vector_entries(self) -> int:
        return len(self.idf) + sum(len(document) for _, document in self.documents)
