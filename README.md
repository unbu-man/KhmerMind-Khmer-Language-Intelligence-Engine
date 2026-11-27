# KhmerMind · Khmer Language Intelligence Engine

A study and research repository for building a Khmer NLP system from scratch. Start by learning how text becomes features, how a model predicts, and how to measure what it remembers after an update.

**New to the project?** Follow [KhmerMind from 0 to 100](START_HERE.md). Start with [Lesson 00](lessons/00-first-khmer-question.md), then work through the exercises and record what you can reproduce.

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
