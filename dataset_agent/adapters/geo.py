from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from ..models import RawDataset


class GEOAdapter:
    """Small NCBI GEO adapter built on the official E-utilities API."""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, fetch_json: Callable[[str], dict] | None = None) -> None:
        self.fetch_json = fetch_json or self._fetch_json

    @staticmethod
    def _fetch_json(url: str) -> dict:
        with urlopen(url, timeout=20) as response:  # nosec: B310 - fixed NCBI host
            return json.loads(response.read().decode("utf-8"))

    def search(self, query: str, limit: int = 10) -> list[RawDataset]:
        search_url = f"{self.base_url}/esearch.fcgi?" + urlencode(
            {"db": "gds", "term": query, "retmode": "json", "retmax": limit}
        )
        ids = self.fetch_json(search_url).get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        summary_url = f"{self.base_url}/esummary.fcgi?" + urlencode(
            {"db": "gds", "id": ",".join(ids), "retmode": "json"}
        )
        result = self.fetch_json(summary_url).get("result", {})
        return [self._to_raw(result[item_id]) for item_id in ids if item_id in result]

    @staticmethod
    def _to_raw(item: dict) -> RawDataset:
        accession = item.get("accession") or f"GDS{item.get('uid', 'unknown')}"
        summary = item.get("summary", "")
        taxon = item.get("taxon", "")
        gds_type = item.get("gdstype", "")
        sample_count = item.get("n_samples")
        return RawDataset(
            source="NCBI GEO",
            source_id=accession,
            title=item.get("title") or accession,
            description=summary,
            landing_page=f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}",
            updated_at=datetime.now(timezone.utc),
            formats=["SOFT", "MINiML"],
            access_text="Public GEO record",
            keywords=[gds_type, taxon],
            metadata={
                "organism": taxon or None,
                "sample_size": sample_count,
                "platform": item.get("gpl"),
                "source_payload": item,
            },
        )
