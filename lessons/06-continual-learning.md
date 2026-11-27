# Lesson 06. Learn new facts while keeping older ones

**Goal.** Measure whether sequential model updates acquire new facts and retain old ones.

## 1. Define the learning setting

A **session** is a release of training examples about newly available facts. Train on the first session and save the model. Train on the second session and score held-out questions about both releases. A decline on the earlier questions is evidence of forgetting under this evaluation. The magnitude can depend on the update method, the data, and which answer classes the model can currently choose. [Lopez-Paz and Ranzato 2017](https://proceedings.neurips.cc/paper/2017/hash/f87522788a2be2d171666752f97ddebb-Abstract.html)

An expanding search index is a practical product comparison. It adds retrievable source records. The neural experiment measures whether training changes which answer an input maps to, with the reference answer text displayed after prediction.

## 2. Compare practical update rules

| Method | What is available at an update |
| --- | --- |
| Frozen model | The original weights and original answer classes |
| Sequential only | Previous weights and the current training batch |
| Uniform replay | Previous weights, the current batch, and a capped sample of older training examples |
| Fact-balanced replay | The same resources as uniform replay, with a policy that tries to cover more fact IDs |
| Full-history reference | All released training examples, with compute reported separately |
| Retrieval | A search index built from released training questions and approved fact records |

In replay, replace part of each minibatch with samples from the old buffer. Under a matched-step comparison, with batch size $B$ and replay fraction $\rho$ chosen so $\rho B$ is an integer, reserve $\rho B$ positions for old examples and $(1-\rho)B$ for new examples. When the buffer is empty, fill the batch with new examples. Record the same batch size and number of gradient steps for sequential and replay methods. [Chaudhry et al. 2019](https://arxiv.org/abs/1902.10486)

**Uniform memory rule.** Keep the first $M$ examples in a reservoir. At example $k>M$, sample an integer uniformly from $1$ to $k$. If it is at most $M$, replace that slot. The new example then has probability $M/k$ of being kept. Each older example had probability $M/(k-1)$ of already being present and, conditional on being present, survives this update with probability $1-1/k$. Their product is $M/k$.

## 3. Read the accuracy matrix

Let $A_{t,j}$ be the fraction of held-out questions from release $j$ answered correctly after training through release $t$. This matrix counts abstaining on a known question as incorrect. The example values are hypothetical.

| Trained through | Release 1 questions | Release 2 questions | Release 3 questions |
| --- | ---: | ---: | ---: |
| Release 1 | 0.90 | — | — |
| Release 2 | 0.75 | 0.85 | — |
| Release 3 | 0.70 | 0.80 | 0.88 |

At release 3, new-session accuracy is $0.88$. The mean accuracy across the old sessions is $(0.70+0.80)/2=0.75$. Average across individual questions instead if you want a micro average, and report the weights if session sizes differ.

Define average forgetting for $t>1$ as the mean drop from each earlier session’s best **prior** score:

$$
F_t=\frac{1}{t-1}\sum_{j=1}^{t-1}\left(
   \max_{j\le k<t} A_{k,j}-A_{t,j}\right).
$$

At release 3 the example gives $[(0.90-0.70)+(0.85-0.80)]/2=0.125$, or 12.5 percentage points. A negative contribution can occur when an old session improves beyond its best previous score. This peak-to-current measure differs from backward transfer, which compares the current score with the score immediately after first training on that session. Report which definition you use.

## 4. Compare methods fairly

Give all methods the same releases and held-out wording. Check new accuracy and old accuracy together. Track unknown false answers, the fraction of all questions the model answers, and how much data and compute each update uses. Pair methods on the same seeds. Keep training, validation, and test families separate. Use the full protocol when planning the first measured run.

## 5. Exit exercise

1. Calculate forgetting at release 2 from the table above.
2. Suppose replay changes the release 3 row to $[0.85,0.82,0.75]$. Compare forgetting and new accuracy to the original row. Explain the tradeoff.
3. Choose a memory of four examples and give a concrete reason to compare uniform and fact-balanced replay under that budget.

**Self-check for exercise 2.** Forgetting falls to $[(0.90-0.85)+(0.85-0.82)]/2=0.04$. New accuracy also falls from $0.88$ to $0.75$. You need to report both changes.

Continue to the [research protocol](../research/protocol.md).
