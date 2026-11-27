"""Measure paired Khmer and English lengths under controlled byte-BPE tokenizers."""
import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .tokenization import BytePairEncoder, normalize_token_text

DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "tokenization_pairs.jsonl"
MIXES = (
    ("English-only byte BPE", 4, 0),
    ("English-heavy byte BPE", 3, 1),
    ("Balanced byte BPE", 2, 2),
)


@dataclass(frozen=True)
class ParallelPair:
    id: str
    split: str
    kind: str
    km: str
    en: str


def load_pairs(path: Path) -> list[ParallelPair]:
    pairs = []
    seen_ids = set()
    seen_text = {"km": set(), "en": set()}
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                pair = ParallelPair(**json.loads(line))
                if not isinstance(pair.id, str) or not pair.id.strip() or pair.split not in {"train", "test"}:
                    raise ValueError("Expected an ID and a train or test split.")
                if pair.kind not in {"term", "text"}:
                    raise ValueError("Expected a term or text row.")
                if pair.id in seen_ids:
                    raise ValueError("Repeated pair ID.")
                for language in ("km", "en"):
                    original = getattr(pair, language)
                    if not isinstance(original, str):
                        raise ValueError(f"Expected {language} text.")
                    text = normalize_token_text(original)
                    if not text or text in seen_text[language]:
                        raise ValueError(f"Empty or repeated {language} text.")
                    seen_text[language].add(text)
            except (TypeError, ValueError, AttributeError) as error:
                raise ValueError(f"{path}:{number}: {error}") from error
            seen_ids.add(pair.id)
            pairs.append(pair)
    if {pair.split for pair in pairs} != {"train", "test"}:
        raise ValueError("Include at least one training pair and one held-out pair.")
    return pairs


def train_tokenizers(training: list[ParallelPair], merge_limit: int) -> dict[str, BytePairEncoder]:
    tokenizers = {}
    for name, english_weight, khmer_weight in MIXES:
        batch = Counter()
        for pair in training:
            batch[pair.en] += english_weight
            batch[pair.km] += khmer_weight
        tokenizers[name] = BytePairEncoder.train(batch, merge_limit)
    return tokenizers


def _khmer_english_counts(text_pair: ParallelPair, tokenizers: dict) -> dict[str, tuple[int, int]]:
    texts = tuple(normalize_token_text(text) for text in (text_pair.km, text_pair.en))
    return {
        "UTF-8 bytes": tuple(len(text.encode("utf-8")) for text in texts),
        "Unicode code points": tuple(map(len, texts)),
        **{name: tuple(len(encoder.encode(text)) for text in texts)
           for name, encoder in tokenizers.items()},
    }


def make_report(source: Path, merge_limit: int) -> str:
    pairs = load_pairs(source)
    training = [pair for pair in pairs if pair.split == "train"]
    test = [pair for pair in pairs if pair.split == "test"]
    tokenizers = train_tokenizers(training, merge_limit)
    counts = [(pair, _khmer_english_counts(pair, tokenizers)) for pair in test]

    report = [
        "# Khmer–English tokenization audit", "",
        f"Each count uses the same synthetic paired material. BPE rules fit on {len(training)} "
        f"training pairs. This report measures {len(test)} held-out pairs "
        f"({sum(pair.kind == 'term' for pair in test)} business terms).", "",
        f"Starting vocabulary: 256 bytes per BPE tokenizer. Target merge budget: {merge_limit}. "
        "English-to-Khmer training weights were 4:0, 3:1, and 2:2 per pair. "
        "All configurations used the same total example weight and tokenizer algorithm. "
        "The number of raw training bytes differs by mix.", "",
        "Counts include internal spaces and punctuation. All text is normalized to NFC and "
        "edge whitespace is trimmed. The code-point row measures a simple character baseline.", "",
        "| Unit or tokenizer | Khmer total | English total | Khmer / English | "
        "Pairs with Khmer longer | Dense attention score cells ratio | Merges learned |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in counts[0][1]:
        lengths = [row[name] for _, row in counts]
        km_total = sum(km for km, _ in lengths)
        en_total = sum(en for _, en in lengths)
        more = sum(km > en for km, en in lengths)
        square_ratio = sum(km * km for km, _ in lengths) / sum(en * en for _, en in lengths)
        merges = str(len(tokenizers[name].merges)) if name in tokenizers else "—"
        report.append(f"| {name} | {km_total} | {en_total} | {km_total / en_total:.2f}× | "
                      f"{more}/{len(lengths)} | {square_ratio:.2f}× | {merges} |")

    report.extend([
        "", "The attention column compares the sum of squared sequence lengths for each unit "
        "across paired inputs. It represents the size of dense score matrices if those units "
        "were used as model tokens. It omits padding and special tokens.", "",
        "## Per-pair counts", "",
        "Each cell lists Khmer / English. See the "
        "[parallel data](../data/tokenization_pairs.jsonl) for the full paired text.", "",
        "| Pair | " + " | ".join(counts[0][1]) + " |",
        "| --- |" + " ---: |" * len(counts[0][1]),
    ])
    for pair, row in counts:
        report.append(f"| {pair.id} | " + " | ".join(f"{km} / {en}" for km, en in row.values()) + " |")
    report.extend([
        "", "## Reproduce", "",
        "```bash",
        "python3 -m khmer_learning.tokenization_audit --output reports/tokenization.md",
        "```", "",
        f"Input SHA-256: `{hashlib.sha256(source.read_bytes()).hexdigest()}`.", "",
        "These results describe this corpus and these small custom tokenizers. The experiment "
        "does not measure Khmer language model accuracy, commercial tokenizers, or runtime.", "",
    ])
    return "\n".join(report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--merges", type=int, default=128)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = make_report(args.data, args.merges)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
        else:
            print(report, end="")
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
