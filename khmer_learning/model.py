"""Small linear and feedforward classifiers with manually written gradients."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Classifier:
    weights: np.ndarray
    bias: np.ndarray
    hidden_weights: np.ndarray | None = None
    hidden_bias: np.ndarray | None = None

    @classmethod
    def initialize(cls, dimensions: int, classes: int, hidden: int, seed: int):
        if hidden == 0:
            return cls(np.zeros((dimensions, classes)), np.zeros(classes))
        rng = np.random.default_rng(seed)
        hidden_weights = rng.normal(0, np.sqrt(2 / dimensions), (dimensions, hidden))
        head = rng.normal(0, np.sqrt(1 / hidden), (hidden, classes))
        return cls(head, np.zeros(classes), hidden_weights, np.zeros(hidden))

    def copy(self):
        return Classifier(
            self.weights.copy(),
            self.bias.copy(),
            None if self.hidden_weights is None else self.hidden_weights.copy(),
            None if self.hidden_bias is None else self.hidden_bias.copy(),
        )

    def expand(self, added_classes: int) -> None:
        self.weights = np.pad(self.weights, ((0, 0), (0, added_classes)))
        self.bias = np.pad(self.bias, (0, added_classes))

    def _forward(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        activations = features
        if self.hidden_weights is not None:
            activations = np.maximum(features @ self.hidden_weights + self.hidden_bias, 0)
        logits = activations @ self.weights + self.bias
        return activations, logits

    def predict(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        _, logits = self._forward(features)
        probabilities = np.exp(log_softmax(logits))
        best = probabilities.argmax(axis=1)
        return best, probabilities[np.arange(len(best)), best]

    def loss_and_gradients(self, features: np.ndarray, labels: np.ndarray):
        activations, logits = self._forward(features)
        log_probabilities = log_softmax(logits)
        rows = np.arange(len(labels))
        loss = -log_probabilities[rows, labels].mean()
        logit_gradient = np.exp(log_probabilities)
        logit_gradient[rows, labels] -= 1
        logit_gradient /= len(rows)
        gradients = [
            (self.weights, activations.T @ logit_gradient),
            (self.bias, logit_gradient.sum(axis=0)),
        ]
        if self.hidden_weights is not None:
            hidden_gradient = (logit_gradient @ self.weights.T) * (activations > 0)
            gradients.extend([
                (self.hidden_weights, features.T @ hidden_gradient),
                (self.hidden_bias, hidden_gradient.sum(axis=0)),
            ])
        return float(loss), gradients

    @property
    def parameter_bytes(self) -> int:
        parameters = (self.weights, self.bias, self.hidden_weights, self.hidden_bias)
        return sum(parameter.nbytes for parameter in parameters if parameter is not None)


def log_softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def fit(
    model: Classifier, features: np.ndarray, labels: np.ndarray, new: list[int], old: list[int],
    steps: int, batch_size: int, replay_samples: int, learning_rate: float, seed: int,
) -> None:
    rng = np.random.default_rng(seed)
    old_count = replay_samples if old else 0
    for _ in range(steps):
        batch = rng.choice(new, size=batch_size - old_count)
        if old_count:
            batch = np.concatenate((batch, rng.choice(old, size=old_count)))
        _, gradients = model.loss_and_gradients(features[batch], labels[batch])
        for parameter, gradient in gradients:
            parameter -= learning_rate * gradient
