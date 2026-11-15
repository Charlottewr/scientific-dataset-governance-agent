import tempfile
import unittest
from pathlib import Path

from dataset_agent.io import load_records
from dataset_agent.pipeline import process
from dataset_agent.review_store import ReviewStore
from dataset_agent.versioning import metadata_diff


ROOT = Path(__file__).resolve().parents[1]


class ReviewAndVersioningTests(unittest.TestCase):
    def setUp(self):
        self.results = process(load_records(ROOT / "data" / "sample_datasets.json"))

    def test_version_diff_is_explicit(self):
        diff = metadata_diff(self.results[0].dataset, self.results[1].dataset)
        self.assertTrue(diff["changed"])
        self.assertIn("title", diff["changes"])

    def test_review_queue_and_audit_log(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ReviewStore(Path(folder) / "reviews.db")
            review_id = store.enqueue(self.results[0])
            store.decide(review_id, "approved", "reviewer@example.com", "Evidence checked")
            self.assertEqual(store.list()[0]["status"], "approved")
            self.assertEqual(len(store.audit(review_id)), 2)
            self.assertEqual(store.metrics()["total"], 1)


if __name__ == "__main__":
    unittest.main()
