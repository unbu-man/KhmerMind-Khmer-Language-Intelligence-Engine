# Practice 02. Measure forgetting in a small Khmer classifier

**Before you start.** Complete [Practice 01](01-first-retrieval.md), then read [Lesson 04](../lessons/04-model-math.md) and [Lesson 06](../lessons/06-continual-learning.md). Use the original four glossary facts and keep both practice files in the same folder.

## 1. Decide what the experiment should prove

Train a linear classifier on two release-1 facts. Save its weights. Start two release-2 runs from those same weights. One run trains only on the two new facts. The other uses two old examples and two new examples per update. Both use the same batch size and number of optimizer steps.

A classifier sees only the query features when making a prediction. The replay buffer is used during training. The earlier retrieval practice searched stored wording during prediction.

| Group | Fact IDs | When training rows are available |
| --- | --- | --- |
| Old | `gross_revenue`, `net_revenue` | Release 1 |
| New | `repeat_customer`, `safety_stock` | Release 2 |

There are two training phrasings and one held-out phrasing for each fact. With only two held-out questions in each release, one different prediction changes accuracy by 50 percentage points. Use this deliberately small fixture to understand the mechanics.

## 2. Run the first weight update

Use a virtual environment for the exercise. On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install numpy
```

On Windows, use `py -m venv .venv` and activate using `.venv\Scripts\Activate.ps1` in PowerShell, then use `python -m pip install numpy`.

Create `practice02.py`. The feature vector has a fixed number of positions. A reproducible hash maps each character trigram to one position. This lets the input size stay the same when new text arrives. The last feature is a constant so the model can learn an intercept.

```python
import zlib

import numpy as np

from lesson00 import GLOSSARY
from practice01 import character_ngrams


FACT_IDS = ("gross_revenue", "net_revenue", "repeat_customer", "safety_stock")
EXTRA_QUESTIONS = (
    "ចំណូលសរុបគឺជាអ្វី?",
    "តើអ្វីទៅជាចំណូលសុទ្ធ?",
    "អតិថិជនទិញម្តងទៀតជាអ្នកណា?",
    "តើគេហៅអ្វីថាស្តុកបម្រុង?",
)
HELD_OUT = (
    ("តើអ្វីទៅជាចំណូលសរុប?", 0),
    ("សូមពន្យល់អំពីចំណូលសុទ្ធ។", 1),
    ("សូមពន្យល់ពាក្យអតិថិជនទិញម្តងទៀត។", 2),
    ("តើអ្វីទៅជាស្តុកបម្រុង?", 3),
)
FEATURES = 256
STEPS = 48
LEARNING_RATE = 0.4


def vectorize(question):
    vector = np.zeros(FEATURES + 1)
    for trigram in character_ngrams(question):
        position = zlib.crc32(trigram.encode("utf-8")) % FEATURES
        vector[position] = 1.0
    length = np.linalg.norm(vector)
    if length:
        vector /= length
    vector[-1] = 1.0
    return vector


def train(weights, active_classes, incoming, memory, seed):
    result = weights.copy()
    active = result[:, :active_classes]
    incoming_rng = np.random.default_rng(seed)
    memory_rng = np.random.default_rng(seed + 1)
    for _ in range(STEPS):
        old_count = 2 if memory else 0
        batch = [incoming[i] for i in incoming_rng.integers(len(incoming), size=4 - old_count)]
        if memory:
            batch += [memory[i] for i in memory_rng.integers(len(memory), size=old_count)]
        questions, labels = zip(*batch)
        x = np.stack([vectorize(question) for question in questions])
        logits = x @ active
        logits -= logits.max(axis=1, keepdims=True)
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        probabilities[np.arange(len(batch)), list(labels)] -= 1.0
        gradient = (x.T @ probabilities) / len(batch)
        active -= LEARNING_RATE * gradient
    return result


def accuracy(weights, active_classes, questions):
    right = 0
    for question, expected in questions:
        scores = vectorize(question) @ weights[:, :active_classes]
        right += int(scores.argmax() == expected)
    return right / len(questions)


if __name__ == "__main__":
    question_by_fact = {record["fact_id"]: question for question, record in GLOSSARY.items()}
    rows = [
        (question, label)
        for label, (identity, extra) in enumerate(zip(FACT_IDS, EXTRA_QUESTIONS))
        for question in (question_by_fact[identity], extra)
    ]
    old_train, new_train = rows[:4], rows[4:]
    old_test, new_test = HELD_OUT[:2], HELD_OUT[2:]
    zeros = np.zeros((FEATURES + 1, len(FACT_IDS)))
    for seed in (7, 19, 37):
        first = train(zeros, 2, old_train, [], seed)
        initial_old = accuracy(first, 2, old_test)
        print(f"Seed {seed} | release 1 old set: {initial_old:.0%}")
        for method, memory in (("sequential", []), ("replay", old_train)):
            second = train(first, 4, new_train, memory, seed + 10)
            old_score = accuracy(second, 4, old_test)
            new_score = accuracy(second, 4, new_test)
            forgetting = 100 * (initial_old - old_score)
            print(f"  {method:10s} old={old_score:.0%} new={new_score:.0%} forgetting={forgetting:+.0f} pp")
```

Run `python3 practice02.py`, or `python practice02.py` if that is the command inside your virtual environment.

## 3. Trace the math while reading the code

1. `x` has one row per training question. `active` contains a column for each answer class available at this release.
2. `x @ active` gives logits. Rows become probabilities after softmax.
3. Subtracting 1 from the correct class gives the per-example logit gradient. Multiplying by `x.T` and averaging gives the weight gradient.
4. The optimizer subtracts the gradient times the learning rate. Copying the incoming weights before training lets both release-2 runs start from the same state.

With two releases and one earlier-session score, forgetting in percentage points reduces to

$$
100\,(A_{1,1}-A_{2,1}).
$$

For example, if first-release accuracy is 50% and old-question accuracy after training falls to 0%, forgetting is 50 percentage points. At this scale, inspect which individual truth labels changed. This example scores known questions. Add out-of-scope queries and an abstention rule when you run the full protocol.

## 4. Read one verified run

The original exercise gave these results with Python 3.12 and NumPy 2.3.5. Both methods answered both new questions correctly for these seeds.

| Seed | Before release 2 | Old accuracy after sequential training | Old accuracy after replay |
| --- | ---: | ---: | ---: |
| 7 | 50% | 0% | 50% |
| 19 | 50% | 0% | 100% |
| 37 | 50% | 0% | 50% |

For seed 7 the sequential run forgot 50 percentage points, and the replay run forgot zero. For seed 19 replay improved the old score by 50 points, so forgetting was −50 points. Each held-out group has only two questions, and the memory holds all four old training rows. These results illustrate how to measure the effect. The larger study tests how well it holds under tighter memory budgets.

## 5. Interpret it and scale one piece at a time

- Make a table with seed, method, old accuracy, new accuracy, and forgetting. Identify a case where replay changes the old score. Check new accuracy at the same time.
- Reduce the old memory to a single example. Check which fact disappeared from the buffer and how the predictions change. Keep the same step count.
- Replace the in-memory tuples with reviewed, versioned data. Add an independently worded validation split and permanent unknowns. Then run three or more release sessions and report the full accuracy matrix.

The four-row memory here contains every release-1 training question. In the larger benchmark, compare bounded memory policies under the same constraints and use seed variation to describe uncertainty. Follow the [research protocol](../research/protocol.md).
