"""Validate configuration for the demo and benchmarks."""
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    seeds: tuple[int, ...]
    dimensions: int
    hidden_units: int
    steps: int
    batch_size: int
    replay_samples: int
    replay_capacity: int
    learning_rate: float
    neural_threshold: float
    retrieval_min_score: float
    retrieval_min_gap: float

    @classmethod
    def load(cls, path: Path):
        values = json.loads(path.read_text(encoding="utf-8"))
        values["seeds"] = tuple(values["seeds"])
        config = cls(**values)
        positive = (config.dimensions, config.hidden_units, config.steps, config.batch_size)
        if any(type(value) is not int or value < 1 for value in positive):
            raise ValueError("Dimensions, hidden units, steps and batch size must be positive integers.")
        if type(config.replay_samples) is not int or not 0 <= config.replay_samples < config.batch_size:
            raise ValueError("Replay samples must be an integer smaller than the batch size.")
        if type(config.replay_capacity) is not int or config.replay_capacity < 0:
            raise ValueError("Replay capacity must be a nonnegative integer.")
        if not config.seeds or any(type(seed) is not int or seed < 0 for seed in config.seeds):
            raise ValueError("Provide one or more nonnegative integer seeds.")
        if len(config.seeds) != len(set(config.seeds)):
            raise ValueError("Seeds must be unique.")
        thresholds = (config.neural_threshold, config.retrieval_min_score, config.retrieval_min_gap)
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in thresholds):
            raise ValueError("Thresholds must be between 0 and 1.")
        if not math.isfinite(config.learning_rate) or config.learning_rate <= 0:
            raise ValueError("Learning rate must be positive and finite.")
        return config


