# Khmer–English tokenization audit

Each count uses the same synthetic paired material. BPE rules fit on 24 training pairs. This report measures 16 held-out pairs (4 business terms).

Starting vocabulary: 256 bytes per BPE tokenizer. Target merge budget: 128. English-to-Khmer training weights were 4:0, 3:1, and 2:2 per pair. All configurations used the same total example weight and tokenizer algorithm. The number of raw training bytes differs by mix.

Counts include internal spaces and punctuation. All text is normalized to NFC and edge whitespace is trimmed. The code-point row measures a simple character baseline.

| Unit or tokenizer | Khmer total | English total | Khmer / English | Pairs with Khmer longer | Dense attention score cells ratio | Merges learned |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| UTF-8 bytes | 1809 | 731 | 2.47× | 16/16 | 6.04× | — |
| Unicode code points | 611 | 731 | 0.84× | 2/16 | 0.69× | — |
| English-only byte BPE | 1809 | 381 | 4.75× | 16/16 | 22.35× | 128 |
| English-heavy byte BPE | 607 | 428 | 1.42× | 14/16 | 1.99× | 128 |
| Balanced byte BPE | 482 | 481 | 1.00× | 7/16 | 1.01× | 128 |

The attention column compares the sum of squared sequence lengths for each unit across paired inputs. It represents the size of dense score matrices if those units were used as model tokens. It omits padding and special tokens.

## Per-pair counts

Each cell lists Khmer / English. See the [parallel data](../data/tokenization_pairs.jsonl) for the full paired text.

| Pair | UTF-8 bytes | Unicode code points | English-only byte BPE | English-heavy byte BPE | Balanced byte BPE |
| --- | ---: | ---: | ---: | ---: | ---: |
| test_text_01 | 142 / 52 | 48 / 52 | 142 / 22 | 49 / 27 | 39 / 35 |
| test_text_02 | 145 / 65 | 49 / 65 | 145 / 31 | 47 / 38 | 38 / 42 |
| test_text_03 | 139 / 44 | 47 / 44 | 139 / 26 | 46 / 26 | 38 / 30 |
| test_text_04 | 154 / 67 | 52 / 67 | 154 / 38 | 56 / 40 | 47 / 44 |
| test_text_05 | 115 / 49 | 39 / 49 | 115 / 31 | 37 / 34 | 25 / 34 |
| test_text_06 | 163 / 65 | 55 / 65 | 163 / 37 | 52 / 40 | 46 / 44 |
| test_text_07 | 127 / 63 | 43 / 63 | 127 / 33 | 44 / 37 | 33 / 41 |
| test_text_08 | 172 / 75 | 58 / 75 | 172 / 33 | 56 / 39 | 43 / 48 |
| test_text_09 | 145 / 54 | 49 / 54 | 145 / 25 | 47 / 30 | 38 / 34 |
| test_text_10 | 148 / 71 | 50 / 71 | 148 / 37 | 52 / 41 | 47 / 44 |
| test_text_11 | 151 / 44 | 51 / 44 | 151 / 27 | 47 / 29 | 36 / 30 |
| test_text_12 | 151 / 57 | 51 / 57 | 151 / 27 | 54 / 33 | 38 / 39 |
| test_term_01 | 15 / 5 | 5 / 5 | 15 / 1 | 5 / 1 | 1 / 1 |
| test_term_02 | 15 / 7 | 5 / 7 | 15 / 2 | 5 / 2 | 4 / 4 |
| test_term_03 | 9 / 4 | 3 / 4 | 9 / 4 | 3 / 4 | 2 / 4 |
| test_term_04 | 18 / 9 | 6 / 9 | 18 / 7 | 7 / 7 | 7 / 7 |

## Reproduce

```bash
python3 -m khmer_learning.tokenization_audit --output reports/tokenization.md
```

Input SHA-256: `e41ee32ff319f6d56d3ee5c2fc4d1c1e6f14cffbbaa602af6e8ea478d4f7a5b1`.

These results describe this corpus and these small custom tokenizers. The experiment does not measure Khmer language model accuracy, commercial tokenizers, or runtime.
