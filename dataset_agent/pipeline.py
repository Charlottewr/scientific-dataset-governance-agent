from __future__ import annotations

from .classify import enrich_classification
from .compatibility import check_genengine_compatibility
from .deduplicate import find_duplicate
from .models import NormalizedDataset, RawDataset, Recommendation
from .normalize import normalize
from .recommend import build_recommendation


def process(records: list[RawDataset]) -> list[Recommendation]:
    accepted_catalog: list[NormalizedDataset] = []
    recommendations: list[Recommendation] = []
    for raw in records:
        dataset = enrich_classification(normalize(raw))
        duplicate = find_duplicate(dataset, accepted_catalog)
        compatibility = check_genengine_compatibility(dataset)
        recommendation = build_recommendation(dataset, compatibility, duplicate)
        recommendations.append(recommendation)
        if duplicate is None:
            accepted_catalog.append(dataset)
    return recommendations

