"""Export enriched SagaRoutes journey data for the web interface."""

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

CHARACTERS_FILE = CURATED_DIRECTORY / "characters.json"
JOURNEYS_FILE = CURATED_DIRECTORY / "journeys.json"
LEGS_FILE = CURATED_DIRECTORY / "journey_legs.json"
PLACES_FILE = CURATED_DIRECTORY / "places.json"
PASSAGES_FILE = CURATED_DIRECTORY / "passages.json"

OUTPUT_FILE = EXPORT_DIRECTORY / "journeys.json"


class ExportError(Exception):
    """Raised when journey data cannot be exported safely."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    if not path.exists():
        raise ExportError(f"Required file does not exist: {path}")

    try:
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
    except json.JSONDecodeError as exc:
        raise ExportError(
            f"Invalid JSON in {path}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ExportError(f"Could not read {path}: {exc}") from exc

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

    if not all(isinstance(record, dict) for record in records):
        raise ExportError(
            f"Every item in {path}:{key} must be an object"
        )

    return records


def build_index(
    records: list[dict[str, Any]],
    record_type: str,
) -> dict[str, dict[str, Any]]:
    """Create an ID-based record index."""

    index: dict[str, dict[str, Any]] = {}

    for record in records:
        record_id = record.get("id")

        if not isinstance(record_id, str) or not record_id:
            raise ExportError(
                f"{record_type} record has no valid ID"
            )

        if record_id in index:
            raise ExportError(
                f"Duplicate {record_type} ID: {record_id}"
            )

        index[record_id] = record

    return index


def get_record(
    index: dict[str, dict[str, Any]],
    record_id: Any,
    record_type: str,
) -> dict[str, Any]:
    """Return a referenced record or raise a helpful error."""

    if not isinstance(record_id, str) or record_id not in index:
        raise ExportError(
            f"Unknown {record_type} ID: {record_id}"
        )

    return index[record_id]


def export_character(
    character: dict[str, Any],
) -> dict[str, Any]:
    """Return selected public-facing character fields."""

    return {
        "id": character.get("id"),
        "preferred_name": character.get("preferred_name"),
        "alternate_names": character.get("alternate_names", []),
        "role_in_work": character.get("role_in_work"),
        "editorial_note": character.get("editorial_note"),
    }


def export_place(
    place: dict[str, Any],
) -> dict[str, Any]:
    """Return selected place fields for an itinerary endpoint."""

    geometry = place.get("geometry")

    return {
        "id": place.get("id"),
        "preferred_name": place.get("preferred_name"),
        "alternate_names": place.get("alternate_names", []),
        "feature_type": place.get("feature_type"),
        "identification_status": place.get(
            "identification_status"
        ),
        "spatial_certainty": place.get("spatial_certainty"),
        "has_geometry": geometry is not None,
        "geometry": geometry,
    }


def export_passage(
    passage: dict[str, Any],
) -> dict[str, Any]:
    """Return selected textual evidence fields."""

    return {
        "id": passage.get("id"),
        "language_code": passage.get("language_code"),
        "language": passage.get("language"),
        "chapter_number": passage.get("chapter_number"),
        "chapter_title": passage.get("chapter_title"),
        "passage_type": passage.get("passage_type"),
        "sequence_in_document": passage.get(
            "sequence_in_document"
        ),
        "text": passage.get("text"),
    }


def build_export() -> dict[str, Any]:
    """Build the complete enriched journey export."""

    characters = require_records(
        CHARACTERS_FILE,
        "characters",
    )

    journeys = require_records(
        JOURNEYS_FILE,
        "journeys",
    )

    legs = require_records(
        LEGS_FILE,
        "journey_legs",
    )

    places = require_records(
        PLACES_FILE,
        "places",
    )

    passages = require_records(
        PASSAGES_FILE,
        "passages",
    )

    character_index = build_index(
        characters,
        "character",
    )

    journey_index = build_index(
        journeys,
        "journey",
    )

    leg_index = build_index(
        legs,
        "journey leg",
    )

    place_index = build_index(
        places,
        "place",
    )

    passage_index = build_index(
        passages,
        "passage",
    )

    exported_journeys: list[dict[str, Any]] = []

    sorted_journeys = sorted(
        journeys,
        key=lambda record: (
            record.get("narrative_order", 0),
            record.get("id", ""),
        ),
    )

    for journey in sorted_journeys:
        journey_id = journey["id"]

        traveler_ids = journey.get("traveler_ids", [])
        passage_ids = journey.get("primary_passage_ids", [])
        leg_ids = journey.get("journey_leg_ids", [])

        travelers = [
            export_character(
                get_record(
                    character_index,
                    traveler_id,
                    "character",
                )
            )
            for traveler_id in traveler_ids
        ]

        primary_passages = [
            export_passage(
                get_record(
                    passage_index,
                    passage_id,
                    "passage",
                )
            )
            for passage_id in passage_ids
        ]

        exported_legs: list[dict[str, Any]] = []

        for leg_id in leg_ids:
            leg = get_record(
                leg_index,
                leg_id,
                "journey leg",
            )

            if leg.get("journey_id") != journey_id:
                raise ExportError(
                    f"{leg_id} does not belong to {journey_id}"
                )

            origin = get_record(
                place_index,
                leg.get("origin_place_id"),
                "place",
            )

            destination = get_record(
                place_index,
                leg.get("destination_place_id"),
                "place",
            )

            participants = [
                export_character(
                    get_record(
                        character_index,
                        participant_id,
                        "character",
                    )
                )
                for participant_id in leg.get(
                    "participant_ids",
                    [],
                )
            ]

            leg_passages = [
                export_passage(
                    get_record(
                        passage_index,
                        passage_id,
                        "passage",
                    )
                )
                for passage_id in leg.get("passage_ids", [])
            ]

            exported_legs.append(
                {
                    "id": leg.get("id"),
                    "sequence": leg.get("sequence"),
                    "origin": export_place(origin),
                    "destination": export_place(destination),
                    "participants": participants,
                    "passages": leg_passages,
                    "alignment_id": leg.get("alignment_id"),
                    "travel_mode": leg.get("travel_mode"),
                    "route_classification": leg.get(
                        "route_classification"
                    ),
                    "spatial_display_status": leg.get(
                        "spatial_display_status"
                    ),
                    "has_geometry": leg.get("geometry") is not None,
                    "geometry": leg.get("geometry"),
                    "editorial_note": leg.get("editorial_note"),
                }
            )

        exported_journeys.append(
            {
                "id": journey_id,
                "title": journey.get("title"),
                "narrative_order": journey.get(
                    "narrative_order"
                ),
                "purpose": journey.get("purpose"),
                "route_certainty": journey.get(
                    "route_certainty"
                ),
                "review_status": journey.get("review_status"),
                "alignment_ids": journey.get(
                    "alignment_ids",
                    [],
                ),
                "travelers": travelers,
                "primary_passages": primary_passages,
                "leg_count": len(exported_legs),
                "mapped_leg_count": sum(
                    1
                    for leg in exported_legs
                    if leg["has_geometry"]
                ),
                "legs": exported_legs,
                "editorial_note": journey.get(
                    "editorial_note"
                ),
            }
        )

    return {
        "schema_version": "0.1.0",
        "work_id": "gunnlaug",
        "description": (
            "Enriched narrative journeys and ordered journey legs "
            "for the SagaRoutes web interface."
        ),
        "journey_count": len(exported_journeys),
        "journeys": exported_journeys,
    }


def write_export(dataset: dict[str, Any]) -> None:
    """Write the journey export as formatted UTF-8 JSON."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        json.dump(
            dataset,
            output,
            ensure_ascii=False,
            indent=2,
        )
        output.write("\n")


def main() -> int:
    """Generate the enriched journey export."""

    try:
        dataset = build_export()
        write_export(dataset)
    except (ExportError, KeyError, TypeError, OSError) as exc:
        print(f"Journey export failed: {exc}", file=sys.stderr)
        return 1

    leg_count = sum(
        journey["leg_count"]
        for journey in dataset["journeys"]
    )

    mapped_leg_count = sum(
        journey["mapped_leg_count"]
        for journey in dataset["journeys"]
    )

    print(
        "Wrote: "
        "data/gunnlaug/exports/journeys.json"
    )
    print(f"Journeys: {dataset['journey_count']}")
    print(f"Journey legs: {leg_count}")
    print(f"Legs with geometry: {mapped_leg_count}")
    print(
        f"Legs awaiting geometry: "
        f"{leg_count - mapped_leg_count}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
