from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .models import RawDataset, Recommendation
from .pipeline import process
from .review_store import ReviewStore


app = FastAPI(
    title="Scientific Dataset Governance Agent",
    version="0.1.0",
    description="Evidence-first metadata normalization, compatibility checks and review routing.",
)
store = ReviewStore()


class ReviewDecision(BaseModel):
    action: str
    reviewer: str
    note: str = ""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/evaluate", response_model=list[Recommendation])
def evaluate(records: list[RawDataset]) -> list[Recommendation]:
    results = process(records)
    for item in results:
        store.enqueue(item)
    return results


@app.get("/v1/reviews")
def reviews(status: str | None = None) -> list[dict]:
    return store.list(status)


@app.post("/v1/reviews/{review_id}/decision")
def decide(review_id: str, decision: ReviewDecision) -> dict[str, str]:
    try:
        store.decide(review_id, decision.action, decision.reviewer, decision.note)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"review_id": review_id, "status": decision.action}


@app.get("/v1/reviews/{review_id}/audit")
def audit(review_id: str) -> list[dict]:
    return store.audit(review_id)


@app.get("/v1/metrics")
def metrics() -> dict:
    return store.metrics()


PAGE = """<!doctype html><html><head><meta charset='utf-8'><title>Dataset Review</title>
<style>body{font:15px system-ui;margin:32px;max-width:1100px}h1{margin-bottom:4px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card{border:1px solid #ddd;border-radius:10px;padding:16px}table{width:100%;border-collapse:collapse;margin-top:24px}th,td{padding:10px;border-bottom:1px solid #ddd;text-align:left}button{margin:2px;padding:6px 9px}</style></head>
<body><h1>Scientific Dataset Review</h1><p>Human-in-the-loop queue and data quality dashboard</p><div class='grid' id='metrics'></div><table><thead><tr><th>Dataset</th><th>Confidence</th><th>Status</th><th>Action</th></tr></thead><tbody id='rows'></tbody></table>
<script>async function load(){const m=await(await fetch('/v1/metrics')).json();document.querySelector('#metrics').innerHTML=Object.entries(m).filter(x=>x[0]!='status_counts').map(x=>`<div class=card><b>${x[0]}</b><div>${x[1]}</div></div>`).join('');const q=await(await fetch('/v1/reviews')).json();document.querySelector('#rows').innerHTML=q.map(x=>`<tr><td>${x.payload.dataset.title}</td><td>${x.payload.confidence}</td><td>${x.status}</td><td>${['approved','rejected','needs_information'].map(a=>`<button onclick="decide('${x.id}','${a}')">${a}</button>`).join('')}</td></tr>`).join('')}async function decide(id,action){await fetch(`/v1/reviews/${id}/decision`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,reviewer:'demo-reviewer'})});load()}load()</script></body></html>"""


@app.get("/review", response_class=HTMLResponse)
def review_page() -> str:
    return PAGE


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return PAGE

