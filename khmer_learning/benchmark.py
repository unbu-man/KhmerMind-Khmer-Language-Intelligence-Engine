"""Compare incremental retrieval and matched-budget neural learning methods."""
import hashlib
import json
import platform
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import numpy as np

from .config import Config
from .data import Dataset, Question
from .metrics import Prediction, score
from .model import Classifier, fit
from .replay import Reservoir, balanced_memory
from .retrieval import RetrievalIndex
from .text import hashed_features, ngrams

NEURAL_METHODS = ("frozen", "sequential", "uniform_replay", "fact_balanced_replay", "full_history")


def _record(history, dataset, questions, predictions, session, elapsed, **counts) -> dict:
    metrics, prediction_rows = score(dataset, questions, predictions, session, history)
    row = {
        "session": session, "metrics": metrics, "predictions": prediction_rows,
        "update_seconds": round(elapsed, 6), **counts,
    }
    history.append(metrics)
    return row


def _retrieval_run(dataset: Dataset, config: Config, evaluations: dict) -> dict:
    history, rows, visible = [], [], []
    for session in dataset.sessions:
        started = perf_counter()
        visible.extend(dataset.training(session))
        index = RetrievalIndex(visible)
        elapsed = perf_counter() - started
        questions = evaluations[session]
        predictions = []
        for question in questions:
            match = index.match(question.text, config.retrieval_min_score, config.retrieval_min_gap)
            predictions.append(Prediction(match.fact_id, match.score, match.best_fact_id))
        rows.append(_record(
            history, dataset, questions, predictions, session, elapsed,
            indexed_questions=len(visible), index_vector_entries=index.vector_entries,
        ))
    return {"method": "retrieval", "seed": None, "sessions": rows}


def _transform(questions: list[Question], dimensions: int) -> np.ndarray:
    return np.asarray([hashed_features(question.text, dimensions) for question in questions])


def _neural_runs(dataset: Dataset, config: Config, evaluations: dict, hidden: int) -> list[dict]:
    sessions = dataset.sessions
    fact_ids = sorted(dataset.facts, key=lambda fact_id: (dataset.facts[fact_id].session, fact_id))
    label_by_fact = {fact_id: label for label, fact_id in enumerate(fact_ids)}
    active_classes = {
        session: sum(fact.session <= session for fact in dataset.facts.values())
        for session in sessions
    }
    training = [question for session in sessions for question in dataset.training(session)]
    features = _transform(training, config.dimensions)
    labels = np.asarray([label_by_fact[question.fact_id] for question in training])
    indices = {
        session: [index for index, question in enumerate(training)
                  if dataset.facts[question.fact_id].session == session]
        for session in sessions
    }
    evaluation_features = {
        session: _transform(questions, config.dimensions)
        for session, questions in evaluations.items()
    }
    evaluation_has_grams = {
        session: [bool(ngrams(question.text)) for question in questions]
        for session, questions in evaluations.items()
    }
    question_bytes = [
        len(json.dumps(asdict(question), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        for question in training
    ]

    runs = []
    for seed in config.seeds:
        started = perf_counter()
        initial = Classifier.initialize(config.dimensions, active_classes[1], hidden, seed)
        fit(initial, features, labels, indices[1], [], config.steps, config.batch_size,
            0, config.learning_rate, seed)
        first_elapsed = perf_counter() - started
        for method in NEURAL_METHODS:
            history, rows, seen = [], [], []
            model = initial.copy()
            reservoir = Reservoir(config.replay_capacity)
            buffer = []
            for session in sessions:
                new = indices[session]
                seen.extend(new)
                started = perf_counter()
                steps = config.steps
                rehearsal_before_update = 0
                full_history_training_rows = 0
                if session > 1:
                    if method == "frozen":
                        steps = 0
                    elif method == "full_history":
                        model = Classifier.initialize(
                            config.dimensions, active_classes[session], hidden, seed
                        )
                        steps *= session
                        full_history_training_rows = len(seen)
                        fit(model, features, labels, seen, [], steps, config.batch_size,
                            0, config.learning_rate, seed + session)
                    else:
                        model.expand(active_classes[session] - model.weights.shape[1])
                        rehearsal_before_update = len(buffer)
                        fit(model, features, labels, new, buffer, steps, config.batch_size,
                            config.replay_samples, config.learning_rate, seed + session)

                if method == "uniform_replay":
                    reservoir.add(new, np.random.default_rng([seed, session, 1]))
                    buffer = reservoir.items
                elif method == "fact_balanced_replay":
                    buffer = balanced_memory(
                        buffer, new, labels, config.replay_capacity,
                        np.random.default_rng([seed, session, 2]),
                    )
                elapsed = perf_counter() - started
                if session == 1:
                    elapsed += first_elapsed

                indices_predicted, scores = model.predict(evaluation_features[session])
                predictions = [
                    Prediction(
                        fact_ids[int(index)] if has_grams and confidence >= config.neural_threshold
                        else None,
                        float(confidence),
                        fact_ids[int(index)] if has_grams else None,
                    )
                    for index, confidence, has_grams in zip(
                        indices_predicted, scores, evaluation_has_grams[session], strict=True
                    )
                ]
                rows.append(_record(
                    history, dataset, evaluations[session], predictions, session, elapsed,
                    optimizer_steps=steps, model_classes=model.weights.shape[1],
                    parameter_bytes=model.parameter_bytes, buffer_examples=len(buffer),
                    buffer_facts=len({int(labels[index]) for index in buffer}),
                    buffer_payload_bytes=sum(question_bytes[index] for index in buffer),
                    rehearsal_examples_available=rehearsal_before_update,
                    rehearsal_draws=steps * config.replay_samples if rehearsal_before_update else 0,
                    full_history_training_rows=full_history_training_rows,
                ))
            runs.append({"method": method, "seed": seed, "sessions": rows})
    return runs


def run_benchmark(
    dataset: Dataset, config: Config, split: str, model: str, data_path: Path,
    release_order: tuple[int, ...],
) -> dict:
    evaluations = {session: dataset.evaluation(split, session) for session in dataset.sessions}
    runs = [_retrieval_run(dataset, config, evaluations)]
    runs.extend(_neural_runs(dataset, config, evaluations, config.hidden_units if model == "ffn" else 0))
    return {
        "evaluation_split": split,
        "model": model,
        "release_order": list(release_order),
        "config": asdict(config),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "dataset": dataset.summary(),
        "data_sha256": {
            name: hashlib.sha256((data_path / name).read_bytes()).hexdigest()
            for name in ("facts.jsonl", "questions.jsonl")
        },
        "runs": runs,
    }
