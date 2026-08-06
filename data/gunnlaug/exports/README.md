# Gunnlaug Geographic Exports

This directory contains generated geographic datasets derived from the curated SagaRoutes research data.

## `places.geojson`

A GeoJSON FeatureCollection containing only places with reviewed geometry.

Each feature includes:

- Normalized place metadata
- Spatial and identification certainty
- Textual place mentions
- Old Norse and English surface forms
- Relevant saga passages
- Editorial notes
- Coordinate-source information

## `unmapped_places.json`

Places that have been identified or mentioned in the saga but do not yet have sufficiently supported geometry.

These records are intentionally preserved rather than omitted or assigned speculative coordinates.

## Regeneration

From the repository root:

```bash
python3 src/sagaroutes/validate_places.py
python3 src/sagaroutes/export_geojson.py
