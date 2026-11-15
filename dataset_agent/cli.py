from __future__ import annotations

import argparse

from .io import load_records, write_recommendations
from .pipeline import process


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the scientific dataset governance pipeline")
    parser.add_argument("--input", default="data/sample_datasets.json")
    parser.add_argument("--output", default="data/output/recommendations.json")
    args = parser.parse_args()
    recommendations = process(load_records(args.input))
    write_recommendations(recommendations, args.output)
    for item in recommendations:
        print(f"{item.dataset.source_id}: {item.decision.value} (confidence={item.confidence:.3f})")


if __name__ == "__main__":
    main()

