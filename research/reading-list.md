# Annotated readings for KhmerMind

Read to answer a specific project question. After each source, write what the authors tested, what result their evidence supports, and which part still needs to be checked on Khmer glossary data.

## Khmer text and retrieval

| When | Source | What to look for |
| --- | --- | --- |
| Lesson 02 | Unicode Consortium. [UAX #15, Unicode Normalization Forms](https://www.unicode.org/reports/tr15/) | What canonical equivalence means and what NFC changes. |
| Lesson 02 | Unicode Consortium. [UAX #29, Unicode Text Segmentation](https://www.unicode.org/reports/tr29/) | The distinction between grapheme and word boundaries. Find the discussion of scripts such as Khmer. |
| Lesson 02 | [A review of Khmer word segmentation and part-of-speech tagging and an experimental study using bidirectional LSTM](https://doi.org/10.46223/HCMCOUJS.tech.en.12.1.2219.2022) (2022) | Read how the study frames Khmer word boundaries and defines its segmentation evaluation. Our first baseline treats segmentation as a separate design choice. |
| Lesson 02 | Sennrich, Haddow, and Birch (2016). [Neural Machine Translation of Rare Words with Subword Units](https://aclanthology.org/P16-1162/) | Trace the merge process. Their translation experiment motivates trying subwords while our QA results need their own evaluation. |
| Lesson 03 | Manning, Raghavan, and Schütze (2008). [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf), Chapter 6 | Derive why term frequency and document frequency contribute different information, then work through cosine scoring. |

## Neural foundations

| When | Source | What to look for |
| --- | --- | --- |
| Lesson 04 | Mikolov et al. (2013). [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) | Identify which token is the input and which token is the prediction target in Skip-gram. |
| Lesson 04 | Goodfellow, Bengio, and Courville (2016). [Deep Feedforward Networks](https://www.deeplearningbook.org/contents/mlp.html) | Follow the chain rule and compare the text's function-composition view to the matrix gradients in the lesson. |
| Lesson 05 | Hochreiter and Schmidhuber (1997). [Long Short-Term Memory](https://doi.org/10.1162/neco.1997.9.8.1735) | Understand the problem that motivated a gated memory. The lesson uses a commonly taught LSTM with a forget gate. |
| Lesson 05 | Cho et al. (2014). [Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation](https://aclanthology.org/D14-1179/) | Inspect the reset gate and the update gate. Check which term the paper multiplies by the update gate before copying a formula. |
| Lesson 05 | Vaswani et al. (2017). [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Start with scaled dot-product attention and trace the query, key, and value shapes. |

## Continual learning and evaluation

| When | Source | What to look for |
| --- | --- | --- |
| Lesson 06 | Lopez-Paz and Ranzato (2017). [Gradient Episodic Memory for Continual Learning](https://proceedings.neurips.cc/paper/2017/hash/f87522788a2be2d171666752f97ddebb-Abstract.html) | See how authors evaluate older tasks after newer ones. Compare their backward-transfer definition with our peak-to-current forgetting. |
| Lesson 06 | Chaudhry et al. (2019). [On Tiny Episodic Memories in Continual Learning](https://arxiv.org/abs/1902.10486) | See why replay with a small buffer is a baseline worth testing. Identify the data and architecture studied before applying its findings to question answering. |
| Extension | Kirkpatrick et al. (2017). [Overcoming Catastrophic Forgetting in Neural Networks](https://arxiv.org/abs/1612.00796) | Understand the intuition behind penalizing changes to important weights and compare that mechanism with replay. |
| Extension | Kim et al. (2024). [Carpe diem: On the Evaluation of World Knowledge in Lifelong Language Models](https://aclanthology.org/2024.naacl-long.302/) | Compare adding a new fact with updating or removing an old fact. Their benchmark motivates a later correction experiment. |
| Evaluation | Ribeiro et al. (2020). [Beyond Accuracy: Behavioral Testing of NLP Models with CheckList](https://aclanthology.org/2020.acl-main.442/) | Turn expected behavior into checks for stable meaning, meaning-changing edits, and tricky inputs. |

## How to log your reading

For each source, make one note with the citation, one equation or worked example you understood, one design decision it informed, and one limitation. Example: «Unicode UAX #29 → use code-point trigrams for the first baseline → learn that feature boundaries and word boundaries are distinct → verify which Khmer variants normalize to the same string.»
