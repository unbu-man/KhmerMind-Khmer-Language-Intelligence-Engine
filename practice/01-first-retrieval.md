# Practice 01. Find a glossary answer with different wording

**Before you start.** Finish [Lesson 00](../lessons/00-first-khmer-question.md), [Lesson 02](../lessons/02-khmer-text.md), and [Lesson 03](../lessons/03-retrieval.md). Keep the original `lesson00.py` in your practice folder for this run.

## 1. See why the lookup needs a better match

The original glossary has «តើចំណូលសុទ្ធមានន័យដូចម្តេច». Try asking «តើអ្វីទៅជាចំណូលសុទ្ធ?». The whole strings differ, but parts of them overlap. We will score those shared parts.

For a short hand check, compare `abcde` and `xbcde`. Their character trigram sets are `{abc, bcd, cde}` and `{xbc, bcd, cde}`. Two features are shared and four occur in either string. Their Jaccard score is

$$
J = \frac{2}{4}=0.5.
$$

In Khmer, use Unicode code points as the units in this practice. The program can extract overlapping snippets without first identifying words. Later you can test whether changing the units improves your results.

## 2. Implement the minimum you need

Create `practice01.py` in the same folder as `lesson00.py`. The code follows four steps. It creates feature sets, filters the glossary to the selected release, ranks candidates, then decides whether to answer.

```python
import unicodedata

from lesson00 import GLOSSARY, clean_question, fact_id, lookup


def character_ngrams(text, size=3):
    text = unicodedata.normalize("NFC", clean_question(text)).casefold()
    return {text[start:start + size] for start in range(len(text) - size + 1)}


def jaccard(left, right):
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def search(question, release):
    query = character_ngrams(question)
    scores = []
    for stored_question, record in GLOSSARY.items():
        if record["release"] <= release:
            score = jaccard(query, character_ngrams(stored_question))
            scores.append((score, record))
    scores.sort(key=lambda entry: (-entry[0], entry[1]["fact_id"]))

    if not scores:
        return None, 0.0

    best_score, best_record = scores[0]
    second_score = scores[1][0] if len(scores) > 1 else 0.0
    if best_score < 0.20 or best_score - second_score < 0.04:
        return None, best_score
    return best_record, best_score


if __name__ == "__main__":
    checks = (
        ("តើអ្វីទៅជាចំណូលសុទ្ធ?", 1, "net_revenue"),
        ("តើអ្វីទៅជាស្តុកបម្រុង?", 1, "UNKNOWN"),
        ("តើអ្វីទៅជាស្តុកបម្រុង?", 2, "safety_stock"),
        ("តើកិច្ចប្រជុំនៅបន្ទប់ណា?", 2, "UNKNOWN"),
    )
    assert jaccard(character_ngrams("abcde"), character_ngrams("xbcde")) == 0.5
    for question, release, expected in checks:
        match, score = search(question, release)
        predicted = fact_id(match)
        exact = fact_id(lookup(question, release))
        print(f"Release {release} | {question} | exact={exact} | search={predicted} ({score:.2f})")
        assert predicted == expected, (question, predicted, expected)
    print(f"{len(checks)} retrieval checks passed.")
```

Run `python3 practice01.py` in the same folder. The four checks cover a new wording about an old fact, a future fact, a fact after it arrives, and a permanent unknown. The number printed with the answer measures text overlap even when the system abstains. It is a similarity score, so `0.50` means a Jaccard similarity of one-half, with no calibrated probability interpretation.

The two thresholds are fixed teaching settings for this tiny glossary. In a study, choose thresholds using a separate validation split and record them before final test scoring. If you store multiple questions for each fact, rank distinct facts by each fact’s highest score before applying the runner-up rule.

On the original sample, the net-revenue paraphrase scored 0.24 and the safety-stock paraphrase scored 0.44 after release 2. The script ended with `4 retrieval checks passed.`

## 3. Inspect one miss

Write a paraphrase without the phrase «ចំណូលសុទ្ធ». Inspect the trigrams it shares with the stored question. Try the following and record what changed:

1. Try two-character grams instead of three-character grams. Identify which unrelated overlaps increase.
2. Write a question about gross revenue that shares many words with net revenue. Compare the two scores.
3. Change the score or gap rule on a validation example and record both a useful answer and a false answer that might appear.

## 4. Move your lookup toward the project

Move the four answers into a fact table and give each a release and source. Move question wordings into a separate table with wording families and splits. Build the index from released training questions only. Keep test question phrasing out of the glossary index. Then implement the TF-IDF scoring from [Lesson 03](../lessons/03-retrieval.md) and apply both methods to the same held-out questions.

You have completed this practice when you can calculate one score, explain one abstention, and point to what data the system could see at each release. Move on to [Lesson 04 · Model math](../lessons/04-model-math.md).
