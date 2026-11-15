from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class AccessStatus(str, Enum):
    OPEN = "open"
    CONTROLLED = "controlled"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class ReviewStatus(str, Enum):
    AUTO_ACCEPT = "auto_accept"
    HUMAN_REVIEW = "human_review"
    REJECT = "reject"


class Evidence(BaseModel):
    field: str
    value: str
    source: str
    source_url: HttpUrl | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RawDataset(BaseModel):
    source: str
    source_id: str
    title: str
    description: str = ""
    landing_page: HttpUrl
    version: str | None = None
    updated_at: datetime | None = None
    formats: list[str] = Field(default_factory=list)
    access_text: str = ""
    keywords: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedDataset(BaseModel):
    canonical_id: str
    source: str
    source_id: str
    title: str
    description: str
    landing_page: HttpUrl
    version: str | None = None
    updated_at: datetime | None = None
    domain: str
    phenotype: list[str] = Field(default_factory=list)
    omics_layer: list[str] = Field(default_factory=list)
    formats: list[str] = Field(default_factory=list)
    access_status: AccessStatus = AccessStatus.UNKNOWN
    license: str | None = None
    organism: str | None = None
    sample_size: int | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    information_gaps: list[str] = Field(default_factory=list)
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class DuplicateMatch(BaseModel):
    candidate_id: str
    duplicate_of: str
    match_type: str
    score: float = Field(ge=0, le=1)
    reasons: list[str]


class CompatibilityCheck(BaseModel):
    compatible: bool
    score: float = Field(ge=0, le=1)
    passed_rules: list[str]
    failed_rules: list[str]
    information_gaps: list[str]


class Recommendation(BaseModel):
    dataset: NormalizedDataset
    compatibility: CompatibilityCheck
    confidence: float = Field(ge=0, le=1)
    decision: ReviewStatus
    rationale: list[str]
    duplicate: DuplicateMatch | None = None

