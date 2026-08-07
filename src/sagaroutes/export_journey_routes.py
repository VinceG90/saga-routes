"""Export SagaRoutes journey legs as displayable GeoJSON routes.

Curated route geometry is preserved when available. When a journey leg has no
reviewed geometry but both endpoints have mapped Point geometries, SagaRoutes
may derive a straight LineString for display purposes.

Such derived geometry is explicitly marked as schematic and must not be
interpreted as a reconstruction of the historical route.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CURATED_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "curated"
)

EXPORT_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "exports"
)

PLACES_FILE = CURATED_DIRECTORY / "places.json"
JOURNEYS_FILE = CURATED_DIRECTORY / "journeys.json"
LEGS_FILE = CURATED_DIRECTORY / "journey_legs.json"

OUTPUT_FILE = (
    EXPORT_DIRECTORY / "journey_routes.geojson"
)


class ExportError(Exception):
    """Raised when route data cannot be exported safely."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    if not path.exists():
        raise ExportError(
            f"Required file does not exist: {path}"
        )

    try:
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
    except json.JSONDecodeError as exc:
        raise ExportError(
            f"Invalid JSON in {path}: "
            f"line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ExportError(
            f"Could not read {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ExportError(
            f"Top-level JSON value must be an object: {path}"
        )

    return data


def require_records(
    path: Path,
    key: str,
) -> list[dict[str, Any]]:
    """Load a required list of records."""

    data = load_json(path)
    records = data.get(key)

    if not isinstance(records, list):
        raise ExportError(
            f"{path} must contain a list named {key}"
        )

    if not all(
        isinstance(record, dict)
        for record in records
    ):
        raise ExportError(
            f"Every record in {path}:{key} "
            "must be an object"
        )

    return records


def build_index(
    records: list[dict[str, Any]],
    record_type: str,
) -> dict[str, dict[str, Any]]:
    """Index records by their IDs."""

    index: dict[str, dict[str, Any]] = {}

    for record in records:
        record_id = record.get("id")

        if (
            not isinstance(record_id, str)
            or not record_id
        ):
            raise ExportError(
                f"{record_type} record has no valid ID"
            )

        if record_id in index:
            raise ExportError(
                f"Duplicate {record_type} ID: "
                f"{record_id}"
            )

        index[record_id] = record

    return index


def point_coordinates(
    place: dict[str, Any],
) -> list[float] | None:
    """Return Point coordinates, if the place has them."""

    geometry = place.get("geometry")

    if geometry is None:
        return None

    if geometry.get("type") != "Point":
        raise ExportError(
            f"{place.get('id')}: "
            "place geometry is not a Point"
        )

    coordinates = geometry.get("coordinates")

    if (
        not isinstance(coordinates, list)
        or len(coordinates) != 2
    ):
        raise ExportError(
            f"{place.get('id')}: "
            "invalid Point coordinates"
        )

    return coordinates


def make_route_feature(
    leg: dict[str, Any],
    journey: dict[str, Any],
    origin: dict[str, Any],
    destination: dict[str, Any],
) -> dict[str, Any] | None:
    """Create a route feature when display geometry is possible."""

    curated_geometry = leg.get("geometry")

    if curated_geometry is not None:
        geometry = curated_geometry
        geometry_basis = "curated_route"
        display_type = "curated"

    else:
        origin_coordinates = point_coordinates(origin)
        destination_coordinates = point_coordinates(
            destination
        )

        if (
            origin_coordinates is None
            or destination_coordinates is None
        ):
            return None

        geometry = {
            "type": "LineString",
            "coordinates": [
                origin_coordinates,
                destination_coordinates,
            ],
        }

        geometry_basis = "schematic_endpoints"
        display_type = "schematic"

    return {
        "type": "Feature",
        "id": leg["id"],
        "geometry": geometry,
        "properties": {
            "leg_id": leg["id"],
            "journey_id": journey["id"],
            "journey_title": journey.get("title"),
            "sequence": leg.get("sequence"),
            "origin_place_id": origin["id"],
            "origin_name": origin.get(
                "preferred_name"
            ),
            "destination_place_id": destination[
                "id"
            ],
            "destination_name": destination.get(
                "preferred_name"
            ),
            "travel_mode": leg.get(
                "travel_mode"
            ),
            "route_classification": leg.get(
                "route_classification"
            ),
            "display_type": display_type,
            "geometry_basis": geometry_basis,
            "historical_route_claim": False
            if display_type == "schematic"
            else True,
            "editorial_note": leg.get(
                "editorial_note"
            ),
        },
    }


def build_export() -> dict[str, Any]:
    """Build the display-route GeoJSON FeatureCollection."""

    places = require_records(
        PLACES_FILE,
        "places",
    )

    journeys = require_records(
        JOURNEYS_FILE,
        "journeys",
    )

    legs = require_records(
        LEGS_FILE,
        "journey_legs",
    )

    place_index = build_index(
        places,
        "place",
    )

    journey_index = build_index(
        journeys,
        "journey",
    )

    features: list[dict[str, Any]] = []

    for leg in sorted(
        legs,
        key=lambda record: (
            record.get("journey_id", ""),
            record.get("sequence", 0),
        ),
    ):
        journey_id = leg.get("journey_id")

        if journey_id not in journey_index:
            raise ExportError(
                f"{leg.get('id')}: "
                f"unknown journey ID {journey_id}"
            )

        origin_id = leg.get(
            "origin_place_id"
        )

        destination_id = leg.get(
            "destination_place_id"
        )

        if origin_id not in place_index:
            raise ExportError(
                f"{leg.get('id')}: "
                f"unknown origin {origin_id}"
            )

        if destination_id not in place_index:
            raise ExportError(
                f"{leg.get('id')}: "
                f"unknown destination "
                f"{destination_id}"
            )

        feature = make_route_feature(
            leg=leg,
            journey=journey_index[journey_id],
            origin=place_index[origin_id],
            destination=place_index[
                destination_id
            ],
        )

        if feature is not None:
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "name": (
            "SagaRoutes: Gunnlaugs saga "
            "journey routes"
        ),
        "schema_version": "0.1.0",
        "work_id": "gunnlaug",
        "description": (
            "Display geometries for narrative "
            "journey legs. Features marked "
            "schematic_endpoints are straight "
            "connections between reviewed place "
            "coordinates and do not claim to "
            "represent historical routes."
        ),
        "feature_count": len(features),
        "features": features,
    }


def main() -> int:
    """Generate journey-route GeoJSON."""

    try:
        dataset = build_export()

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8",
        ) as output:
            json.dump(
                dataset,
                output,
                ensure_ascii=False,
                indent=2,
            )
            output.write("\n")

    except (
        ExportError,
        KeyError,
        TypeError,
        OSError,
    ) as exc:
        print(
            f"Journey route export failed: {exc}",
            file=sys.stderr,
        )
        return 1

    schematic_count = sum(
        1
        for feature in dataset["features"]
        if feature["properties"]["display_type"]
        == "schematic"
    )

    curated_count = (
        dataset["feature_count"]
        - schematic_count
    )

    print(
        "Wrote: "
        "data/gunnlaug/exports/"
        "journey_routes.geojson"
    )
    print(
        f"Displayable route legs: "
        f"{dataset['feature_count']}"
    )
    print(
        f"Schematic legs: {schematic_count}"
    )
    print(
        f"Curated route geometries: "
        f"{curated_count}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
