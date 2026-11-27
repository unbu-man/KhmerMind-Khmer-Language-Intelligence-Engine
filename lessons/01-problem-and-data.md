# Lesson 01. Define the problem and design the data

**Goal.** By the end, you can describe exactly what goes into KhmerMind, what comes out, and what counts as a correct answer. Allow 30–45 minutes for the lesson and exercise.

## 1. Follow one question

A team member reads a sales report and asks «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» The system maps the question to the stable ID `net_revenue`. It displays the definition active for that reporting release. The first experiment is a **classification** or **retrieval** task with a reference answer. The system makes no numeric sales calculation unless you later build a separate calculator backed by data.

| Piece | Example |
| --- | --- |
| Input | «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» |
| Fact ID | `net_revenue` |
| Answer version | `net_revenue_v1` |
| Answer | «ចំណូលសុទ្ធគឺចំណូលសរុបក្រោយដកការបញ្ចុះតម្លៃ និងតម្លៃទំនិញដែលអតិថិជនបង្វិលមកវិញ។» |
| Release | `1` |
| Source | `fictional_glossary_v1` |

A fact is the concept, an answer version is its definition at a particular time, and a question is one way a user asks about it. Many questions can map to the same fact. A later release can add a different fact. In a follow-up experiment, a release can also revise the definition of an existing fact.

## 2. Make releases concrete

| Release | Newly available facts | What to check |
| --- | --- | --- |
| 1 | Gross revenue and net revenue | Separate two similar concepts and decline unrelated questions. |
| 2 | Repeat customer and safety stock | Answer new questions about these facts and retain earlier answers. |
| 3 | Fulfillment and other inventory metrics | Test whether retention holds after another update. |

A query about safety stock before release 2 is **not yet supported**. An unrelated query about the location of a meeting stays out of scope. Track these two cases separately because their expected outcomes differ after the release.

## 3. Write two tables

**Facts.** Record `fact_id`, `version_id`, `answer_km`, `available_from_session`, and `source_id`. Specify units, reporting period, and denominator for rates or averages. Preserve the original definition when a later release revises it.

**Questions.** Record `question_id`, `question_km`, `fact_id` or an empty value for out-of-scope, `paraphrase_group`, and `split`. Keep the original Khmer string. For a production glossary, verify that you can publish the source text and that the wording agrees with domain experts.

## 4. Decide who sees which examples

| Split | Purpose | Example for `net_revenue` |
| --- | --- | --- |
| Train | Fit weights or build the search index after release | «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» |
| Validation | Compare methods and pick thresholds | «តើត្រូវដកអ្វីខ្លះចេញពីចំណូលសរុបដើម្បីបានចំណូលសុទ្ធ?» |
| Test | Score the finished protocol once choices are fixed | «ក្រោយដកការបញ្ចុះតម្លៃ និងការសងប្រាក់ តើគួររាយការណ៍ចំណូលប្រភេទណា?» |

Put superficial variations from the same wording family in the same split. For instance, a question and its copy with a different question mark are one family. Keep at least one independently phrased held-out question per fact. A known fact can appear in several splits through different wording. The model is expected to know its definition after release. Its held-out questions evaluate whether it recognizes other ways to ask.

**Worked check.** A colleague adds «តើចំណូលសុទ្ធមានន័យដូចម្តេច» to the test set. The same text with a question mark is in training. Treat them as a single wording family. An easy duplicate could make accuracy look better without showing the system handles a new phrasing.

## 5. Exit exercise

- Define four facts with stable IDs and assign each to one of two releases.
- Write two question phrasings per fact and mark the wording families. Add a third distinct family per fact when you create the validation split.
- Write one permanently out-of-scope question and one question about a fact before it arrives.
- Explain what the two questions should return after release 2.

**Self-check.** You can name the exact field your evaluation scores, state why the held-out questions remain hidden during development, and explain the difference between a permanent unknown and a future fact.

Continue to [Lesson 02](02-khmer-text.md).
