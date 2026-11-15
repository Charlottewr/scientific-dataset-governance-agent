from __future__ import annotations

import re
from difflib import SequenceMatcher

from .models import DuplicateMatch, NormalizedDataset


def _clean_title(value: str) -> str:
    value = re.sub(r"\bv(?:ersion)?\s*\d+(?:\.\d+)*\b", "", value.lower())
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def find_duplicate(candidate: NormalizedDataset, existing: list[NormalizedDataset]) -> DuplicateMatch | None:
    best: DuplicateMatch | None = None
    for item in existing:
        reasons: list[str] = []
        if candidate.source == item.source and candidate.source_id == item.source_id:
            return DuplicateMatch(
                candidate_id=candidate.canonical_id,
                duplicate_of=item.canonical_id,
                match_type="stable_identifier",
                score=1.0,
                reasons=["Same source and source identifier"],
            )
        title_score = SequenceMatcher(None, _clean_title(candidate.title), _clean_title(item.title)).ratio()
        if title_score >= 0.9:
            reasons.append(f"Normalized title similarity={title_score:.2f}")
        if candidate.organism and candidate.organism == item.organism:
            reasons.append("Same organism")
        if candidate.sample_size and candidate.sample_size == item.sample_size:
            reasons.append("Same sample size")
        score = min(1.0, title_score + 0.04 * max(0, len(reasons) - 1))
        if reasons and score >= 0.9 and (best is None or score > best.score):
            best = DuplicateMatch(
                candidate_id=candidate.canonical_id,
                duplicate_of=item.canonical_id,
                match_type="metadata_similarity",
                score=score,
                reasons=reasons,
            )
    return best

