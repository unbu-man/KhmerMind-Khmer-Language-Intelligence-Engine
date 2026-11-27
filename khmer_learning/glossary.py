"""Shared query interface for the command line and browser demo."""
from dataclasses import asdict

from .config import Config
from .data import Dataset
from .retrieval import RetrievalIndex


class Glossary:
    def __init__(self, dataset: Dataset, config: Config):
        self.facts = dataset.facts
        self.config = config
        self.sessions = dataset.sessions
        self.indexes = {}
        visible = []
        for session in self.sessions:
            visible.extend(dataset.training(session))
            self.indexes[session] = RetrievalIndex(visible)

    def ask(self, question: str, release: int) -> dict:
        if release not in self.indexes:
            raise ValueError(f"Release must be one of {self.sessions}.")
        if not question.strip():
            raise ValueError("Enter a nonempty question.")
        match = self.indexes[release].match(
            question, self.config.retrieval_min_score, self.config.retrieval_min_gap
        )
        return {
            "question": question,
            "release": release,
            "status": "answered" if match.fact_id else "unknown",
            "fact": asdict(self.facts[match.fact_id]) if match.fact_id else None,
            "score": round(match.score, 6),
            "gap": round(match.gap, 6),
        }
