"""Integration tests for the SagaRoutes research-data pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

CURATED_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "curated"
)

EXPORT_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "exports"
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


class SagaRoutesPipelineTests(unittest.TestCase):
    """Test major structural invariants in the prototype dataset."""

    @classmethod
    def setUpClass(cls) -> None:
        exporters = [
            "src/sagaroutes/export_geojson.py",
            "src/sagaroutes/export_journeys.py",
        ]

        for exporter in exporters:
            result = subprocess.run(
                [
                    sys.executable,
                    exporter,
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"{exporter} failed before tests:\n"
                    + result.stdout
                    + result.stderr
                )
    def test_passage_ids_are_unique(self) -> None:
        data = load_json(
            CURATED_DIRECTORY / "passages.json"
        )

        identifiers = [
            passage["id"]
            for passage in data["passages"]
        ]

        self.assertEqual(
            len(identifiers),
            len(set(identifiers)),
        )

    def test_place_ids_are_unique(self) -> None:
        data = load_json(
            CURATED_DIRECTORY / "places.json"
        )

        identifiers = [
            place["id"]
            for place in data["places"]
        ]

        self.assertEqual(
            len(identifiers),
            len(set(identifiers)),
        )

    def test_every_place_is_exported(self) -> None:
        places = load_json(
            CURATED_DIRECTORY / "places.json"
        )["places"]

        mapped = load_json(
            EXPORT_DIRECTORY / "places.geojson"
        )["features"]

        unmapped = load_json(
            EXPORT_DIRECTORY / "unmapped_places.json"
        )["places"]

        exported_ids = {
            feature["properties"]["place_id"]
            for feature in mapped
        }

        exported_ids.update(
            place["id"]
            for place in unmapped
        )

        curated_ids = {
            place["id"]
            for place in places
        }

        self.assertEqual(
            exported_ids,
            curated_ids,
        )

    def test_geojson_contains_only_mapped_places(self) -> None:
        geojson = load_json(
            EXPORT_DIRECTORY / "places.geojson"
        )

        self.assertEqual(
            geojson["type"],
            "FeatureCollection",
        )

        for feature in geojson["features"]:
            self.assertEqual(
                feature["geometry"]["type"],
                "Point",
            )

            coordinates = feature["geometry"][
                "coordinates"
            ]

            self.assertEqual(
                len(coordinates),
                2,
            )

    def test_journey_leg_counts_match(self) -> None:
        curated_legs = load_json(
            CURATED_DIRECTORY / "journey_legs.json"
        )["journey_legs"]

        exported_journeys = load_json(
            EXPORT_DIRECTORY / "journeys.json"
        )["journeys"]

        exported_leg_count = sum(
            journey["leg_count"]
            for journey in exported_journeys
        )

        self.assertEqual(
            exported_leg_count,
            len(curated_legs),
        )

    def test_journey_routes_are_continuous(self) -> None:
        journeys = load_json(
            EXPORT_DIRECTORY / "journeys.json"
        )["journeys"]

        for journey in journeys:
            legs = journey["legs"]

            for current_leg, next_leg in zip(
                legs,
                legs[1:],
            ):
                self.assertEqual(
                    current_leg["destination"]["id"],
                    next_leg["origin"]["id"],
                )


if __name__ == "__main__":
    unittest.main()
