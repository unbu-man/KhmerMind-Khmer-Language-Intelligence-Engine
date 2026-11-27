# Lesson 07. Why can Khmer text use more tokens?

**Goal.** Measure Khmer and English text with the same tokenizer and explain how its training data changes the result.

## 1. Separate words, characters, bytes, and tokens

A word is a unit of language. A Unicode code point is part of the text representation. A byte is a unit of storage. A token is whatever unit the tokenizer passes to a model.

Compare «ស្តុក» with `stock`.

| Representation | Khmer «ស្តុក» | English `stock` |
| --- | ---: | ---: |
| Unicode code points | 5 | 5 |
| UTF-8 bytes | 15 | 5 |
| Tokens under this audit's English-only BPE | 15 | 1 |
| Tokens under this audit's balanced BPE | 1 | 1 |

The Khmer code points are `U+179F U+17D2 U+178F U+17BB U+1780`. These code points include signs that combine in display. Each uses three UTF-8 bytes, which explains the $5\times3=15$ bytes. Khmer words also do not reliably correspond to whitespace-separated strings. We compare paired translations directly so this experiment can measure sequence length without guessing word boundaries. [Unicode Text Segmentation](https://www.unicode.org/reports/tr29/)

## 2. Derive one BPE merge

This byte-level version of byte-pair encoding (BPE) starts with byte symbols and adds frequent adjacent symbol pairs to the vocabulary. For training sequences $s$ and weights $w_s$, the count of two adjacent symbols $a$ and $b$ is

$$
C(a,b)=\sum_s w_s\sum_{j=1}^{|s|-1}\mathbf{1}[s_j=a,\ s_{j+1}=b].
$$

Suppose the training sequences are `abab` and `abcc` with weight 1 each. The pair `ab` occurs twice in `abab` and once in `abcc`, so $C(a,b)=3$. Merge `a` and `b` to a new symbol `AB`. Then `abab` becomes `[AB, AB]` and `abcc` becomes `[AB, c, c]`. Those sequences now have 2 and 3 tokens. Recount the pairs before learning the next merge. Our implementation breaks equal-count ties by token ID and applies the learned merges in rank order at encoding. [Sennrich et al. 2016](https://aclanthology.org/P16-1162/)

The English-only BPE can represent a Khmer input through its original bytes because it starts with all 256 byte values. It has no learned Khmer-script merges in this example. Giving Khmer text positive training weight changes which byte sequences win the limited merge slots. The terms in the table are held-out standalone inputs. Their component sequences can occur inside training sentences and contribute to merges.

## 3. Compute the ratio on matched text

For test pair $i$, let $T_{i,\mathrm{km}}$ and $T_{i,\mathrm{en}}$ be lengths produced by the **same** tokenizer. Use the ratio of totals:

$$
R=\frac{\sum_i T_{i,\mathrm{km}}}{\sum_i T_{i,\mathrm{en}}}.
$$

In our 16-pair audit, the English-only byte BPE gives $R=1809/381\approx4.75$. The balanced BPE gives $R=482/481\approx1.002$. Balancing the training mix also changes the English denominator. Report both lengths so you can see what happened in each language. Check individual pairs too. Seven pairs still have more Khmer tokens under the balanced setup. Published multilingual research uses paired texts to study length differences across languages and tokenizers. [Petrov et al., Language Model Tokenizers Introduce Unfairness Between Languages](https://arxiv.org/abs/2305.15425)

To measure tokens **per word** in the future, first obtain reviewed word boundaries. Define fertility as the total number of tokens divided by the total number of annotated words, and state how you handle punctuation and tokens that span a word boundary. That adds a word-segmentation task to the audit.

## 4. Connect sequence length to a learning model

In standard dense self-attention, $Q\in\mathbb{R}^{T\times d_k}$ and $K\in\mathbb{R}^{T\times d_k}$. The product $QK^\top$ has shape $T\times T$. For an idealized comparison with the same head count and no padding, compare the number of score cells across the paired dataset:

$$
R_{\mathrm{attention}}=\frac{\sum_i T_{i,\mathrm{km}}^2}{\sum_i T_{i,\mathrm{en}}^2}.
$$

For the first test pair under English-only BPE, the lengths are 142 and 22. The respective score matrices have $142^2=20{,}164$ and $22^2=484$ cells, about $41.7$ times as many for that one pair. Across all 16 pairs, the ratio is $22.35$. Under the balanced BPE, it is $1.01$. This equation counts score cells. Actual memory and time also depend on the implementation, batching, padding, and hardware. [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762)

The current KhmerMind linear and feedforward models use a fixed-length vector of hashed character n-gram features. The attention calculation applies to a future sequence model. To learn whether the tokenizer helps continual learning, compare answer accuracy and forgetting on the same releases while keeping the architecture, seeds, replay budget, and evaluation questions fixed. Fit each tokenizer with a declared training corpus available at the start and keep its vocabulary and IDs fixed throughout the comparison. This way you can interpret differences in retention without also changing the meaning of the model's input IDs during updates.

## 5. Check your understanding

1. For `sell` and «លក់», predict which has more code points and which has more UTF-8 bytes. Compare the report for `test_term_03`.
2. For the eighth test question under the English-heavy BPE, compute the one-pair token ratio $56/39$ and the score-cell ratio $(56/39)^2$. Check what each ratio means.
3. Run the audit with `--merges 64` and again with `--merges 128`. Explain the effect of increasing slots on both languages. Keep these as separate results.

[Audit results with every pair](../reports/tokenization.md) · [Training and test data](../data/tokenization_pairs.jsonl)
