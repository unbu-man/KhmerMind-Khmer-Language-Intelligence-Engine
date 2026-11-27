# KhmerMind from 0 to 100

Start with one Khmer question, understand every input and output, then build an experiment that shows what the model learns and what it forgets. The practice scripts in these lessons are small enough to type and inspect. Keep your implementation in your own project folder as you go.

## Where to start today

Read [Lesson 00 · Answer your first Khmer question](lessons/00-first-khmer-question.md). You can do the first half on paper if Python is not set up. Then run the example and explain why the same safety-stock question gives different results in releases 1 and 2. That is your first milestone.

## The milestones

| Milestone | Learn | Build or verify |
| --- | --- | --- |
| **0–10 · One question** | [Lesson 00 · Lookup and releases](lessons/00-first-khmer-question.md) | Run the example and trace one known, future, and out-of-scope question. |
| **10–20 · A small dataset** | [Lesson 01 · Problem and data](lessons/01-problem-and-data.md) | Write your own fact and question tables. Keep distinct wording families in separate splits. |
| **20–35 · Khmer text and search** | [Lesson 02 · Text](lessons/02-khmer-text.md), [Lesson 03 · Retrieval](lessons/03-retrieval.md), [Practice 01](practice/01-first-retrieval.md) | Run the character n-gram search. Explain a good match, a wrong match, and an abstention. Then compare it with TF-IDF. |
| **35–55 · Classify a question** | [Lesson 04 · Model math](lessons/04-model-math.md) | Implement a linear classifier and then an FFN. Show the loss dropping and check an analytical gradient by hand or finite difference. |
| **55–75 · Study updating and forgetting** | [Lesson 06 · Continual learning](lessons/06-continual-learning.md), [Practice 02](practice/02-first-continual-experiment.md) | Run the two-release experiment. Calculate old accuracy, new accuracy, and forgetting. Explain how replay changes the training batch. |
| **75–90 · Run a reproducible study** | [Research protocol](research/protocol.md), [Annotated readings](research/reading-list.md) | Prepare the larger dataset. Compare sequential training, replay, and retrieval on fixed splits and budgets. Save per-question results. |
| **90–100 · Share your work** | [Research protocol · Reproduce a run](research/protocol.md#5-save-enough-evidence-to-reproduce-a-run) | Publish a recorded demo or runnable command, the benchmark table, and an error analysis. Ask a classmate to reproduce one table. |

Use [Lesson 05 · Sequence models](lessons/05-sequence-models.md) after the FFN or after the first continual-learning result. It gives you the foundations for comparing an RNN or Transformer against the smaller baseline. The first end-to-end result can use a linear classifier.

## What 100 looks like

Present one example of a Khmer question asked before and after its fact arrives. Show the released version of the answer and what the system does when unsure. In the research report, show old-session accuracy, new-session accuracy, forgetting, unknown false-answer rate, and update costs. State your dataset size and what claims it supports. A measured tradeoff is a valid result.

After each milestone, write down one decision, one expected result, the observed result, and one error or open question. Use a commit message that describes the work, such as `Add glossary release checks`. This makes the repository a record of how your project changed.
