import unittest

from dataset_agent.adapters.geo import GEOAdapter


class GEOAdapterTests(unittest.TestCase):
    def test_search_maps_ncbi_summary_to_raw_dataset(self):
        responses = iter([
            {"esearchresult": {"idlist": ["200000001"]}},
            {"result": {"200000001": {
                "uid": "200000001", "accession": "GSE1", "title": "RNA-seq study",
                "summary": "Human tumor expression", "taxon": "Homo sapiens",
                "gdstype": "Expression profiling by high throughput sequencing", "n_samples": 24,
            }}},
        ])
        records = GEOAdapter(fetch_json=lambda _: next(responses)).search("cancer", limit=1)
        self.assertEqual(records[0].source_id, "GSE1")
        self.assertEqual(records[0].metadata["sample_size"], 24)


if __name__ == "__main__":
    unittest.main()
