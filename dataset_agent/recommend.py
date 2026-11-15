from __future__ import annotations

from .models import DuplicateMatch, NormalizedDataset, Recommendation, ReviewStatus


def build_recommendation(
    dataset: NormalizedDataset,
    compatibility,
    duplicate: DuplicateMatch | None,
) -> Recommendation:
    evidence_coverage = min(1.0, len(dataset.evidence) / 3)
    gap_penalty = min(0.35, 0.05 * len(dataset.information_gaps))
    confidence = max(0.0, min(1.0, 0.65 * compatibility.score + 0.35 * evidence_coverage - gap_penalty))
    rationale = [f"Compatibility score={compatibility.score:.3f}", f"Evidence records={len(dataset.evidence)}"]

    if duplicate is not None:
        decision = ReviewStatus.HUMAN_REVIEW
        rationale.append(f"Possible duplicate detected ({duplicate.match_type}, score={duplicate.score:.2f})")
    elif compatibility.compatible and confidence >= 0.7 and not dataset.information_gaps:
        decision = ReviewStatus.AUTO_ACCEPT
        rationale.append("All required metadata and quality gates passed")
    elif compatibility.score < 0.45:
        decision = ReviewStatus.REJECT
        rationale.append("Compatibility is below the minimum threshold")
    else:
        decision = ReviewStatus.HUMAN_REVIEW
        rationale.append("Uncertainty or information gaps require reviewer judgment")

    return Recommendation(
        dataset=dataset,
        compatibility=compatibility,
        confidence=round(confidence, 3),
        decision=decision,
        rationale=rationale,
        duplicate=duplicate,
    )

