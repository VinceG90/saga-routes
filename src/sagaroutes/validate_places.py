"""Validate SagaRoutes places and textual place mentions."""

from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CURATED_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "curated"
)

PLACES_FILE = CURATED_DIRECTORY / "places.json"
MENTIONS_FILE = CURATED_DIRECTORY / "place_mentions.json"
PASSAGES_FILE = CURATED_DIRECTORY / "passages.json"
ALIGNMENTS_FILE = CURATED_DIRECTORY / "alignments.json"

ALLOWED_IDENTIFICATION_STATUSES = {
    "identified",
    "probable",
    "possible",
    "unresolved",
    "disputed",
}

ALLOWED_SPATIAL_CERTAINTIES = {
    "high",
    "medium",
    "low",
    "unknown",
}

ALLOWED_VISIT_STATUSES = {
    "present",
    "arrived",
    "departed",
    "visited",
    "passed_through",
    "mentioned_only",
    "uncertain",
}


class ValidationError(Exception):
    """Raised when geographic annotation data is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    """Load and return a JSON object."""

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
        raise ValidationError(
            f"Could not read {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValidationError(
            f"Top-level JSON value must be an object: {path}"
        )

    return data


def normalized_text(value: str) -> str:
    """Normalize Unicode and case for conservative substring checks."""

    return unicodedata.normalize("NFKC", value).casefold()


def validate_unique_ids(
    records: list[dict[str, Any]],
    record_type: str,
) -> None:
    """Confirm every record has a unique, nonblank ID."""

    identifiers = [record.get("id") for record in records]

    invalid = [
        identifier
        for identifier in identifiers
        if not isinstance(identifier, str) or not identifier.strip()
    ]

    if invalid:
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


def validate_geometry(
    place_id: str,
    geometry: Any,
) -> None:
    """Validate an optional GeoJSON Point geometry."""

    if geometry is None:
        return

    if not isinstance(geometry, dict):
        raise ValidationError(
            f"{place_id}: geometry must be an object or null"
        )

    if geometry.get("type") != "Point":
        raise ValidationError(
            f"{place_id}: only Point geometry is currently supported"
        )

    coordinates = geometry.get("coordinates")

    if (
        not isinstance(coordinates, list)
        or len(coordinates) != 2
        or not all(
            isinstance(value, (int, float))
            for value in coordinates
        )
    ):
        raise ValidationError(
            f"{place_id}: Point coordinates must contain "
            "[longitude, latitude]"
        )

    longitude, latitude = coordinates

    if not -180 <= longitude <= 180:
        raise ValidationError(
            f"{place_id}: invalid longitude: {longitude}"
        )

    if not -90 <= latitude <= 90:
        raise ValidationError(
            f"{place_id}: invalid latitude: {latitude}"
        )


def main() -> int:
    """Validate all current geographic annotation files."""

    try:
        places_data = load_json(PLACES_FILE)
        mentions_data = load_json(MENTIONS_FILE)
        passages_data = load_json(PASSAGES_FILE)
        alignments_data = load_json(ALIGNMENTS_FILE)

        places = places_data.get("places")
        mentions = mentions_data.get("mentions")
        passages = passages_data.get("passages")
        alignments = alignments_data.get("alignments")

        if not isinstance(places, list):
            raise ValidationError(
                "places.json must contain a places list"
            )

        if not isinstance(mentions, list):
            raise ValidationError(
                "place_mentions.json must contain a mentions list"
            )

        if not isinstance(passages, list):
            raise ValidationError(
                "passages.json must contain a passages list"
            )

        if not isinstance(alignments, list):
            raise ValidationError(
                "alignments.json must contain an alignments list"
            )

        validate_unique_ids(places, "place")
        validate_unique_ids(mentions, "place mention")

        place_index = {
            place["id"]: place
            for place in places
        }

        passage_index = {
            passage["id"]: passage
            for passage in passages
        }

        alignment_ids = {
            alignment["id"]
            for alignment in alignments
        }

        for place in places:
            place_id = place["id"]

            identification_status = place.get(
                "identification_status"
            )

            if (
                identification_status
                not in ALLOWED_IDENTIFICATION_STATUSES
            ):
                raise ValidationError(
                    f"{place_id}: invalid identification status: "
                    f"{identification_status}"
                )

            spatial_certainty = place.get(
                "spatial_certainty"
            )

            if (
                spatial_certainty
                not in ALLOWED_SPATIAL_CERTAINTIES
            ):
                raise ValidationError(
                    f"{place_id}: invalid spatial certainty: "
                    f"{spatial_certainty}"
                )

            validate_geometry(
                place_id,
                place.get("geometry"),
            )

            if (
                place.get("spatial_certainty") == "high"
                and place.get("geometry") is None
            ):
                raise ValidationError(
                    f"{place_id}: high spatial certainty "
                    "requires geometry"
                )

            note = place.get("editorial_note")

            if not isinstance(note, str) or not note.strip():
                raise ValidationError(
                    f"{place_id}: editorial_note must not be blank"
                )

        for mention in mentions:
            mention_id = mention["id"]
            place_id = mention.get("place_id")
            passage_id = mention.get("passage_id")
            alignment_id = mention.get("alignment_id")
            language_code = mention.get("language_code")
            surface_form = mention.get("surface_form")
            visit_status = mention.get("visit_status")

            if place_id not in place_index:
                raise ValidationError(
                    f"{mention_id}: unknown place ID: {place_id}"
                )

            if passage_id not in passage_index:
                raise ValidationError(
                    f"{mention_id}: unknown passage ID: {passage_id}"
                )

            passage = passage_index[passage_id]

            if passage.get("language_code") != language_code:
                raise ValidationError(
                    f"{mention_id}: mention language "
                    f"{language_code} does not match passage language "
                    f"{passage.get('language_code')}"
                )

            if (
                not isinstance(surface_form, str)
                or not surface_form.strip()
            ):
                raise ValidationError(
                    f"{mention_id}: surface_form must not be blank"
                )

            if normalized_text(surface_form) not in normalized_text(
                passage.get("text", "")
            ):
                raise ValidationError(
                    f"{mention_id}: surface form "
                    f"{surface_form!r} was not found in {passage_id}"
                )

            if visit_status not in ALLOWED_VISIT_STATUSES:
                raise ValidationError(
                    f"{mention_id}: invalid visit status: "
                    f"{visit_status}"
                )

            if (
                alignment_id is not None
                and alignment_id not in alignment_ids
            ):
                raise ValidationError(
                    f"{mention_id}: unknown alignment ID: "
                    f"{alignment_id}"
                )

    except (ValidationError, KeyError, TypeError) as exc:
        print(
            f"Place validation failed: {exc}",
            file=sys.stderr,
        )
        return 1

    mapped_places = sum(
        1
        for place in places
        if place.get("geometry") is not None
    )

    print("Place validation passed")
    print(f"Places: {len(places)}")
    print(f"Place mentions: {len(mentions)}")
    print(f"Places with geometry: {mapped_places}")
    print(f"Places awaiting coordinates: {len(places) - mapped_places}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
