"""Export curated SagaRoutes geographic data as GeoJSON.

Mapped places are written to a GeoJSON FeatureCollection. Places without
geometry are retained in a separate JSON file so unresolved geographic
evidence is not silently discarded.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
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
MENTIONS_FILE = CURATED_DIRECTORY / "place_mentions.json"
PASSAGES_FILE = CURATED_DIRECTORY / "passages.json"

GEOJSON_FILE = EXPORT_DIRECTORY / "places.geojson"
UNMAPPED_FILE = EXPORT_DIRECTORY / "unmapped_places.json"


class ExportError(Exception):
    """Raised when source data cannot be exported safely."""


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


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write formatted UTF-8 JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as output:
        json.dump(
            data,
            output,
            ensure_ascii=False,
            indent=2,
        )
        output.write("\n")


def repository_path(path: Path) -> str:
    """Return a path relative to the repository root."""

    return path.relative_to(REPOSITORY_ROOT).as_posix()


def enrich_mention(
    mention: dict[str, Any],
    passage_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Combine a place mention with selected passage metadata."""

    passage_id = mention.get("passage_id")

    if passage_id not in passage_index:
        raise ExportError(
            f"{mention.get('id')}: unknown passage ID: {passage_id}"
        )

    passage = passage_index[passage_id]

    return {
        "mention_id": mention.get("id"),
        "passage_id": passage_id,
        "alignment_id": mention.get("alignment_id"),
        "language_code": mention.get("language_code"),
        "surface_form": mention.get("surface_form"),
        "mention_role": mention.get("mention_role"),
        "visit_status": mention.get("visit_status"),
        "character_names": mention.get("character_names", []),
        "chapter_number": passage.get("chapter_number"),
        "chapter_title": passage.get("chapter_title"),
        "passage_type": passage.get("passage_type"),
        "sequence_in_document": passage.get(
            "sequence_in_document"
        ),
        "text": passage.get("text"),
        "editorial_note": mention.get("editorial_note"),
    }


def mention_sort_key(
    mention: dict[str, Any],
) -> tuple[str, int, str]:
    """Provide deterministic ordering for exported mentions."""

    language = str(mention.get("language_code", ""))
    sequence = mention.get("sequence_in_document")

    if not isinstance(sequence, int):
        sequence = 0

    mention_id = str(mention.get("mention_id", ""))

    return language, sequence, mention_id


def make_feature(
    place: dict[str, Any],
    mentions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Convert one mapped place into a GeoJSON Feature."""

    geometry = place.get("geometry")

    if geometry is None:
        raise ExportError(
            f"{place.get('id')}: cannot create a feature "
            "without geometry"
        )

    properties = {
        "place_id": place.get("id"),
        "preferred_name": place.get("preferred_name"),
        "alternate_names": place.get("alternate_names", []),
        "feature_type": place.get("feature_type"),
        "associated_site_type": place.get(
            "associated_site_type"
        ),
        "country_code": place.get("country_code"),
        "broader_region": place.get("broader_region"),
        "identification_status": place.get(
            "identification_status"
        ),
        "spatial_certainty": place.get("spatial_certainty"),
        "coordinate_source_id": place.get(
            "coordinate_source_id"
        ),
        "authority_ids": place.get("authority_ids", {}),
        "editorial_note": place.get("editorial_note"),
        "mention_count": len(mentions),
        "mentions": sorted(
            mentions,
            key=mention_sort_key,
        ),
    }

    return {
        "type": "Feature",
        "id": place.get("id"),
        "geometry": geometry,
        "properties": properties,
    }


def build_exports() -> tuple[dict[str, Any], dict[str, Any]]:
    """Build mapped and unmapped export datasets."""

    places_data = load_json(PLACES_FILE)
    mentions_data = load_json(MENTIONS_FILE)
    passages_data = load_json(PASSAGES_FILE)

    places = places_data.get("places")
    mentions = mentions_data.get("mentions")
    passages = passages_data.get("passages")

    if not isinstance(places, list):
        raise ExportError(
            "places.json must contain a places list"
        )

    if not isinstance(mentions, list):
        raise ExportError(
            "place_mentions.json must contain a mentions list"
        )

    if not isinstance(passages, list):
        raise ExportError(
            "passages.json must contain a passages list"
        )

    passage_index = {
        passage["id"]: passage
        for passage in passages
    }

    mentions_by_place: dict[str, list[dict[str, Any]]] = (
        defaultdict(list)
    )

    for mention in mentions:
        place_id = mention.get("place_id")

        if not isinstance(place_id, str):
            raise ExportError(
                f"{mention.get('id')}: missing place ID"
            )

        mentions_by_place[place_id].append(
            enrich_mention(
                mention,
                passage_index,
            )
        )

    mapped_features: list[dict[str, Any]] = []
    unmapped_places: list[dict[str, Any]] = []

    for place in sorted(
        places,
        key=lambda record: str(record.get("id", "")),
    ):
        place_id = place.get("id")
        place_mentions = mentions_by_place.get(
            str(place_id),
            [],
        )

        if place.get("geometry") is not None:
            mapped_features.append(
                make_feature(
                    place,
                    place_mentions,
                )
            )
        else:
            unmapped_record = dict(place)
            unmapped_record["mention_count"] = len(
                place_mentions
            )
            unmapped_record["mentions"] = sorted(
                place_mentions,
                key=mention_sort_key,
            )
            unmapped_places.append(unmapped_record)

    geojson = {
        "type": "FeatureCollection",
        "name": "SagaRoutes: Gunnlaugs saga places",
        "schema_version": "0.1.0",
        "work_id": "gunnlaug",
        "source_files": {
            "places": repository_path(PLACES_FILE),
            "place_mentions": repository_path(
                MENTIONS_FILE
            ),
            "passages": repository_path(PASSAGES_FILE),
        },
        "feature_count": len(mapped_features),
        "features": mapped_features,
    }

    unmapped = {
        "schema_version": "0.1.0",
        "work_id": "gunnlaug",
        "description": (
            "Saga places retained without map geometry because "
            "their precise historic locations remain unresolved "
            "or insufficiently supported."
        ),
        "place_count": len(unmapped_places),
        "places": unmapped_places,
    }

    return geojson, unmapped


def main() -> int:
    """Generate all geographic export files."""

    try:
        geojson, unmapped = build_exports()

        write_json(GEOJSON_FILE, geojson)
        write_json(UNMAPPED_FILE, unmapped)

    except (ExportError, KeyError, TypeError, OSError) as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote: {repository_path(GEOJSON_FILE)}")
    print(f"Mapped features: {geojson['feature_count']}")
    print(f"Wrote: {repository_path(UNMAPPED_FILE)}")
    print(f"Unmapped places: {unmapped['place_count']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
