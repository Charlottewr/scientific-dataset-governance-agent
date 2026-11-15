import unittest
from pathlib import Path

from dataset_agent.io import load_records
from dataset_agent.pipeline import process


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.results = process(load_records(ROOT / "data" / "sample_datasets.json"))

    def test_pipeline_produces_recommendations(self):
        self.assertEqual(len(self.results), 3)
        self.assertTrue(all(0 <= item.confidence <= 1 for item in self.results))

    def test_version_like_record_is_routed_to_review(self):
        second = self.results[1]
        self.assertEqual(second.decision.value, "human_review")
        self.assertIsNotNone(second.duplicate)

    def test_controlled_access_is_normalized(self):
        third = self.results[2]
        self.assertEqual(third.dataset.access_status.value, "controlled")
        self.assertIn("VCF", third.dataset.formats)


if __name__ == "__main__":
    unittest.main()

