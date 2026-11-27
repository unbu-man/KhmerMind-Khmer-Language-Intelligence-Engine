import tempfile
import unittest
from collections import Counter
from pathlib import Path

from khmer_learning.tokenization import BytePairEncoder, normalize_token_text
from khmer_learning.tokenization_audit import DEFAULT_DATA, load_pairs, make_report


class BytePairTests(unittest.TestCase):
    def test_highest_count_pair_and_merged_length(self):
        encoder = BytePairEncoder.train(Counter({"abab": 1, "abcc": 1}), 1)
        self.assertEqual(encoder.merges, ((ord("a"), ord("b")),))
        self.assertEqual(encoder.encode("abab"), (256, 256))
        self.assertEqual(encoder.decode(encoder.encode("abcc")), "abcc")

    def test_ties_are_deterministic_and_merges_do_not_overlap(self):
        tied = BytePairEncoder.train(Counter({"xy": 1, "ab": 1}), 1)
        self.assertEqual(tied.merges, ((ord("a"), ord("b")),))
        repeated = BytePairEncoder.train(Counter({"aaa": 1}), 1)
        self.assertEqual(repeated.encode("aaa"), (256, ord("a")))

    def test_round_trip_preserves_normalized_khmer(self):
        test = "  តើស្តុកជាអ្វី?  "
        encoder = BytePairEncoder.train(Counter({"ស្តុក": 4, "stock": 1}), 8)
        self.assertEqual(encoder.decode(encoder.encode(test)), normalize_token_text(test))
        empty = BytePairEncoder.train(Counter(), 10)
        self.assertEqual(len(empty.encode("ស្តុក")), 15)

    def test_cross_split_duplicates_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pairs.jsonl"
            path.write_text(
                '{"id":"one","split":"train","kind":"term","km":"ក","en":"a"}\n'
                '{"id":"two","split":"test","kind":"term","km":"ក","en":"b"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "repeated km text"):
                load_pairs(path)

    def test_report_matches_the_published_artifact(self):
        report = DEFAULT_DATA.parents[1] / "reports" / "tokenization.md"
        self.assertEqual(make_report(DEFAULT_DATA, 128), report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
