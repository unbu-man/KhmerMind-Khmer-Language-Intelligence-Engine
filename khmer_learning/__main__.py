"""Command-line entry point for data validation, retrieval, and experiments."""
import argparse
import json
from pathlib import Path

from .config import Config
from .data import load_dataset
from .glossary import Glossary

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = (
    ("តើចំណូលសុទ្ធមានន័យដូចម្តេច?", 1),
    ("តើស្តុកបម្រុងជាអ្វី?", 1),
    ("តើស្តុកបម្រុងជាអ្វី?", 3),
    ("តើថ្ងៃនេះសីតុណ្ហភាពប៉ុន្មាន?", 3),
)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KhmerMind glossary and continual-learning study")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--config", type=Path, default=ROOT / "benchmark.json")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("validate", help="Validate records and show split counts")
    commands.add_parser("demo", help="Show known, newly released, and unknown queries")
    ask = commands.add_parser("ask", help="Search published glossary definitions")
    ask.add_argument("question")
    ask.add_argument("--release", type=int, help="Use an earlier glossary release")
    ask.add_argument("--json", action="store_true", help="Print the structured result")

    serve = commands.add_parser("serve", help="Open a local Khmer Q&A web interface")
    serve.add_argument("--port", type=int, default=8000)

    benchmark = commands.add_parser("benchmark", help="Run matched-budget learning comparisons")
    benchmark.add_argument("--model", choices=("linear", "ffn"), default="linear")
    benchmark.add_argument("--split", choices=("validation", "test"), default="validation")
    benchmark.add_argument("--order", type=int, nargs="+", metavar="SESSION")
    benchmark.add_argument("--output", type=Path, required=True, help="Save metrics and predictions as JSON")
    return parser


def show_answer(response: dict) -> None:
    fact = response["fact"]
    if fact:
        print(f'{fact["version_id"]} · {fact["answer"]}')
        print(f'Source {fact["source_id"]} · released in session {fact["session"]}')
    else:
        print("UNKNOWN · រកមិនឃើញនិយមន័យដែលត្រូវនឹងសំណួរ។")
    print(f'Retrieval score {response["score"]:.3f} · gap {response["gap"]:.3f}')


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    try:
        dataset = load_dataset(args.data)
        if args.command == "validate":
            print(json.dumps(dataset.summary(), indent=2))
            return
        config = Config.load(args.config)
        if args.command == "benchmark":
            from .benchmark import run_benchmark

            order = tuple(args.order) if args.order else dataset.sessions
            result = run_benchmark(dataset.reordered(order), config, args.split, args.model,
                                   args.data, order)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
            print(f'Saved {len(result["runs"])} runs to {args.output}')
            return

        glossary = Glossary(dataset, config)
        if args.command == "ask":
            release = args.release if args.release is not None else dataset.sessions[-1]
            response = glossary.ask(args.question, release)
            if args.json:
                print(json.dumps(response, ensure_ascii=False, indent=2))
            else:
                show_answer(response)
        elif args.command == "demo":
            for question, release in EXAMPLES:
                if release in dataset.sessions:
                    print(f"\nRelease {release} · {question}")
                    show_answer(glossary.ask(question, release))
        else:
            from .web import serve

            serve(glossary, args.port)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
