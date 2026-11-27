# Lesson 03. Search a glossary

**Goal.** Rank candidate facts with a simple score and decide when your system should abstain.

## 1. Walk through retrieval

1. Take the query and apply the same normalization and feature extraction used for stored questions.
2. Compare it with training questions from facts released so far.
3. Combine matches from the same fact, for example by keeping its strongest match.
4. Rank the distinct facts. Return the best answer only when the score and its lead over the runner-up are both large enough.

This is a useful first system for data analysts. It searches approved metric definitions and can display the source and version. Adding an entry changes the searchable index. A neural model’s trained parameters are studied separately.

## 2. Calculate Jaccard similarity

Jaccard similarity compares two sets of features. If both sets are empty, return 0 as a defined behavior for this project.

$$
J(Q,D)=\frac{\lvert Q\cap D\rvert}{\lvert Q\cup D\rvert}.
$$

| Candidate | Feature set | Query feature set | Shared / combined | Score |
| --- | --- | --- | --- | --- |
| A | `{abc, bcd, cde}` | `{abc, bcd}` | $2/3$ | $0.667$ |
| B | `{abc, xyz}` | `{abc, bcd}` | $1/3$ | $0.333$ |

Candidate A wins. Explain why recognizing one broad phrase can still lead to the wrong metric when two concepts have similar questions.

## 3. Calculate TF-IDF and cosine

Term frequency counts a feature within a training question. Inverse document frequency gives more weight to features found in fewer training questions. One smoothed form is

$$
w_{t,d}=\mathrm{tf}(t,d)\left[1+\log\left(\frac{1+N}{1+\mathrm{df}(t)}\right)\right],
$$

where $N$ is the number of training questions in the index and $\mathrm{df}(t)$ is the number containing term $t$. With $N=3$, a feature found in one question has IDF $1+\log(2)$, approximately $1.693$. A feature found in all three has IDF $1$.

Compute cosine from vectors using the same feature map and IDF values for the query and stored questions:

$$
\cos(\mathbf q,\mathbf d)=\frac{\mathbf q^\top\mathbf d}{\|\mathbf q\|_2\|\mathbf d\|_2}.
$$

If an input vector has length 0, define the score as 0 and abstain when the query has no usable features. For $\mathbf q=(1,1)$ and $\mathbf d=(2,0)$, the dot product is $2$, and cosine is $2/(2\sqrt{2})\approx 0.707$. [Manning, Raghavan, and Schütze, Chapter 6](https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf)

## 4. Compare ranking and rejection

If the best score is $s_1$ and the next-best fact scores $s_2$, test both conditions:

$$
s_1\ge \tau_{\mathrm{score}}\qquad\text{and}\qquad s_1-s_2\ge \tau_{\mathrm{gap}}.
$$

Use held-out validation questions to choose the thresholds. Include close distractors, permanently unknown topics, and common short questions. Keep the final test for scoring after you fix the settings. Report both how often known questions were answered correctly and how often unknown questions got an answer.

**Worked check.** Suppose the two top facts score $0.62$ and $0.59$. With a minimum score of $0.50$ and gap of $0.10$, the top score passes and the gap fails. The system should abstain.

## 5. Exit exercise

Pick three training questions and one new phrasing. Start with Jaccard, write the overlapping features, and record why the best result wins. Add a distractor with similar wording and calculate the two top scores again. Explain when the gap rule changes your decision.

Continue to [Lesson 04](04-model-math.md).
