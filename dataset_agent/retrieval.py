from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_+-]+")


def tokenize(text: str) -> list[str]:
    """Return deterministic lowercase tokens for scientific metadata text."""
    return TOKEN_PATTERN.findall(text.lower())


def chunk_text(text: str, *, size: int = 80, overlap: int = 15) -> list[str]:
    """Split text into overlapping word chunks without external dependencies."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    words = text.split()
    if not words:
        return []
    step = size - overlap
    return [" ".join(words[start : start + size]) for start in range(0, len(words), step)]


@dataclass(frozen=True)
class SearchResult:
    document_id: str
    score: float


class TfidfRetriever:
    """Small, auditable TF-IDF baseline for metadata evidence retrieval."""

    def __init__(self, documents: dict[str, str]):
        if not documents:
            raise ValueError("At least one document is required")
        self.documents = documents
        self._tokens = {key: tokenize(value) for key, value in documents.items()}
        document_frequency: Counter[str] = Counter()
        for tokens in self._tokens.values():
            document_frequency.update(set(tokens))
        total = len(documents)
        self._idf = {
            term: math.log((1 + total) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }
        self._vectors = {key: self._vector(tokens) for key, tokens in self._tokens.items()}

    def _vector(self, tokens: Iterable[str]) -> dict[str, float]:
        counts = Counter(tokens)
        length = sum(counts.values()) or 1
        return {term: count / length * self._idf.get(term, 0.0) for term, count in counts.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        dot = sum(value * right.get(term, 0.0) for term, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)

    def search(self, query: str, *, top_k: int = 3) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        query_vector = self._vector(tokenize(query))
        ranked = [
            SearchResult(document_id=key, score=round(self._cosine(query_vector, vector), 6))
            for key, vector in self._vectors.items()
        ]
        return sorted(ranked, key=lambda item: (-item.score, item.document_id))[:top_k]


def evaluate_retrieval(
    retriever: TfidfRetriever,
    cases: list[dict[str, object]],
    *,
    top_k: int = 3,
) -> dict[str, float | int]:
    """Compute Recall@K and MRR for labelled retrieval cases."""
    if not cases:
        raise ValueError("At least one evaluation case is required")
    hits = 0
    reciprocal_ranks: list[float] = []
    for case in cases:
        expected = str(case["expected_document_id"])
        results = retriever.search(str(case["query"]), top_k=top_k)
        rank = next((index for index, item in enumerate(results, start=1) if item.document_id == expected), None)
        hits += int(rank is not None)
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
    return {
        "cases": len(cases),
        "top_k": top_k,
        "recall_at_k": round(hits / len(cases), 4),
        "mrr": round(sum(reciprocal_ranks) / len(cases), 4),
    }
