"""Validate SagaRoutes characters, journeys, and journey legs."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CURATED_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "curated"
)

CHARACTERS_FILE = CURATED_DIRECTORY / "characters.json"
JOURNEYS_FILE = CURATED_DIRECTORY / "journeys.json"
LEGS_FILE = CURATED_DIRECTORY / "journey_legs.json"
PLACES_FILE = CURATED_DIRECTORY / "places.json"
PASSAGES_FILE = CURATED_DIRECTORY / "passages.json"
ALIGNMENTS_FILE = CURATED_DIRECTORY / "alignments.json"

ALLOWED_ROUTE_CLASSIFICATIONS = {
    "explicit",
    "inferred",
    "schematic",
    "reconstructed",
}

ALLOWED_TRAVEL_MODES = {
    "horseback",
    "walking",
    "ship",
    "boat",
    "mixed",
    "unknown",
}

ALLOWED_DISPLAY_STATUSES = {
    "ready",
    "partial",
    "unmapped",
}

ALLOWED_ROUTE_CERTAINTIES = {
    "high",
    "medium",
    "low",
    "mixed",
}

ALLOWED_REVIEW_STATUSES = {
    "provisional",
    "reviewed",
    "disputed",
}


class ValidationError(Exception):
    """Raised when journey data is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    if not path.exists():
        raise ValidationError(f"Required file is missing: {path}")

    try:
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"Invalid JSON in {path}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ValidationError(f"Could not read {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(
            f"Top-level JSON value must be an object: {path}"
        )

    return data


def require_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return a required list of JSON objects."""

    records = data.get(key)

    if not isinstance(records, list):
        raise ValidationError(f"Expected a list named {key}")

    if not all(isinstance(record, dict) for record in records):
        raise ValidationError(f"Every record in {key} must be an object")

    return records


def index_records(
    records: list[dict[str, Any]],
    record_type: str,
) -> dict[str, dict[str, Any]]:
    """Validate IDs and index records by identifier."""

    identifiers = [record.get("id") for record in records]

    if any(
        not isinstance(identifier, str) or not identifier.strip()
        for identifier in identifiers
    ):
        raise ValidationError(
            f"Every {record_type} must have a nonblank string ID"
        )

    duplicates = [
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    ]

    if duplicates:
        raise ValidationError(
            f"Duplicate {record_type} IDs: "
            + ", ".join(duplicates)
        )

    return {
        record["id"]: record
        for record in records
    }


def require_known_ids(
    record_id: str,
    field_name: str,
    values: Any,
    known_ids: set[str],
) -> None:
    """Validate a nonempty list of referenced IDs."""

    if not isinstance(values, list) or not values:
        raise ValidationError(
            f"{record_id}: {field_name} must be a nonempty list"
        )

    if len(values) != len(set(values)):
        raise ValidationError(
            f"{record_id}: {field_name} contains duplicate IDs"
        )

    for value in values:
        if value not in known_ids:
            raise ValidationError(
                f"{record_id}: unknown ID in {field_name}: {value}"
            )


def validate_geometry(record_id: str, geometry: Any) -> None:
    """Validate an optional GeoJSON LineString."""

    if geometry is None:
        return

    if not isinstance(geometry, dict):
        raise ValidationError(
            f"{record_id}: geometry must be an object or null"
        )

    if geometry.get("type") != "LineString":
        raise ValidationError(
            f"{record_id}: journey geometry must be a LineString"
        )

    coordinates = geometry.get("coordinates")

    if not isinstance(coordinates, list) or len(coordinates) < 2:
        raise ValidationError(
            f"{record_id}: LineString requires at least two points"
        )

    for point in coordinates:
        if (
            not isinstance(point, list)
            or len(point) != 2
            or not all(isinstance(value, (int, float)) for value in point)
        ):
            raise ValidationError(
                f"{record_id}: invalid LineString coordinate"
            )

        longitude, latitude = point

        if not -180 <= longitude <= 180:
            raise ValidationError(
                f"{record_id}: invalid longitude: {longitude}"
            )

        if not -90 <= latitude <= 90:
            raise ValidationError(
                f"{record_id}: invalid latitude: {latitude}"
            )


def main() -> int:
    """Validate the complete journey model."""

    try:
        characters = require_list(
            load_json(CHARACTERS_FILE),
            "characters",
        )

        journeys = require_list(
            load_json(JOURNEYS_FILE),
            "journeys",
        )

        legs = require_list(
            load_json(LEGS_FILE),
            "journey_legs",
        )

        places = require_list(
            load_json(PLACES_FILE),
            "places",
        )

        passages = require_list(
            load_json(PASSAGES_FILE),
            "passages",
        )

        alignments = require_list(
            load_json(ALIGNMENTS_FILE),
            "alignments",
        )

        character_index = index_records(
            characters,
            "character",
        )

        journey_index = index_records(
            journeys,
            "journey",
        )

        leg_index = index_records(
            legs,
            "journey leg",
        )

        place_index = index_records(
            places,
            "place",
        )

        passage_index = index_records(
            passages,
            "passage",
        )

        alignment_index = index_records(
            alignments,
            "alignment",
        )

        character_ids = set(character_index)
        journey_ids = set(journey_index)
        leg_ids = set(leg_index)
        place_ids = set(place_index)
        passage_ids = set(passage_index)
        alignment_ids = set(alignment_index)

        legs_by_journey: dict[str, list[dict[str, Any]]] = (
            defaultdict(list)
        )

        for journey in journeys:
            journey_id = journey["id"]

            require_known_ids(
                journey_id,
                "traveler_ids",
                journey.get("traveler_ids"),
                character_ids,
            )

            require_known_ids(
                journey_id,
                "primary_passage_ids",
                journey.get("primary_passage_ids"),
                passage_ids,
            )

            require_known_ids(
                journey_id,
                "alignment_ids",
                journey.get("alignment_ids"),
                alignment_ids,
            )

            require_known_ids(
                journey_id,
                "journey_leg_ids",
                journey.get("journey_leg_ids"),
                leg_ids,
            )

            if (
                journey.get("route_certainty")
                not in ALLOWED_ROUTE_CERTAINTIES
            ):
                raise ValidationError(
                    f"{journey_id}: invalid route certainty"
                )

            if (
                journey.get("review_status")
                not in ALLOWED_REVIEW_STATUSES
            ):
                raise ValidationError(
                    f"{journey_id}: invalid review status"
                )

        for leg in legs:
            leg_id = leg["id"]
            journey_id = leg.get("journey_id")

            if journey_id not in journey_ids:
                raise ValidationError(
                    f"{leg_id}: unknown journey ID: {journey_id}"
                )

            legs_by_journey[journey_id].append(leg)

            if leg.get("origin_place_id") not in place_ids:
                raise ValidationError(
                    f"{leg_id}: unknown origin place"
                )

            if leg.get("destination_place_id") not in place_ids:
                raise ValidationError(
                    f"{leg_id}: unknown destination place"
                )

            if (
                leg.get("origin_place_id")
                == leg.get("destination_place_id")
            ):
                raise ValidationError(
                    f"{leg_id}: origin and destination are identical"
                )

            require_known_ids(
                leg_id,
                "participant_ids",
                leg.get("participant_ids"),
                character_ids,
            )

            require_known_ids(
                leg_id,
                "passage_ids",
                leg.get("passage_ids"),
                passage_ids,
            )

            if leg.get("alignment_id") not in alignment_ids:
                raise ValidationError(
                    f"{leg_id}: unknown alignment ID"
                )

            if (
                leg.get("travel_mode")
                not in ALLOWED_TRAVEL_MODES
            ):
                raise ValidationError(
                    f"{leg_id}: invalid travel mode"
                )

            if (
                leg.get("route_classification")
                not in ALLOWED_ROUTE_CLASSIFICATIONS
            ):
                raise ValidationError(
                    f"{leg_id}: invalid route classification"
                )

            display_status = leg.get("spatial_display_status")

            if display_status not in ALLOWED_DISPLAY_STATUSES:
                raise ValidationError(
                    f"{leg_id}: invalid spatial display status"
                )

            validate_geometry(
                leg_id,
                leg.get("geometry"),
            )

            if display_status == "ready" and leg.get("geometry") is None:
                raise ValidationError(
                    f"{leg_id}: ready legs require geometry"
                )

        for journey in journeys:
            journey_id = journey["id"]
            ordered_legs = sorted(
                legs_by_journey[journey_id],
                key=lambda record: record.get("sequence", 0),
            )

            expected_ids = journey["journey_leg_ids"]
            actual_ids = [leg["id"] for leg in ordered_legs]

            if actual_ids != expected_ids:
                raise ValidationError(
                    f"{journey_id}: journey_leg_ids do not match "
                    "the legs in sequence order"
                )

            sequences = [
                leg.get("sequence")
                for leg in ordered_legs
            ]

            expected_sequences = list(
                range(1, len(ordered_legs) + 1)
            )

            if sequences != expected_sequences:
                raise ValidationError(
                    f"{journey_id}: leg sequence must begin at 1 "
                    "and contain no gaps"
                )

            for previous_leg, next_leg in zip(
                ordered_legs,
                ordered_legs[1:],
            ):
                if (
                    previous_leg["destination_place_id"]
                    != next_leg["origin_place_id"]
                ):
                    raise ValidationError(
                        f"{journey_id}: discontinuity between "
                        f"{previous_leg['id']} and {next_leg['id']}"
                    )

    except (ValidationError, KeyError, TypeError) as exc:
        print(
            f"Journey validation failed: {exc}",
            file=sys.stderr,
        )
        return 1

    mapped_legs = sum(
        1
        for leg in legs
        if leg.get("geometry") is not None
    )

    print("Journey validation passed")
    print(f"Characters: {len(characters)}")
    print(f"Journeys: {len(journeys)}")
    print(f"Journey legs: {len(legs)}")
    print(f"Legs with geometry: {mapped_legs}")
    print(f"Legs awaiting geometry: {len(legs) - mapped_legs}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
