import json
import tempfile
import threading
import unittest
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np

from khmer_learning.benchmark import run_benchmark
from khmer_learning.config import Config
from khmer_learning.data import load_dataset
from khmer_learning.glossary import Glossary
from khmer_learning.model import Classifier
from khmer_learning.replay import Reservoir, balanced_memory
from khmer_learning.web import handler_for

ROOT = Path(__file__).resolve().parents[1]
SAFETY_QUESTION = "តើស្តុកបម្រុងជាអ្វី?"


class KhmerMindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(ROOT / "data")
        cls.config = Config.load(ROOT / "benchmark.json")

    def test_dataset_rejects_cross_split_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            for filename in ("facts.jsonl", "questions.jsonl"):
                (data / filename).write_bytes((ROOT / "data" / filename).read_bytes())
            questions = data / "questions.jsonl"
            row = json.loads(questions.read_text(encoding="utf-8").splitlines()[0])
            row.update(question_id="leaked_copy", split="test", paraphrase_group="other")
            with questions.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate normalized question"):
                load_dataset(data)

    def test_retrieval_respects_release(self):
        glossary = Glossary(self.dataset, self.config)
        self.assertIsNone(glossary.ask(SAFETY_QUESTION, 1)["fact"])
        self.assertEqual(glossary.ask(SAFETY_QUESTION, 3)["fact"]["version_id"],
                         "safety_stock_v1")
        self.assertIsNone(glossary.ask("តើថ្ងៃនេះសីតុណ្ហភាពប៉ុន្មាន?", 3)["fact"])

    def test_reordered_releases_do_not_change_ids(self):
        alternate = self.dataset.reordered((3, 1, 2))
        self.assertEqual(alternate.facts["safety_stock"].session, 1)
        self.assertEqual(alternate.facts["safety_stock"].version_id, "safety_stock_v1")
        with self.assertRaises(ValueError):
            self.dataset.reordered((1, 1, 2))

    def test_ffn_gradients_match_centered_differences(self):
        model = Classifier.initialize(2, 3, 3, 9)
        x = np.array([[0.5, 1.2], [1.1, -0.4]])
        labels = np.array([2, 0])
        _, grads = model.loss_and_gradients(x, labels)
        epsilon = 1e-6
        for parameter, analytical in grads:
            for index in np.ndindex(parameter.shape):
                original = parameter[index]
                parameter[index] = original + epsilon
                plus, _ = model.loss_and_gradients(x, labels)
                parameter[index] = original - epsilon
                minus, _ = model.loss_and_gradients(x, labels)
                parameter[index] = original
                self.assertAlmostEqual(float(analytical[index]), (plus - minus) / (2 * epsilon), 6)

    def test_memory_is_bounded_and_balanced_uses_available_rows(self):
        reservoir = Reservoir(4)
        rng = np.random.default_rng(7)
        reservoir.add(list(range(12)), rng)
        self.assertEqual(len(set(reservoir.items)), 4)
        reservoir.add(list(range(12, 18)), rng)
        self.assertEqual(reservoir.count, 18)
        self.assertEqual(len(set(reservoir.items)), 4)
        labels = np.array([0, 0, 0, 1, 2])
        selected = balanced_memory([1], [2, 3, 4], labels, 3, rng)
        self.assertNotIn(0, selected)
        self.assertEqual(set(labels[selected]), {0, 1, 2})

    def test_benchmark_matches_update_budgets_and_never_uses_future_labels(self):
        settings = replace(self.config, steps=5, seeds=(7,), replay_capacity=5)
        result = run_benchmark(self.dataset, settings, "validation", "ffn",
                               ROOT / "data", (1, 2, 3))
        for run in result["runs"]:
            if run["method"] in ("sequential", "uniform_replay", "fact_balanced_replay"):
                self.assertEqual([row["optimizer_steps"] for row in run["sessions"]],
                                 [5, 5, 5])
            for row in run["sessions"]:
                self.assertLessEqual(row.get("buffer_examples", 0), 5)
                versions = {fact.version_id for fact in self.dataset.facts.values()
                            if fact.session <= row["session"]}
                for prediction in row["predictions"]:
                    self.assertIn(prediction["top_version_id"], {None, *versions})
        with_replay = next(run for run in result["runs"] if run["method"] == "uniform_replay")
        self.assertEqual(with_replay["sessions"][1]["rehearsal_draws"],
                         settings.steps * settings.replay_samples)

    def test_browser_endpoints_share_release_behavior(self):
        glossary = Glossary(self.dataset, self.config)
        with ThreadingHTTPServer(("127.0.0.1", 0), handler_for(glossary)) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with urlopen(base + "/", timeout=3) as response:
                    self.assertIn(b"KhmerMind", response.read())
                for release in (1, 3):
                    params = urlencode({"question": SAFETY_QUESTION, "release": release})
                    with urlopen(base + "/api/ask?" + params, timeout=3) as response:
                        self.assertEqual(json.load(response), glossary.ask(SAFETY_QUESTION, release))
                with self.assertRaises(HTTPError) as error:
                    urlopen(base + "/api/ask?question=test&release=99", timeout=3)
                self.assertEqual(error.exception.code, 400)
                error.exception.close()
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
