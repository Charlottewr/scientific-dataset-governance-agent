from __future__ import annotations

from fastapi import FastAPI

from .models import RawDataset, Recommendation
from .pipeline import process


app = FastAPI(
    title="Scientific Dataset Governance Agent",
    version="0.1.0",
    description="Evidence-first metadata normalization, compatibility checks and review routing.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/evaluate", response_model=list[Recommendation])
def evaluate(records: list[RawDataset]) -> list[Recommendation]:
    return process(records)

