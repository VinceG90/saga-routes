# SagaRoutes Source Register

This register documents the primary texts, editions, translations, datasets, gazetteers, and secondary sources used by SagaRoutes.

The presence of a source in this register does not mean that SagaRoutes treats every statement in it as authoritative. Sources may provide textual evidence, geographic identifications, variant readings, bibliographic context, or competing scholarly interpretations.

## Primary Text 001: Old Norse

* **Work:** *Gunnlaugs saga ormstungu*
* **Language:** Old Norse
* **Textual form:** Normalized digital text
* **Attributed author:** Anonymous
* **Digital editor:** Sveinbjörn Þórðarson
* **Digital repository:** Icelandic Saga Database
* **Repository file:** `src/gunnlaugs_saga_ormstungu.on.xml`
* **Local file:** `data/gunnlaug/source/sagadb/gunnlaugs_saga_ormstungu.on.xml`
* **Format:** XML
* **Character encoding:** UTF-8
* **Recorded chapter count:** 13
* **Rights status:** Public domain, according to the Icelandic Saga Database
* **Date accessed:** 2026-08-05
* **Upstream version:** Recorded in `data/gunnlaug/source/sagadb/UPSTREAM_COMMIT.txt`
* **File checksum:** Recorded in `data/gunnlaug/source/sagadb/checksums.sha256`

### Provenance Note

This file was obtained from the public GitHub repository underlying the Icelandic Saga Database. The file contains structured metadata, chapters, paragraphs, and poetry.

The XML metadata does not identify the printed or critical edition from which this Old Norse text ultimately derives. It should therefore be treated as a normalized, openly reusable working text rather than as a diplomatic manuscript transcription or fully documented critical edition.

Before publishing detailed philological claims, SagaRoutes should compare relevant passages against a documented scholarly edition.

### Intended Use

This text will provide:

* Old Norse place-name forms
* Old Norse passages corresponding to mapped events
* Evidence for narrative sequence
* Input for place-name extraction experiments
* One side of the project’s parallel-text display

## Primary Text 002: English Translation

* **Work:** *The Saga of Gunnlaug the Worm-Tongue and Rafn the Skald*
* **Original work:** *Gunnlaugs saga ormstungu*
* **Language:** English
* **Translators:** William Morris and Eiríkr Magnússon
* **Digital editor:** Sveinbjörn Þórðarson
* **Digital repository:** Icelandic Saga Database
* **Repository file:** `src/gunnlaugs_saga_ormstungu.en.xml`
* **Local file:** `data/gunnlaug/source/sagadb/gunnlaugs_saga_ormstungu.en.xml`
* **Format:** XML
* **Character encoding:** UTF-8
* **Recorded chapter count:** 18
* **Translation date in SagaDB metadata:** 1901
* **Rights status:** Public domain, according to the Icelandic Saga Database
* **Date accessed:** 2026-08-05
* **Upstream version:** Recorded in `data/gunnlaug/source/sagadb/UPSTREAM_COMMIT.txt`
* **File checksum:** Recorded in `data/gunnlaug/source/sagadb/checksums.sha256`

### Provenance Note

The SagaDB XML identifies the translators as William Morris and Eiríkr Magnússon and identifies the Northvegr Foundation as the digital source from which SagaDB obtained the text.

Project Gutenberg separately distributes the Morris–Magnússon translation as a public-domain text in the United States and associates it with an 1875 publication. SagaDB’s XML records a translation date of 1901. SagaRoutes will preserve this metadata discrepancy until the precise edition history has been verified bibliographically.

### Intended Use

This translation will provide:

* The primary public-facing reading text for the prototype
* English place-name forms
* English passages displayed with mapped locations
* Input for English named-entity extraction experiments
* One side of the project’s parallel-text display

### Translation Note

The Morris–Magnússon translation uses deliberately archaic English and frequently Anglicizes or transforms Old Norse names. Examples include forms such as “Burg,” “Gufaros,” and “Raven.”

SagaRoutes must not assume that identical geographic entities will have identical written forms across the Old Norse and English texts.

## Parallel-Text Relationship

The Old Norse and English files represent the same narrative but do not use matching chapter structures:

* The Old Norse XML contains 13 chapters.
* The English XML contains 18 chapters.

Chapter number will therefore not serve as the project’s primary alignment key.

SagaRoutes will create its own stable passage and alignment identifiers. Alignment will initially be performed manually at the level of narrative passages and later assisted computationally.

Each alignment record should eventually contain:

* A SagaRoutes alignment identifier
* Old Norse chapter number
* Old Norse paragraph identifier
* English chapter number
* English paragraph identifier
* Alignment type
* Alignment confidence
* Editorial notes
* Reviewer
* Review date

## Rights and Reuse Policy

The two SagaDB texts used for the initial prototype are recorded by their source repository as public domain.

SagaRoutes software is licensed separately from its source texts and research data. Every later text added to the project must receive an individual rights review before its contents are committed to the public repository.

## Known Limitations

1. The Old Norse XML does not provide complete bibliographic provenance for its underlying edition.
2. The English translation is historically valuable but stylistically archaic.
3. Chapter divisions do not correspond one-to-one.
4. Digital transcription or OCR errors may remain.
5. A public-domain translation may differ significantly from current scholarly translations.
6. Neither text should be treated as a manuscript facsimile or diplomatic transcription.
7. Geographic names in translation may represent editorial interpretation rather than direct transliteration.
