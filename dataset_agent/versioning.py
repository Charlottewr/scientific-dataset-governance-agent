from __future__ import annotations

from typing import Any

from .models import NormalizedDataset


TRACKED_FIELDS = (
    "title", "description", "version", "updated_at", "domain", "phenotype",
    "omics_layer", "formats", "access_status", "license", "organism", "sample_size",
)


def metadata_diff(previous: NormalizedDataset, current: NormalizedDataset) -> dict[str, Any]:
    changes: dict[str, dict[str, Any]] = {}
    for field in TRACKED_FIELDS:
        before = getattr(previous, field)
        after = getattr(current, field)
        if before != after:
            changes[field] = {
                "before": before.value if hasattr(before, "value") else before,
                "after": after.value if hasattr(after, "value") else after,
            }
    return {
        "canonical_id": current.canonical_id,
        "changed": bool(changes),
        "change_count": len(changes),
        "changes": changes,
    }
