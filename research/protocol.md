# KhmerMind research protocol

## 1. Pin down the question

**Research question.** Under a fixed optimizer-step and memory budget, does replay help a small Khmer fact classifier retain previously introduced facts while learning new ones?

**Comparison.** Start with a linear classifier using character n-grams. Use an FFN as a second backbone after you can gradient-check it. Compare sequential training with uniform replay and fact-balanced replay. A frozen model gives a no-update reference. Full-history retraining is an offline reference with a separately reported cost. As a product baseline, compare incremental TF-IDF retrieval over the same released training questions.

**Hypothesis.** Replay will improve retention relative to sequential training. Report the accompanying changes in new accuracy and unknown false answers. Fact-balanced replay is an experimental variant of the memory policy. Its benefit on Khmer glossary data remains an empirical question.

The system predicts which glossary answer version applies to the input. It can display the text after predicting the ID. This experiment measures closed-book fact identification with a structured answer map. Supporting open-ended answer generation would require its own task and evaluation.

## 2. Prepare and document the dataset

1. Begin with four reviewed synthetic facts across two releases to debug the workflow. Expand to a suggested starting target of 30 facts across three releases when the validator passes.
2. Write several independently worded questions per fact, mixing short searches, full questions, and longer scenarios where natural. Ask a fluent Khmer reviewer to flag ambiguous or unnatural wording. Log feedback, provenance, and rights for any external examples.
3. Assign wording families and keep each family in one split. Deduplicate normalized strings across train, validation, and test. Require independently worded held-out examples for every answerable fact.
4. Record one release date or number per initial fact. Validate unique fact, version, and question IDs, foreign keys, nonempty text, continuous releases, and split coverage. Report class and session counts before training.
5. Include permanent unknowns in validation and test. Include hard unknowns that share terms with known facts. Optionally report future-fact probes separately before their release.
6. Freeze the data version and splits. Give each method only released training examples. If you use a learned vocabulary, fix it from the first training session for the main comparison or explicitly version it under a common protocol. Character hashing avoids fitting a vocabulary. Keep later data out of earlier index statistics, threshold selection, and training.

See [Lesson 01](../lessons/01-problem-and-data.md) for a fact and question schema. For external text, preserve the form and origin of each excerpt. A general corpus can support vocabulary or tokenizer study. The benchmark needs reviewed questions aligned to your glossary facts.

## 3. Predeclare an update schedule

| Decision | Suggested first experiment |
| --- | --- |
| Seeds | 7, 19, 37, paired across methods |
| Testing | Evaluate all released sessions after each update, using the same held-out questions |
| Neural training | Identical initial checkpoint per seed for all warm-start methods |
| Class availability | Add answer classes as facts arrive. Keep old class IDs stable. The frozen reference keeps its original classes. |
| Update budget | Same optimizer, batch size, and step count for sequential and replay methods |
| Buffer | Sweep a few capacities in number of examples. Report stored payload bytes and extra metadata separately. |
| Rehearsal | Replace a fixed share of each training minibatch with prior-buffer samples. Sample only released training rows. |
| Retrieval | Rebuild or update the index from released training rows. Record index size and update time. |
| Abstention | Choose the threshold rule and settings on validation, then hold them fixed for test scoring. |
| Offline reference | Retrain on all released training rows with a declared schedule. Report its time and data access separately. |

For uniform replay, keep a reservoir over observed training examples. For the fact-balanced variant, first try to preserve one example per eligible fact and distribute any remaining capacity across facts that still have examples. If there are more facts than slots, choose which to cover using a fixed seeded rule. Choose candidates only from memory and the incoming data. A fact whose examples have been dropped may be unavailable for later reselection. Log coverage so you can tell when that happens.

After verifying one order of releases, repeat with different topic orders and paired seeds. An improvement that appears only in one topic order deserves a narrower conclusion.

## 4. Measure acquisition, retention, and abstention

Use the [accuracy matrix and forgetting definition](../lessons/06-continual-learning.md) for old and new sessions. Report the number of questions behind each cell. With known questions $K$ and permanently unknown questions $U$:

$$
\mathrm{KnownAccuracy}=\frac{\mathrm{correct\ known\ answers}}{|K|},
\qquad
\mathrm{UnknownFalseAnswerRate}=\frac{\mathrm{answered\ unknowns}}{|U|}.
$$

$$
\mathrm{Coverage}=\frac{\mathrm{questions\ receiving\ an\ answer}}{|K|+|U|}.
$$

Use an undefined value when a metric's denominator is zero. Report accuracy among answered known questions alongside overall known accuracy. Count wrong labels and abstentions separately. In addition to average scores, show examples of failures involving close business terms, changed phrasing, numeral or punctuation variants, and out-of-scope questions. [Ribeiro et al. 2020](https://aclanthology.org/2020.acl-main.442/)

Record optimizer steps, approximate data draws, wall-clock update time, checkpoint size, and replay bytes. Replay budgets describe the stored training memory. Keep application metadata and evaluation data separate in the accounting. Report variation by seed and the absolute number of questions behind each percentage.

## 5. Save enough evidence to reproduce a run

- Dataset version or checksum, split inventory, and release order.
- Preprocessing choices and implementation revision.
- Model dimensions, optimizer settings, seed, and buffer settings.
- Per-question predicted and gold IDs with session, method, and decision score.
- Per-session table and a chart comparing old accuracy with new accuracy.
- A short error analysis with examples, reasons for uncertainty, and any reviewer corrections.

Fill in an empty comparison like this before adding measured results:

| Method | Old accuracy | New accuracy | Forgetting | Unknown false-answer rate | Update time | Replay memory |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sequential | — | — | — | — | — | — |
| Uniform replay | — | — | — | — | — | — |
| Fact-balanced replay | — | — | — | — | — | — |

## 6. Study corrections as a follow-up

Give a previously released fact a revised answer version. Score the new version, count stale predictions, and check nearby definitions that should stay the same. Use the latest applicable version by default and treat explicitly historical questions as a separate time-conditioned task. Define how replay handles superseded labels before training. [Kim et al. 2024](https://aclanthology.org/2024.naacl-long.302/)
