# KhmerMind · Khmer Language Intelligence Engine

Khmer question answering for a versioned business glossary, with a from-scratch continual-learning benchmark. The demo returns a Khmer definition and its source when it finds a confident match.

**Review the project** · [Demo examples and findings](reports/README.md) · [Full benchmark tables](reports/results.md) · [Tokenization math](lessons/07-tokenization-math.md) · [Learning path](START_HERE.md)

## Run the demo

Use Python 3.11 or newer. Clone this repository and run these commands from the checkout root. Validation, search, and the local web interface use the Python standard library.

```bash
python3 -m khmer_learning validate
python3 -m khmer_learning demo
python3 -m khmer_learning ask 'តើស្តុកបម្រុងជាអ្វី?' --release 3
python3 -m khmer_learning serve
```

For the web interface, open `http://127.0.0.1:8000` on the same computer. Try the safety-stock example in release 1, then release 3. The earlier release abstains. The later release shows `safety_stock_v1` and its Khmer definition. The CLI supports `--json` for structured results.

## What is included

| Component | Contents |
| --- | --- |
| [Data](data/README.md) | 30 synthetic Khmer glossary facts across three releases, with 190 training and evaluation questions. |
| [Query engine](khmer_learning/) | Unicode character features, TF-IDF search, confidence and margin rules, and a local browser and CLI interface. |
| [Continual-learning benchmark](khmer_learning/benchmark.py) | Linear and feedforward classifiers with hand-written gradients, compared across retrieval, frozen, sequential, uniform replay, fact-balanced replay, and full-history methods. |
| [Evidence](reports/README.md) | Held-out results for three seeds and two release orders, a chart, examples of errors, and per-question outputs. |
| [Checks](tests/test_project.py) | Data leakage, release availability, matched training budgets, replay limits, FFN gradients, and browser API behavior. |

The demo searches a small fictional glossary. The first benchmark measures how precisely it can handle different wording and reject unknown questions. Independent Khmer review and evaluation against real business queries remain research milestones.

## Run the benchmark

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 -m khmer_learning benchmark --model linear --output reports/generated/validation.json
```

The report documents the exact commands for both backbones and both release orders. [Reproduce the published study](reports/README.md#recreate-the-report)

## Learn how it was built

Work through the [0–100 learning path](START_HERE.md) or start directly at [Lesson 00](lessons/00-first-khmer-question.md).

## The project we are working toward

An analyst asks «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» (“What does net revenue mean?”). The system identifies the glossary entry and returns the company’s definition. New definitions arrive in releases. The research question is whether a small model can learn those definitions without losing the ability to answer earlier questions.

The initial domain is a fictional company’s glossary for sales, customers, and inventory. You can practice with synthetic data and later validate the wording with fluent Khmer speakers. «ពីមូលដ្ឋាន» here means working through a hand example, writing the core algorithm yourself, and checking it against a known result.

## Learning order

| Start here | Study and practice | You can move on when you can… |
| --- | --- | --- |
| [01 · Frame the problem](lessons/01-problem-and-data.md) | Q&A, fact IDs, release sessions, train/validation/test | Write examples for a glossary and explain how wording could leak across splits. |
| [02 · Represent Khmer text](lessons/02-khmer-text.md) | Unicode, normalization, character n-grams, word segmentation, BPE | List the features of a short string and explain what a baseline may miss. |
| [03 · Search a glossary](lessons/03-retrieval.md) | Jaccard, TF-IDF, cosine, abstention | Rank two candidates by hand and explain when to return unknown. |
| [04 · Learn from labeled questions](lessons/04-model-math.md) | Count models, embeddings, softmax, cross-entropy, the FFN and backpropagation | Trace a model forward and verify one derivative by hand. |
| [05 · Read sequences](lessons/05-sequence-models.md) | RNN, LSTM, GRU, attention, Transformer encoder | Trace a hidden-state update and compute attention on two tokens. |
| [06 · Learn continually](lessons/06-continual-learning.md) | Incremental training, replay, forgetting, update budgets | Read an accuracy matrix and explain the difference between retention and new learning. |

Use the [research protocol](research/protocol.md) after Lesson 06 to design your first benchmark. The [annotated readings](research/reading-list.md) explain what published work contributes to each lesson and what remains a question for KhmerMind.

## Your first study session

1. Read Lesson 01 and sketch two releases using four glossary facts.
2. Write two differently worded Khmer questions about each fact.
3. Write two questions the system should decline. Include one question that sounds similar to a real glossary term.
4. Complete the exit exercise before starting tokenization. Save your notes and calculations in Git so you can see how your understanding develops.

For the first implementation you will need Python and Git. NumPy becomes useful once you reach the model math. A notebook or paper is enough for the first lessons.
