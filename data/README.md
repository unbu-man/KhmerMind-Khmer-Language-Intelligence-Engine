# KhmerMind glossary data

The dataset contains 30 synthetic business glossary facts and 190 Khmer or mixed Khmer–English questions. It was written for this project. The values and definitions reflect a fictional company. Fluent Khmer review and external validation are pending.

| Release | Domain | Facts |
| --- | --- | ---: |
| 1 | Sales and revenue | 10 |
| 2 | Customers and promotion | 10 |
| 3 | Inventory and fulfillment | 10 |

Each fact has three training questions. Validation and test each have 42 questions linked to a known fact and eight permanently out-of-scope questions. Out-of-scope queries include requests for actual company numbers and questions about concepts absent from the glossary. Validation was used to select the initial thresholds and training settings.

## Files

- `facts.jsonl` stores `fact_id`, `version_id`, `session`, `topic`, `answer` in Khmer, and `source_id`. The additions benchmark uses one version per fact.
- `questions.jsonl` stores `question_id`, `fact_id`, `paraphrase_group`, `text`, and `split`. A null `fact_id` marks an out-of-scope question. These rows appear only in validation and test.

Review whether different questions belong to the same wording family before adding them. The validator catches duplicate normalized text, reused group IDs across splits, missing required splits, and invalid release or fact IDs. It cannot independently judge semantic near-duplicates, phrasing quality, or agreement with a real organization’s definitions. Preserve the original Unicode and record the source if replacing any synthetic rows.

## Khmer–English tokenization audit

[`tokenization_pairs.jsonl`](tokenization_pairs.jsonl) is a separate synthetic dataset, with 24 training pairs and 16 held-out pairs. The four term-level pairs are marked as `kind: term`. Each record stores a Khmer phrase and its English translation. The audit fits merge rules using only the training split. These translations have yet to receive independent Khmer review. See the [tokenization results](../reports/tokenization.md) for counts and reproduction commands.
