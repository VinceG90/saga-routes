# SagaRoutes Project Charter

## Project Title

**SagaRoutes: Mapping Narrative Movement in Medieval Icelandic Sagas**

## Project Summary

SagaRoutes is a digital humanities project for identifying, organizing, and visualizing geographic movement in historical narrative texts. The initial prototype will focus on *The Saga of Gunnlaug Serpent-Tongue* and will reconstruct the movements of major characters across Iceland, Scandinavia, the British Isles, and the wider North Atlantic world.

Rather than presenting mapped routes as straightforward geographic facts, SagaRoutes will distinguish between locations and journeys that are explicitly stated in the text, inferred from narrative sequence, identified through scholarship, or reconstructed computationally. The project will preserve the textual and scholarly evidence behind each mapped claim.

The long-term goal is to create a reusable, open-source system through which researchers, students, and educators can upload or select a historical text, identify geographic references, review suggested place matches, and generate an interactive map of locations and narrative journeys.

## Central Research Question

How can computational text analysis, historical gazetteers, geographic information systems, and scholarly annotation be combined to reconstruct narrative travel while preserving uncertainty, textual provenance, and competing geographic interpretations?

## Supporting Questions

1. How should a digital system distinguish between a place mentioned in a text and a place physically visited by a character?

2. How can historical, translated, variant, and ambiguous place-names be reconciled with modern geographic coordinates?

3. How should a map represent journeys when the text provides only partial information about routes, chronology, or intermediate stops?

4. How can computational extraction assist scholars without concealing editorial judgment or presenting uncertain interpretations as objective facts?

5. How can mapped narrative data be structured so that it remains reusable, interoperable, citable, and suitable for future comparative research?

## Initial Case Study

The first prototype will use *The Saga of Gunnlaug Serpent-Tongue* as its demonstration text.

The saga is suitable because it contains:

* Travel within Iceland
* Voyages between Iceland and continental Europe
* Visits to royal and political centers
* Multiple traveling characters
* Geographic references with different levels of certainty
* A narrative in which movement, exile, reputation, courtship, and conflict are closely connected

The prototype will begin with a manually curated dataset rather than fully automated extraction. This dataset will serve as a scholarly reference set against which later computational methods can be evaluated.

## Prototype Goals

The initial prototype will:

* Record named geographic locations appearing in the saga
* Associate each place reference with its textual passage
* Distinguish textual place mentions from normalized geographic entities
* Record historical and modern place-names
* Assign coordinates where an identification is reasonably supportable
* Record uncertainty and alternative identifications
* Organize locations according to narrative sequence
* Record journeys made by major characters
* Distinguish explicit, inferred, schematic, and reconstructed routes
* Display locations and journeys on an interactive web map
* Link mapped items to textual passages and supporting scholarly resources
* Export curated data as CSV and GeoJSON
* Provide documentation enabling the software to be run locally

## Prototype Deliverable

The first public demonstration will be an interactive map containing at least six curated locations and several connected journey stages from *The Saga of Gunnlaug Serpent-Tongue*.

Each mapped location should include:

* Name as it appears in the selected text
* Normalized historical name
* Modern name, where applicable
* Latitude and longitude
* Chapter or section
* Relevant textual passage
* Mention type
* Identification confidence
* Editorial notes
* Supporting sources
* External authority identifiers, where available

Each journey stage should include:

* Traveler
* Origin
* Destination
* Narrative sequence
* Travel mode
* Supporting passage
* Route classification
* Confidence level
* Editorial explanation

## Route Classifications

SagaRoutes will use the following preliminary route classifications:

### Explicit

The text directly states that a character traveled from one identified place to another, possibly naming intermediate stops.

### Inferred

The origin and destination can be inferred from narrative sequence, but the journey is not fully described.

### Schematic

The text indicates movement between broad locations, but the historical course cannot be reconstructed with sufficient precision. The map connection is illustrative rather than geographic.

### Reconstructed

A possible route has been proposed using geographic, historical, environmental, or computational evidence beyond the explicit wording of the text.

Reconstructed routes must be clearly labeled and must identify the evidence and assumptions used.

## Principles

### Transparency

Every mapped claim should be traceable to textual or scholarly evidence.

### Uncertainty

Ambiguity should be represented rather than silently resolved.

### Human Review

Computational suggestions must remain subject to scholarly review and correction.

### Reproducibility

Project data, documentation, and software should be organized so that another researcher can understand and reproduce the result.

### Interoperability

Where practical, data should use established formats and identifiers, including GeoJSON, CSV, persistent place identifiers, bibliographic identifiers, and linked-data conventions.

### Accessibility

The interface should be usable by researchers, students, instructors, and interested members of the public.

### Sustainability

The software should avoid unnecessary dependence on proprietary services and should be capable of running on modest institutional or personal infrastructure.

## Intended Audiences

SagaRoutes is intended for:

* Scholars of Old Norse literature
* Medievalists
* Digital humanities researchers
* Historical geographers
* Librarians and information scientists
* Instructors teaching saga literature
* Students studying medieval travel and geography
* Researchers working with other place-rich narrative traditions

## Out of Scope for the First Prototype

The first prototype will not attempt to:

* Automatically interpret every geographic reference in arbitrary PDFs
* Produce historically certain sea routes where evidence is incomplete
* Reconstruct exact medieval weather conditions
* Replace scholarly geographic interpretation
* Provide a comprehensive edition or translation of the saga
* Include every person, place, event, manuscript, or scholarly source
* Support unrestricted public uploads
* Use generative AI to make unreviewed geographic claims
* Present modern routing results as authentic medieval travel routes

These features may be explored in later phases after the curated data model and interpretive methodology have been established.

## Technical Direction

The project is expected to use:

* Python
* Django
* PostgreSQL and PostGIS
* MapLibre GL JS
* GeoJSON
* Docker Compose
* Git and GitHub
* A hybrid of rule-based text processing, named-entity recognition, gazetteer reconciliation, and human review

The public demonstration will eventually be hosted on a headless Debian server.

## Scholarly Contribution

SagaRoutes will contribute more than a visualization of saga place-names. It will investigate how narrative movement can be represented as structured scholarly data while preserving the distinction between textual evidence, editorial interpretation, geographic identification, and computational reconstruction.

The project will also explore how library and information science practices—including authority control, metadata design, provenance, linked data, and sustainable digital infrastructure—can support computational literary scholarship.

## Success Criteria for the Initial Phase

The initial phase will be considered successful when:

1. A documented data model has been created.
2. A source text and edition have been selected and documented.
3. At least six locations have been manually curated.
4. At least one major character journey has been represented as ordered journey stages.
5. Every location and route is linked to supporting textual evidence.
6. Uncertainty can be expressed in the data.
7. The dataset can be exported as valid GeoJSON and CSV.
8. The demonstration map can run locally.
9. Installation and methodology documentation are available.
10. The project can be publicly cited through its GitHub repository.

## Immediate Next Steps

1. Select and document the initial source text.
2. Define the data model for works, passages, place mentions, places, journey legs, people, and sources.
3. Identify the first six locations in the saga.
4. Record textual passages and preliminary geographic identifications.
5. Create a small manually curated JSON dataset.
6. Build a minimal map that reads the curated data.
