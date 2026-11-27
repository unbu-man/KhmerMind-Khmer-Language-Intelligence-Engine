"""Summarize correctness, abstention, and forgetting across releases."""
from collections import defaultdict
from dataclasses import dataclass

from .data import Dataset, Question


@dataclass(frozen=True)
class Prediction:
    fact_id: str | None
    score: float
    best_fact_id: str | None


def _forgetting(current: dict, previous: list[dict], key: str, session: int) -> float | None:
    drops = [
        max(row[key][earlier] for row in previous if earlier in row[key]) - accuracy
        for earlier, accuracy in current.items() if earlier < session
    ]
    return _ratio(sum(drops), len(drops))


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def score(
    dataset: Dataset, questions: list[Question], predictions: list[Prediction],
    session: int, previous: list[dict],
) -> tuple[dict, list[dict]]:
    totals = defaultdict(int)
    correct = defaultdict(int)
    top_correct = defaultdict(int)
    answered_known = 0
    answered_unknown = 0
    rows = []
    for question, prediction in zip(questions, predictions, strict=True):
        guess = prediction.fact_id
        best = prediction.best_fact_id
        expected = question.fact_id
        introduced = dataset.facts[expected].session if expected is not None else None
        if introduced is None:
            answered_unknown += guess is not None
        else:
            totals[introduced] += 1
            correct[introduced] += guess == expected
            top_correct[introduced] += best == expected
            answered_known += guess is not None
        rows.append({
            "question_id": question.question_id,
            "introduced_session": introduced,
            "expected_version_id": dataset.facts[expected].version_id if expected else None,
            "predicted_version_id": dataset.facts[guess].version_id if guess else None,
            "top_version_id": dataset.facts[best].version_id if best else None,
            "score": prediction.score,
        })

    per_session = {earlier: correct[earlier] / size for earlier, size in sorted(totals.items())}
    top_per_session = {earlier: top_correct[earlier] / size for earlier, size in sorted(totals.items())}
    old_sessions = [earlier for earlier in per_session if earlier < session]
    known = sum(totals.values())
    unknown = len(questions) - known
    right = sum(correct.values())
    return {
        "accuracy_by_session": per_session,
        "counts_by_session": dict(totals),
        "known_accuracy": right / known,
        "top_known_accuracy": sum(top_correct.values()) / known,
        "top_accuracy_by_session": top_per_session,
        "top_old_accuracy": _ratio(sum(top_per_session[earlier] for earlier in old_sessions),
                                   len(old_sessions)),
        "top_new_accuracy": top_per_session[session],
        "top_forgetting": _forgetting(top_per_session, previous, "top_accuracy_by_session", session),
        "old_accuracy": _ratio(sum(per_session[earlier] for earlier in old_sessions),
                               len(old_sessions)),
        "new_accuracy": per_session[session],
        "forgetting": _forgetting(per_session, previous, "accuracy_by_session", session),
        "known_accuracy_when_answered": _ratio(right, answered_known),
        "unknown_false_answer_rate": _ratio(answered_unknown, unknown),
        "known_abstentions": known - answered_known,
        "unknown_questions": unknown,
        "coverage": (answered_known + answered_unknown) / len(questions),
    }, rows
