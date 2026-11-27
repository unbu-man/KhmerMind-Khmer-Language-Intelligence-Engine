# Lesson 02. Represent Khmer text

**Goal.** Explain what the program receives when someone types Khmer, and build a plan for turning that text into comparable features.

## 1. Distinguish four units of text

| Unit | What it means | How we use it |
| --- | --- | --- |
| Byte | One unit of UTF-8 storage | Inspect encoding errors when reading files. |
| Unicode code point | An assigned value such as `U+1780` for «ក» | A simple Python n-gram baseline can slice at this level. |
| Grapheme cluster | A sequence that software treats as one user-perceived character boundary | Useful for a more readable character-level representation. |
| Word | A lexical unit selected by Khmer segmentation rules | Useful for word vocabularies and word embeddings. |

The displayed «កា» contains the code points «ក» and «ា». Writing `len("កា")` in Python measures code points. Spaces in Khmer do not reliably mark every word boundary, so splitting on spaces gives an incomplete word segmentation. The Unicode standard discusses language-specific word boundaries. [Unicode UAX #29](https://www.unicode.org/reports/tr29/)

## 2. Choose and test a normalization policy

Keep two fields, the original string for review and a normalized string for retrieval. Start by decoding UTF-8 and applying Unicode NFC. Then write explicit choices for question marks, extra spaces, the zero-width space `U+200B`, Khmer numerals, and English abbreviations. NFC addresses canonical equivalence. Decisions about punctuation and invisible separators belong to your application policy. [Unicode UAX #15](https://www.unicode.org/reports/tr15/)

Take «តើចំណូលសុទ្ធជាអ្វី?» and the same question copied with a zero-width space near «ចំណូលសុទ្ធ». Inspect their code points first. For a character-based retrieval baseline, you can compare the variants after a controlled removal of zero-width spaces. In a word segmentation experiment, an inserted boundary can be useful. Write down which behavior you chose and test for distinct questions that accidentally become identical.

## 3. Extract n-grams

An n-gram is a contiguous sequence of $n$ units. For a sequence $x_1,\dots,x_L$, each window starts at position $i$ and contains $x_i,\dots,x_{i+n-1}$. The number of windows before deduplication is

$$
\max(0,L-n+1).
$$

For the string `abcde`, code-point trigrams are `abc`, `bcd`, and `cde`. Compare «កា» and «ការ». At the code-point level the first has one bigram, «កា», and the second has two, «កា» and «ារ». The overlapping feature is useful to a search system. The second bigram illustrates why a feature can cross a boundary a reader would recognize.

Report whether you use a **set** of features (present or absent) or a **count** (how often they occur). Compare character widths 2, 3, and 4 on validation questions, with the same held-out cases for every width.

## 4. Explore word segmentation and subwords

- **Dictionary segmentation.** Starting at the left, choose the longest matching dictionary word and advance. Define a fallback that always moves forward when a word is missing. Test the algorithm against a small set you segmented by hand. Compare boundary precision and recall. Longest match can choose the wrong interpretation when several segmentations are possible.
- **Byte pair encoding (BPE).** Start from small symbols. Count adjacent pairs and merge the most frequent pair, recording the order of merges. Repeat up to a vocabulary budget. Encode new text using that learned order, with a deterministic tie rule. The names of individual symbols depend on how you define the start alphabet. Fit that vocabulary only on training text available at the chosen release. [Sennrich et al. 2016](https://aclanthology.org/P16-1162/)

## 5. Exit exercise

Write five short Khmer queries and one spelling or punctuation variant per query. Make a table of the raw string, processed string, first five trigrams, and any features lost. Circle two variants you expect a character baseline to match. Then choose a pair with similar spelling but different meaning and predict where the baseline could fail.

**Self-check.** A code-point trigram baseline is reproducible with a sliding window, and you can explain why its feature boundaries differ from word boundaries.

Continue to [Lesson 03](03-retrieval.md).
