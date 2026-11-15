from __future__ import annotations

from .models import AccessStatus, CompatibilityCheck, NormalizedDataset


SUPPORTED_FORMATS = {"CSV", "TSV", "JSON", "XML", "FASTQ", "BAM", "VCF", "H5AD"}


def check_genengine_compatibility(dataset: NormalizedDataset) -> CompatibilityCheck:
    passed: list[str] = []
    failed: list[str] = []
    gaps = list(dataset.information_gaps)

    if dataset.source_id:
        passed.append("Stable source identifier present")
    else:
        failed.append("Stable source identifier missing")
    if dataset.title and dataset.description:
        passed.append("Core descriptive metadata present")
    else:
        failed.append("Title or description missing")
    if dataset.domain != "unknown":
        passed.append("Domain classified")
    else:
        failed.append("Domain classification missing")
    if set(dataset.formats) & SUPPORTED_FORMATS:
        passed.append("At least one supported distribution format")
    else:
        failed.append("No supported distribution format")
    if dataset.access_status != AccessStatus.UNKNOWN:
        passed.append("Access status resolved")
    else:
        failed.append("Access status unresolved")
    if dataset.evidence:
        passed.append("Field-level provenance evidence retained")

    total = len(passed) + len(failed)
    score = len(passed) / total if total else 0.0
    return CompatibilityCheck(
        compatible=score >= 0.7 and not any("identifier" in x.lower() for x in failed),
        score=round(score, 3),
        passed_rules=passed,
        failed_rules=failed,
        information_gaps=gaps,
    )

