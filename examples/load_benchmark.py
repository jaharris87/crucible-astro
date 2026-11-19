"""Inspect a qualified local split without fitting or publishing real records.

Run: uv run python -B examples/load_benchmark.py /absolute/access.json
"""

import argparse
import json

from crucible.benchmark import NAME, VERSION, load_benchmark


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "config", help="local access JSON; see docs/science/data/LOADING.md"
    )
    parser.add_argument(
        "--split", choices=("train", "validation", "test"), default="train"
    )
    args = parser.parse_args()
    data = load_benchmark(
        NAME, VERSION, use="rhs_training", split=args.split, config=args.config
    )
    metadata = data["metadata"]
    print(
        json.dumps(
            {
                "name": metadata["name"],
                "version": metadata["version"],
                "split": metadata["split"],
                "Y_shape": list(data["Y"].shape),
                "fresh_rhs_shape": list(data["fresh_rhs"].shape),
                "histories": len(set(data["particle0"].tolist())),
                "operational_groups": len(set(data["group"].tolist())),
                "units": metadata["units"],
                "overlay_sha256": metadata["overlay_sha256"],
                "payload_sha256": metadata["payload_sha256"],
                "original_scoring_source_sha256": metadata[
                    "original_scoring_source_sha256"
                ],
                "accepted_scoring_successor": metadata["accepted_scoring_successor"],
                "qualified_uses": metadata["qualification_scope"]["qualified_uses"],
                "excluded_uses": list(metadata["qualification_scope"]["excluded_uses"]),
                "limitations": metadata["qualification_scope"]["limitations"],
                "model_results": "NOT_EVALUATED",
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
