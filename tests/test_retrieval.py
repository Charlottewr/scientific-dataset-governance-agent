import unittest

from dataset_agent.retrieval import TfidfRetriever, chunk_text, evaluate_retrieval


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.documents = {
            "geo-expression": "GEO RNA-seq gene expression breast cancer open access metadata",
            "controlled-genomics": "controlled access whole genome sequencing VCF phenotype cohort",
            "proteomics": "mass spectrometry proteomics protein abundance mzML public dataset",
        }
        self.retriever = TfidfRetriever(self.documents)

    def test_chunking_uses_overlap(self):
        chunks = chunk_text("one two three four five six", size=4, overlap=2)
        self.assertEqual(chunks[0], "one two three four")
        self.assertEqual(chunks[1], "three four five six")

    def test_search_returns_relevant_document(self):
        result = self.retriever.search("RNA-seq breast cancer expression", top_k=1)
        self.assertEqual(result[0].document_id, "geo-expression")

    def test_metrics_are_reproducible(self):
        cases = [
            {"query": "VCF genome cohort", "expected_document_id": "controlled-genomics"},
            {"query": "protein abundance mass spectrometry", "expected_document_id": "proteomics"},
            {"query": "GEO gene expression", "expected_document_id": "geo-expression"},
        ]
        metrics = evaluate_retrieval(self.retriever, cases, top_k=2)
        self.assertEqual(metrics["recall_at_k"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)


if __name__ == "__main__":
    unittest.main()
