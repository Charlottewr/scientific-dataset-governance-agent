from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import Recommendation


class ReviewStore:
    def __init__(self, path: str | Path = "data/reviews.db") -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS review_queue (
                    id TEXT PRIMARY KEY, canonical_id TEXT NOT NULL, payload TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_log (
                    event_id TEXT PRIMARY KEY, review_id TEXT NOT NULL, action TEXT NOT NULL,
                    reviewer TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL
                );
                """
            )

    def enqueue(self, recommendation: Recommendation) -> str:
        review_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute(
                "INSERT INTO review_queue VALUES (?, ?, ?, ?, ?, ?)",
                (review_id, recommendation.dataset.canonical_id,
                 recommendation.model_dump_json(), "pending", now, now),
            )
            self._audit(db, review_id, "enqueued", "system", "Recommendation created")
        return review_id

    def list(self, status: str | None = None) -> list[dict]:
        query = "SELECT * FROM review_queue"
        args: tuple[str, ...] = ()
        if status:
            query += " WHERE status = ?"
            args = (status,)
        query += " ORDER BY created_at DESC"
        with self._connect() as db:
            rows = db.execute(query, args).fetchall()
        return [dict(row) | {"payload": json.loads(row["payload"])} for row in rows]

    def decide(self, review_id: str, action: str, reviewer: str, note: str = "") -> None:
        allowed = {"approved", "rejected", "needs_information"}
        if action not in allowed:
            raise ValueError(f"action must be one of {sorted(allowed)}")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            changed = db.execute(
                "UPDATE review_queue SET status = ?, updated_at = ? WHERE id = ?",
                (action, now, review_id),
            ).rowcount
            if not changed:
                raise KeyError(review_id)
            self._audit(db, review_id, action, reviewer, note)

    def audit(self, review_id: str) -> list[dict]:
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM audit_log WHERE review_id = ? ORDER BY created_at", (review_id,)
            ).fetchall()]

    def metrics(self) -> dict:
        with self._connect() as db:
            total = db.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0]
            grouped = dict(db.execute(
                "SELECT status, COUNT(*) FROM review_queue GROUP BY status"
            ).fetchall())
            payloads = [json.loads(row[0]) for row in db.execute("SELECT payload FROM review_queue")]
        confidences = [item["confidence"] for item in payloads]
        gaps = [len(item["dataset"]["information_gaps"]) for item in payloads]
        duplicates = sum(1 for item in payloads if item.get("duplicate"))
        return {
            "total": total,
            "status_counts": grouped,
            "average_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0,
            "metadata_coverage": round(1 - sum(gaps) / max(len(gaps) * 6, 1), 3) if gaps else 0,
            "duplicate_rate": round(duplicates / total, 3) if total else 0,
        }

    @staticmethod
    def _audit(db: sqlite3.Connection, review_id: str, action: str, reviewer: str, note: str) -> None:
        db.execute(
            "INSERT INTO audit_log VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid4()), review_id, action, reviewer, note, datetime.now(timezone.utc).isoformat()),
        )
