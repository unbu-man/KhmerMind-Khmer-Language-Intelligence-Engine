"""Build the Markdown study report, chart, and machine-readable evidence archive."""
import argparse
import gzip
import json
from pathlib import Path
from statistics import mean, stdev

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABELS = {
    "retrieval": "Retrieval",
    "frozen": "Frozen",
    "sequential": "Sequential",
    "uniform_replay": "Uniform replay",
    "fact_balanced_replay": "Fact-balanced replay",
    "full_history": "Full history",
}
METHODS = ("sequential", "uniform_replay", "fact_balanced_replay")


def group_runs(case: dict) -> dict:
    groups = {}
    for run in case["runs"]:
        groups.setdefault(run["method"], []).append(run["sessions"])
    return groups


def percent(values, suffix: str = "%") -> str:
    return f"{mean(values) * 100:.1f}{suffix}"


def final_rows(case: dict) -> list[str]:
    rows = []
    for method, runs in group_runs(case).items():
        final = [run[-1] for run in runs]
        metrics = [row["metrics"] for row in final]
        old = [row["top_old_accuracy"] for row in metrics]
        old_spread = f" ± {stdev(old) * 100:.1f}" if len(old) > 1 else ""
        values = [
            percent(old) + old_spread,
            percent([row["top_new_accuracy"] for row in metrics]),
            percent([row["top_forgetting"] for row in metrics], " pp"),
            percent([row["known_accuracy"] for row in metrics]),
            percent([row["unknown_false_answer_rate"] for row in metrics]),
            percent([row["coverage"] for row in metrics]),
            f'{mean(row["update_seconds"] for row in final) * 1000:.1f}',
            str(round(mean(row.get("buffer_payload_bytes", 0) for row in final))),
        ]
        rows.append("| " + " | ".join([LABELS[method], *values]) + " |")
    return rows


def markdown(cases: list[dict]) -> str:
    lines = [
        "# Held-out benchmark results", "",
        "The synthetic test split contains 42 answerable questions, 14 per release, and "
        "8 out-of-scope questions. Each neural result averages three seeds. "
        "Retrieval is deterministic and runs once per ordering.", "",
        "Top-candidate scores use the most likely fact before rejection. "
        "The last three accuracy and coverage columns use the actual answer after rejection. "
        "A refused known question counts as incorrect. Old top accuracy is reported with "
        "sample standard deviation in percentage points across seeds. Final-update time is "
        "measured in milliseconds and excludes evaluation and shared feature extraction. "
        "Replay bytes count serialized example payloads.", "",
    ]
    for case in cases:
        order = " → ".join(map(str, case["release_order"]))
        lines += [
            f'## {case["model"].upper()} · {order}', "",
            "| Method | Old top accuracy | New top accuracy | Top forgetting | "
            "Known accuracy | Unknown false answers | Coverage | Update ms | Replay bytes |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            *final_rows(case), "",
        ]
    first = cases[0]
    lines += ["## Evidence", "",
              "- [Experimental settings and interpretation](README.md)",
              "- [Per-question predictions, metrics, configuration and checksums (JSON.gz)](benchmark-runs.json.gz)",
              "- [Release-by-release accuracy chart](accuracy.png)",
              f'- Runtime for these files was Python {first["python"]} and NumPy {first["numpy"]}.', ""]
    return "\n".join(lines)


def save_chart(cases: list[dict], output: Path) -> None:
    standard = next(case for case in cases
                    if case["model"] == "linear" and case["release_order"] == [1, 2, 3])
    groups = group_runs(standard)
    fig, axes = plt.subplots(1, 2, figsize=(9.7, 4), sharey=True)
    colors = ("#a84d37", "#16685b", "#435a9a")
    for axis, key, title in zip(
        axes, ("top_old_accuracy", "top_new_accuracy"),
        ("Previously released questions", "Newly released questions"), strict=True,
    ):
        for method, color in zip(METHODS, colors, strict=True):
            runs = groups[method]
            x, y = [], []
            for index, session in enumerate(runs[0], 1):
                scores = [run[index - 1]["metrics"][key] for run in runs]
                if scores[0] is not None:
                    x.append(session["session"])
                    y.append(mean(scores) * 100)
            axis.plot(x, y, "o-", color=color, label=LABELS[method], linewidth=2)
        axis.set(title=title, xlabel="Release after update", xticks=[1, 2, 3], ylim=(-4, 102))
        axis.grid(axis="y", color="#e1e8e6")
        axis.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Top-candidate accuracy (%)")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
    fig.suptitle("KhmerMind · linear classifier across three releases", fontweight="bold")
    fig.tight_layout(rect=(0, 0.10, 1, 0.92))
    fig.savefig(output, dpi=155)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=Path("reports"))
    args = parser.parse_args()
    cases = [json.loads(path.read_text(encoding="utf-8")) for path in args.results]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.md").write_text(markdown(cases), encoding="utf-8")
    save_chart(cases, args.output / "accuracy.png")
    evidence = json.dumps(cases, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    (args.output / "benchmark-runs.json.gz").write_bytes(gzip.compress(evidence, mtime=0))


if __name__ == "__main__":
    main()
