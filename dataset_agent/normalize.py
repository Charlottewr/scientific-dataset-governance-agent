from __future__ import annotations

import hashlib
import re

from .models import AccessStatus, Evidence, NormalizedDataset, RawDataset


FORMAT_ALIASES = {
    "csv": "CSV",
    "tsv": "TSV",
    "json": "JSON",
    "xml": "XML",
    "fastq": "FASTQ",
    "bam": "BAM",
    "vcf": "VCF",
    "h5ad": "H5AD",
    "txt": "TXT",
}


def _canonical_id(source: str, source_id: str) -> str:
    token = f"{source.strip().lower()}::{source_id.strip().lower()}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def _access_status(text: str) -> AccessStatus:
    value = text.lower()
    if any(word in value for word in ("controlled", "application", "dbgap")):
        return AccessStatus.CONTROLLED
    if any(word in value for word in ("restricted", "embargo")):
        return AccessStatus.RESTRICTED
    if any(word in value for word in ("open", "public", "download")):
        return AccessStatus.OPEN
    return AccessStatus.UNKNOWN


def _formats(values: list[str]) -> list[str]:
    normalized = {FORMAT_ALIASES.get(v.strip().lower(), v.strip().upper()) for v in values if v.strip()}
    return sorted(normalized)


def normalize(raw: RawDataset) -> NormalizedDataset:
    metadata = raw.metadata
    evidence = [
        Evidence(field="title", value=raw.title, source=raw.source, source_url=raw.landing_page),
        Evidence(field="access_status", value=raw.access_text or "unknown", source=raw.source, source_url=raw.landing_page),
    ]
    gaps: list[str] = []
    for field in ("license", "organism", "sample_size"):
        if metadata.get(field) in (None, "", []):
            gaps.append(f"Missing {field}")

    sample_size = metadata.get("sample_size")
    if isinstance(sample_size, str):
        digits = re.sub(r"[^0-9]", "", sample_size)
        sample_size = int(digits) if digits else None

    return NormalizedDataset(
        canonical_id=_canonical_id(raw.source, raw.source_id),
        source=raw.source,
        source_id=raw.source_id,
        title=raw.title.strip(),
        description=raw.description.strip(),
        landing_page=raw.landing_page,
        version=raw.version,
        updated_at=raw.updated_at,
        domain=str(metadata.get("domain") or "unknown").lower(),
        phenotype=sorted({str(x).lower() for x in metadata.get("phenotype", [])}),
        omics_layer=sorted({str(x).lower() for x in metadata.get("omics_layer", [])}),
        formats=_formats(raw.formats),
        access_status=_access_status(raw.access_text),
        license=metadata.get("license"),
        organism=metadata.get("organism"),
        sample_size=sample_size,
        evidence=evidence,
        information_gaps=gaps,
        raw_metadata=metadata,
    )

