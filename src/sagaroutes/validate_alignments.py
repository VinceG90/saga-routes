"""Validate SagaRoutes parallel-text alignment records."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

PASSAGES_FILE = (
    REPOSITORY_ROOT
    / "data"
    / "gunnlaug"
    / "curated"
    / "passages.json"
)

ALIGNMENTS_FILE = (
    REPOSITORY_ROOT
    / "data"
    / "gunnlaug"
    / "curated"
    / "alignments.json"
)

ALLOWED_CARDINALITIES = {
    "one_to_one",
    "one_to_many",
    "many_to_one",
    "many_to_many",
}

ALLOWED_COVERAGE_VALUES = {
    "equivalent",
    "substantially_equivalent",
    "partial",
    "summary",
    "expanded",
    "uncertain",
}

ALLOWED_CONFIDENCE_VALUES = {
    "high",
    "medium",
    "low",
}

ALLOWED_REVIEW_STATUSES = {
    "provisional",
    "reviewed",
    "disputed",
}


class ValidationError(Exception):
    """Raised when alignment data violates the SagaRoutes schema."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    if not path.exists():
        raise ValidationError(f"Required file does not exist: {path}")

    try:
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"Invalid JSON in {path}: line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ValidationError(f"Could not read {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"Top-level JSON value must be an object: {path}")

    return data


def expected_cardinality(
    old_norse_count: int,
    english_count: int,
) -> str:
    """Calculate the cardinality implied by the passage arrays."""

    if old_norse_count == 1 and english_count == 1:
        return "one_to_one"

    if old_norse_count == 1 and english_count > 1:
        return "one_to_many"

    if old_norse_count > 1 and english_count == 1:
        return "many_to_one"

    return "many_to_many"


def validate_alignment(
    alignment: dict[str, Any],
    passage_languages: dict[str, str],
) -> None:
    """Validate one alignment record."""

    alignment_id = alignment.get("id")

    if not isinstance(alignment_id, str) or not alignment_id.strip():
        raise ValidationError("Every alignment must have a nonblank string ID")

    old_norse_ids = alignment.get("old_norse_passage_ids")
    english_ids = alignment.get("english_passage_ids")

    if not isinstance(old_norse_ids, list) or not old_norse_ids:
        raise ValidationError(
            f"{alignment_id}: old_norse_passage_ids must be a nonempty list"
        )

    if not isinstance(english_ids, list) or not english_ids:
        raise ValidationError(
            f"{alignment_id}: english_passage_ids must be a nonempty list"
        )

    if len(old_norse_ids) != len(set(old_norse_ids)):
        raise ValidationError(
            f"{alignment_id}: duplicate Old Norse passage ID"
        )

    if len(english_ids) != len(set(english_ids)):
        raise ValidationError(
            f"{alignment_id}: duplicate English passage ID"
        )

    for passage_id in old_norse_ids:
        if passage_id not in passage_languages:
            raise ValidationError(
                f"{alignment_id}: unknown passage ID: {passage_id}"
            )

        if passage_languages[passage_id] != "on":
            raise ValidationError(
                f"{alignment_id}: {passage_id} is not Old Norse"
            )

    for passage_id in english_ids:
        if passage_id not in passage_languages:
            raise ValidationError(
                f"{alignment_id}: unknown passage ID: {passage_id}"
            )

        if passage_languages[passage_id] != "en":
            raise ValidationError(
                f"{alignment_id}: {passage_id} is not English"
            )

    cardinality = alignment.get("cardinality")

    if cardinality not in ALLOWED_CARDINALITIES:
        raise ValidationError(
            f"{alignment_id}: invalid cardinality: {cardinality}"
        )

    implied_cardinality = expected_cardinality(
        len(old_norse_ids),
        len(english_ids),
    )

    if cardinality != implied_cardinality:
        raise ValidationError(
            f"{alignment_id}: cardinality is {cardinality}, "
            f"but passage counts imply {implied_cardinality}"
        )

    coverage = alignment.get("coverage")

    if coverage not in ALLOWED_COVERAGE_VALUES:
        raise ValidationError(
            f"{alignment_id}: invalid coverage value: {coverage}"
        )

    confidence = alignment.get("confidence")

    if confidence not in ALLOWED_CONFIDENCE_VALUES:
        raise ValidationError(
            f"{alignment_id}: invalid confidence value: {confidence}"
        )

    review_status = alignment.get("review_status")

    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise ValidationError(
            f"{alignment_id}: invalid review status: {review_status}"
        )

    editorial_note = alignment.get("editorial_note")

    if not isinstance(editorial_note, str) or not editorial_note.strip():
        raise ValidationError(
            f"{alignment_id}: editorial_note must not be blank"
        )


def main() -> int:
    """Validate the complete alignment dataset."""

    try:
        passage_data = load_json(PASSAGES_FILE)
        alignment_data = load_json(ALIGNMENTS_FILE)

        passages = passage_data.get("passages")
        alignments = alignment_data.get("alignments")

        if not isinstance(passages, list):
            raise ValidationError(
                "passages.json must contain a passages list"
            )

        if not isinstance(alignments, list):
            raise ValidationError(
                "alignments.json must contain an alignments list"
            )

        passage_languages = {
            passage["id"]: passage["language_code"]
            for passage in passages
        }

        alignment_ids = [
            alignment.get("id")
            for alignment in alignments
        ]

        duplicate_ids = [
            alignment_id
            for alignment_id, count
            in Counter(alignment_ids).items()
            if count > 1
        ]

        if duplicate_ids:
            raise ValidationError(
                "Duplicate alignment IDs: "
                + ", ".join(str(value) for value in duplicate_ids)
            )

        for alignment in alignments:
            if not isinstance(alignment, dict):
                raise ValidationError(
                    "Every alignment record must be a JSON object"
                )

            validate_alignment(
                alignment,
                passage_languages,
            )

    except (ValidationError, KeyError, TypeError) as exc:
        print(f"Alignment validation failed: {exc}", file=sys.stderr)
        return 1

    aligned_old_norse = {
        passage_id
        for alignment in alignments
        for passage_id in alignment["old_norse_passage_ids"]
    }

    aligned_english = {
        passage_id
        for alignment in alignments
        for passage_id in alignment["english_passage_ids"]
    }

    print("Alignment validation passed")
    print(f"Alignment records: {len(alignments)}")
    print(f"Aligned Old Norse passages: {len(aligned_old_norse)}")
    print(f"Aligned English passages: {len(aligned_english)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
