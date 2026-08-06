"""Normalize SagaDB XML texts into stable SagaRoutes passage records.

This parser does not modify the upstream XML files. It creates a deterministic
JSON representation that later stages can use for passage alignment, place-name
annotation, and geographic analysis.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "source" / "sagadb"
)

OUTPUT_FILE = (
    REPOSITORY_ROOT / "data" / "gunnlaug" / "curated" / "passages.json"
)

WORK_ID = "gunnlaug"

SOURCES = {
    "on": SOURCE_DIRECTORY / "gunnlaugs_saga_ormstungu.on.xml",
    "en": SOURCE_DIRECTORY / "gunnlaugs_saga_ormstungu.en.xml",
}


def local_name(tag: str) -> str:
    """Return an XML tag without a namespace prefix."""

    return tag.rsplit("}", 1)[-1]


def normalize_whitespace(text: str) -> str:
    """Collapse ordinary whitespace while preserving readable text."""

    return re.sub(r"\s+", " ", text).strip()


def element_text(element: ET.Element) -> str:
    """Extract and normalize all text contained within an XML element."""

    return normalize_whitespace("".join(element.itertext()))


def find_direct_child(
    element: ET.Element,
    child_name: str,
) -> ET.Element | None:
    """Find a direct child by its local XML tag name."""

    for child in element:
        if local_name(child.tag) == child_name:
            return child

    return None


def sha256_file(path: Path) -> str:
    """Calculate the SHA-256 checksum of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as source_file:
        for block in iter(lambda: source_file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def repository_path(path: Path) -> str:
    """Return a path relative to the repository root."""

    return path.relative_to(REPOSITORY_ROOT).as_posix()


def read_upstream_commit() -> str | None:
    """Read the recorded SagaDB commit, if present."""

    commit_file = SOURCE_DIRECTORY / "UPSTREAM_COMMIT.txt"

    if not commit_file.exists():
        return None

    commit = commit_file.read_text(encoding="utf-8").strip()
    return commit or None


def metadata_to_dict(metadata: ET.Element) -> dict[str, str]:
    """Convert the XML metadata element into a plain dictionary."""

    result: dict[str, str] = {}

    for child in metadata:
        result[local_name(child.tag)] = element_text(child)

    return result


def parse_source(
    language_code: str,
    source_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse one SagaDB XML source into source, chapter, and passage records."""

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file does not exist: {source_path}"
        )

    try:
        tree = ET.parse(source_path)
    except ET.ParseError as exc:
        raise ValueError(
            f"Invalid XML in {source_path}: {exc}"
        ) from exc

    root = tree.getroot()

    metadata_element = find_direct_child(root, "metadata")
    content_element = find_direct_child(root, "content")

    if metadata_element is None:
        raise ValueError(f"No metadata element found in {source_path}")

    if content_element is None:
        raise ValueError(f"No content element found in {source_path}")

    metadata = metadata_to_dict(metadata_element)

    chapters: list[dict[str, Any]] = []
    passages: list[dict[str, Any]] = []

    document_sequence = 0

    chapter_elements = [
        child
        for child in content_element
        if local_name(child.tag) == "chapter"
    ]

    for chapter_position, chapter_element in enumerate(
        chapter_elements,
        start=1,
    ):
        source_chapter_number = chapter_element.get(
            "number",
            str(chapter_position),
        )

        try:
            chapter_number = int(source_chapter_number)
        except ValueError:
            chapter_number = chapter_position

        chapter_id = (
            f"{WORK_ID}-{language_code}-c{chapter_number:02d}"
        )

        chapter_title = normalize_whitespace(
            chapter_element.get("title", "")
        )

        chapter_passage_ids: list[str] = []
        sequence_in_chapter = 0
        prose_number = 0
        poetry_number = 0

        # Iterate through direct children so prose and poetry remain
        # in their original narrative order.
        for child in chapter_element:
            element_type = local_name(child.tag)

            if element_type == "paragraph":
                text = element_text(child)

                if not text:
                    continue

                prose_number += 1
                passage_id = (
                    f"{chapter_id}-p{prose_number:03d}"
                )
                passage_type = "prose"
                lines: list[str] | None = None

            elif element_type == "poetry":
                lines = [
                    element_text(line)
                    for line in child
                    if local_name(line.tag) == "line"
                    and element_text(line)
                ]

                text = "\n".join(lines)

                if not text:
                    continue

                poetry_number += 1
                passage_id = (
                    f"{chapter_id}-v{poetry_number:03d}"
                )
                passage_type = "poetry"

            else:
                # Unknown chapter-level elements are skipped for now.
                continue

            sequence_in_chapter += 1
            document_sequence += 1
            chapter_passage_ids.append(passage_id)

            passage: dict[str, Any] = {
                "id": passage_id,
                "work_id": WORK_ID,
                "language_code": language_code,
                "language": metadata.get("language"),
                "chapter_id": chapter_id,
                "chapter_number": chapter_number,
                "source_chapter_number": source_chapter_number,
                "chapter_title": chapter_title,
                "passage_type": passage_type,
                "sequence_in_chapter": sequence_in_chapter,
                "sequence_in_document": document_sequence,
                "text": text,
                "source_file": repository_path(source_path),
                "source_element": element_type,
            }

            if lines is not None:
                passage["lines"] = lines

            passages.append(passage)

        chapters.append(
            {
                "id": chapter_id,
                "work_id": WORK_ID,
                "language_code": language_code,
                "chapter_number": chapter_number,
                "source_chapter_number": source_chapter_number,
                "title": chapter_title,
                "sequence_in_document": chapter_position,
                "passage_count": len(chapter_passage_ids),
                "passage_ids": chapter_passage_ids,
            }
        )

    source_record: dict[str, Any] = {
        "work_id": WORK_ID,
        "language_code": language_code,
        "language": metadata.get("language"),
        "title": metadata.get("title"),
        "basename": metadata.get("basename"),
        "editor": metadata.get("editor"),
        "creator": metadata.get("creator"),
        "source_file": repository_path(source_path),
        "sha256": sha256_file(source_path),
        "chapter_count": len(chapters),
        "passage_count": len(passages),
        "upstream_metadata": metadata,
    }

    return source_record, chapters, passages


def build_dataset() -> dict[str, Any]:
    """Build the complete parallel-text dataset."""

    source_records: list[dict[str, Any]] = []
    chapter_records: list[dict[str, Any]] = []
    passage_records: list[dict[str, Any]] = []

    for language_code, source_path in SOURCES.items():
        source, chapters, passages = parse_source(
            language_code,
            source_path,
        )

        source_records.append(source)
        chapter_records.extend(chapters)
        passage_records.extend(passages)

    passage_ids = [passage["id"] for passage in passage_records]

    if len(passage_ids) != len(set(passage_ids)):
        raise ValueError("Duplicate passage IDs were generated")

    return {
        "schema_version": "0.1.0",
        "work": {
            "id": WORK_ID,
            "original_title": "Gunnlaugs saga ormstungu",
            "project_name": "SagaRoutes",
        },
        "upstream": {
            "repository": "sveinbjornt/sagadb.org",
            "commit": read_upstream_commit(),
        },
        "sources": source_records,
        "chapters": chapter_records,
        "passages": passage_records,
    }


def write_dataset(dataset: dict[str, Any]) -> None:
    """Write the normalized dataset as UTF-8 JSON."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        json.dump(
            dataset,
            output,
            ensure_ascii=False,
            indent=2,
        )
        output.write("\n")


def main() -> int:
    """Run the parser and report what was generated."""

    try:
        dataset = build_dataset()
        write_dataset(dataset)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote: {repository_path(OUTPUT_FILE)}")

    for source in dataset["sources"]:
        print(
            f"{source['language_code']}: "
            f"{source['chapter_count']} chapters, "
            f"{source['passage_count']} passages"
        )

    print(f"Total passages: {len(dataset['passages'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
