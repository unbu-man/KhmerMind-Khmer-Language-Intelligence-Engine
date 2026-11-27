"""Read and validate the additions benchmark dataset."""
import json
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

from .text import normalize

SPLITS = ("train", "validation", "test")


@dataclass(frozen=True)
class Fact:
    fact_id: str
    version_id: str
    session: int
    topic: str
    answer: str
    source_id: str


@dataclass(frozen=True)
class Question:
    question_id: str
    fact_id: str | None
    split: str
    paraphrase_group: str
    text: str


@dataclass(frozen=True)
class Dataset:
    facts: dict[str, Fact]
    questions: tuple[Question, ...]

    @property
    def sessions(self) -> tuple[int, ...]:
        return tuple(sorted({fact.session for fact in self.facts.values()}))

    def training(self, session: int) -> list[Question]:
        return [
            question for question in self.questions
            if question.split == "train" and self.facts[question.fact_id].session == session
        ]

    def reordered(self, order: tuple[int, ...]) -> "Dataset":
        if sorted(order) != list(self.sessions):
            raise ValueError(f"Release order must be a permutation of {self.sessions}.")
        release = {original: new for new, original in enumerate(order, 1)}
        return Dataset(
            {key: replace(fact, session=release[fact.session]) for key, fact in self.facts.items()},
            self.questions,
        )

    def evaluation(self, split: str, session: int) -> list[Question]:
        return [
            question for question in self.questions
            if question.split == split
            and (question.fact_id is None or self.facts[question.fact_id].session <= session)
        ]

    def summary(self) -> dict:
        return {
            "facts": len(self.facts),
            "sessions": dict(sorted(Counter(fact.session for fact in self.facts.values()).items())),
            "questions_by_split": dict(Counter(question.split for question in self.questions)),
            "unknown_questions": sum(question.fact_id is None for question in self.questions),
        }


def _read_rows(path: Path, row_type) -> list:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(row_type(**json.loads(line)))
            except (TypeError, ValueError) as error:
                raise ValueError(f"{path}:{line_number}: {error}") from error
    return rows


def _nonempty(*values) -> bool:
    return all(isinstance(value, str) and value.strip() for value in values)


def load_dataset(directory: Path) -> Dataset:
    facts = {}
    versions = set()
    for fact in _read_rows(directory / "facts.jsonl", Fact):
        if not _nonempty(fact.fact_id, fact.version_id, fact.topic, fact.answer, fact.source_id):
            raise ValueError("Each fact needs a nonempty ID, version, topic, answer and source.")
        if type(fact.session) is not int or fact.session < 1:
            raise ValueError(f"{fact.fact_id}: session must be a positive integer.")
        if fact.fact_id in facts or fact.version_id in versions:
            raise ValueError(f"{fact.fact_id}: duplicate fact ID or version ID.")
        facts[fact.fact_id] = fact
        versions.add(fact.version_id)

    questions = tuple(_read_rows(directory / "questions.jsonl", Question))
    dataset = Dataset(facts, questions)
    sessions = dataset.sessions
    if not sessions or sessions != tuple(range(1, len(sessions) + 1)):
        raise ValueError("Release sessions must be consecutive starting at 1.")

    identifiers = set()
    normalized_texts = {}
    group_splits = {}
    fact_splits = {}
    unknown_splits = set()
    for question in questions:
        if not _nonempty(question.question_id, question.split, question.paraphrase_group,
                         question.text):
            raise ValueError("Question IDs, splits, paraphrase groups and text must be nonempty.")
        if question.question_id in identifiers:
            raise ValueError(f"{question.question_id}: duplicate question ID.")
        identifiers.add(question.question_id)
        if question.split not in SPLITS:
            raise ValueError(f"{question.question_id}: invalid split {question.split}.")
        if question.fact_id is None:
            if question.split == "train":
                raise ValueError(f"{question.question_id}: unknown questions are evaluation-only.")
            unknown_splits.add(question.split)
        else:
            if not isinstance(question.fact_id, str) or question.fact_id not in facts:
                raise ValueError(f"{question.question_id}: unknown fact ID.")
            fact_splits.setdefault(question.fact_id, set()).add(question.split)

        text = normalize(question.text)
        if not text:
            raise ValueError(f"{question.question_id}: question is empty after normalization.")
        if text in normalized_texts:
            other = normalized_texts[text]
            raise ValueError(f"{question.question_id}: duplicate normalized question {other}.")
        normalized_texts[text] = question.question_id
        previous_split = group_splits.setdefault(question.paraphrase_group, question.split)
        if previous_split != question.split:
            raise ValueError(f"{question.paraphrase_group}: paraphrase group crosses splits.")

    for fact_id in facts:
        if fact_splits.get(fact_id) != set(SPLITS):
            raise ValueError(f"{fact_id}: provide training, validation, and test questions.")
    if unknown_splits != {"validation", "test"}:
        raise ValueError("Include out-of-scope questions in both evaluation splits.")
    return dataset
