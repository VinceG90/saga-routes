# SagaRoutes Static Map Prototype

This directory contains the first browser-based SagaRoutes interface.

The prototype reads generated research data from:

- `data/gunnlaug/exports/places.geojson`
- `data/gunnlaug/exports/unmapped_places.json`

## Run locally

Start an HTTP server from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
