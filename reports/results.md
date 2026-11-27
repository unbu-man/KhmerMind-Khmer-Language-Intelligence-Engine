# Held-out benchmark results

The synthetic test split contains 42 answerable questions, 14 per release, and 8 out-of-scope questions. Each neural result averages three seeds. Retrieval is deterministic and runs once per ordering.

Top-candidate scores use the most likely fact before rejection. The last three accuracy and coverage columns use the actual answer after rejection. A refused known question counts as incorrect. Old top accuracy is reported with sample standard deviation in percentage points across seeds. Final-update time is measured in milliseconds and excludes evaluation and shared feature extraction. Replay bytes count serialized example payloads.

## LINEAR · 1 → 2 → 3

| Method | Old top accuracy | New top accuracy | Top forgetting | Known accuracy | Unknown false answers | Coverage | Update ms | Replay bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 32.1% | 42.9% | 7.1 pp | 19.0% | 25.0% | 22.0% | 6.7 | 0 |
| Frozen | 17.9% ± 3.6 | 0.0% | 0.0 pp | 1.6% | 16.7% | 12.7% | 0.0 | 0 |
| Sequential | 0.0% ± 0.0 | 50.0% | 35.7 pp | 4.8% | 16.7% | 6.7% | 31.5 | 0 |
| Uniform replay | 10.7% ± 3.6 | 38.1% | 20.2 pp | 0.0% | 0.0% | 0.7% | 27.8 | 5659 |
| Fact-balanced replay | 7.1% ± 6.2 | 47.6% | 26.2 pp | 0.0% | 0.0% | 0.0% | 27.7 | 5391 |
| Full history | 29.8% ± 4.1 | 31.0% | 10.7 pp | 0.0% | 0.0% | 0.0% | 82.2 | 0 |

## FFN · 1 → 2 → 3

| Method | Old top accuracy | New top accuracy | Top forgetting | Known accuracy | Unknown false answers | Coverage | Update ms | Replay bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 32.1% | 42.9% | 7.1 pp | 19.0% | 25.0% | 22.0% | 6.9 | 0 |
| Frozen | 16.7% ± 5.5 | 0.0% | 0.0 pp | 11.1% | 91.7% | 90.7% | 0.0 | 0 |
| Sequential | 0.0% ± 0.0 | 47.6% | 36.9 pp | 15.1% | 100.0% | 97.3% | 29.8 | 0 |
| Uniform replay | 3.6% ± 3.6 | 38.1% | 28.6 pp | 14.3% | 87.5% | 76.7% | 34.2 | 5659 |
| Fact-balanced replay | 0.0% ± 0.0 | 38.1% | 32.1 pp | 11.1% | 83.3% | 77.3% | 38.1 | 5391 |
| Full history | 31.0% ± 4.1 | 38.1% | 4.8 pp | 27.0% | 79.2% | 67.3% | 89.9 | 0 |

## LINEAR · 3 → 1 → 2

| Method | Old top accuracy | New top accuracy | Top forgetting | Known accuracy | Unknown false answers | Coverage | Update ms | Replay bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 39.3% | 28.6% | 10.7 pp | 19.0% | 25.0% | 22.0% | 6.2 | 0 |
| Frozen | 22.6% ± 2.1 | 0.0% | 0.0 pp | 4.0% | 8.3% | 7.3% | 0.0 | 0 |
| Sequential | 0.0% ± 0.0 | 42.9% | 42.9 pp | 10.3% | 0.0% | 15.3% | 23.5 | 0 |
| Uniform replay | 20.2% ± 4.1 | 40.5% | 11.9 pp | 1.6% | 0.0% | 1.3% | 27.8 | 5589 |
| Fact-balanced replay | 9.5% ± 2.1 | 42.9% | 22.6 pp | 0.8% | 0.0% | 0.7% | 26.9 | 5433 |
| Full history | 29.8% ± 5.5 | 35.7% | 8.3 pp | 0.0% | 0.0% | 0.0% | 72.2 | 0 |

## FFN · 3 → 1 → 2

| Method | Old top accuracy | New top accuracy | Top forgetting | Known accuracy | Unknown false answers | Coverage | Update ms | Replay bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval | 39.3% | 28.6% | 10.7 pp | 19.0% | 25.0% | 22.0% | 6.4 | 0 |
| Frozen | 28.6% ± 3.6 | 0.0% | 0.0 pp | 18.3% | 87.5% | 86.7% | 0.0 | 0 |
| Sequential | 0.0% ± 0.0 | 40.5% | 47.6 pp | 13.5% | 100.0% | 98.7% | 29.1 | 0 |
| Uniform replay | 8.3% ± 5.5 | 35.7% | 28.6 pp | 16.7% | 79.2% | 76.0% | 44.3 | 5589 |
| Fact-balanced replay | 8.3% ± 2.1 | 38.1% | 29.8 pp | 15.9% | 62.5% | 74.7% | 33.1 | 5433 |
| Full history | 29.8% ± 4.1 | 42.9% | 14.3 pp | 27.0% | 75.0% | 66.0% | 88.1 | 0 |

## Evidence

- [Experimental settings and interpretation](README.md)
- [Per-question predictions, metrics, configuration and checksums (JSON.gz)](benchmark-runs.json.gz)
- [Release-by-release accuracy chart](accuracy.png)
- Runtime for these files was Python 3.12.14 and NumPy 2.3.5.
