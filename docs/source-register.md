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


## Geographic Source 001: Borg á Mýrum

- **Source ID:** `geo-source-west-is-borg`
- **Resource:** Borg á Mýrum
- **Publisher:** West Iceland
- **Resource type:** Regional cultural and visitor-information site
- **URL:** https://www.west.is/is/thjonusta/saga-og-menning/borg-a-myrum
- **Date accessed:** 2026-08-06
- **Coordinates supplied by source:** N 64° 33' 42.415", W 21° 54' 54.523"
- **Decimal coordinates used by SagaRoutes:** 64.561782, -21.915145
- **Intended use:** Location of the extant Borg á Mýrum farm and church site
- **Reliability note:** Suitable for locating the modern historic site. These coordinates do not establish the precise location or extent of medieval buildings.

## Geographic Reference 002: Icelandic Saga Map

- **Source ID:** `geo-reference-icelandic-saga-map`
- **Resource:** Icelandic Saga Map
- **Institutional context:** University of Iceland and associated project partners
- **URL:** https://sagamap.hi.is/
- **Date accessed:** 2026-08-06
- **Resource type:** Scholarly digital map and discovery resource
- **Intended use:** Discovery of candidate saga-place identifications and comparison with prior digital mapping
- **Reliability note:** The project describes its map as a beta version and warns that its geographic data has not been fully checked. Candidate coordinates must therefore be independently reviewed before adoption by SagaRoutes.

## Geographic Source 003: Grenjar identification

- **Source ID:** `geo-source-arnastofnun-grenjar`
- **Institution:** Stofnun Árna Magnússonar í íslenskum fræðum
- **Resource:** Svör við fyrirspurnum um örnefni
- **Resource type:** Institutional place-name reference
- **Date accessed:** 2026-08-07
- **Finding:** The Institute identifies the Grenjar mentioned in
  Gunnlaugs saga as the farm formerly in Álftaneshrepp and now
  within Borgarbyggð.
- **Intended use:** Historical identification of saga-place Grenjar.
- **Reliability note:** Strong evidence for continuity of the place-name
  and farm identity, but not for the exact location of medieval buildings.

## Geographic Source 004: Grenjar coordinates

- **Source ID:** `geo-source-geonames-grenjar`
- **Resource:** Grenjar geographic record
- **Underlying authority:** GeoNames
- **GeoNames ID:** 3416928
- **Date accessed:** 2026-08-07
- **Coordinates:** 64.69943, -21.87543
- **Intended use:** Modern location of the farm Grenjar.
- **Reliability note:** Coordinates locate the modern named farm.
  SagaRoutes does not equate this point with the exact medieval farmstead.

## Geographic Source 005: Valfell / Kambur identification

- **Source ID:** `geo-source-vsnr-valfell`
- **Institution:** Viking Society for Northern Research
- **Resource:** Bandamanna saga, general notes
- **Date accessed:** 2026-08-07
- **Finding:** Scholarly commentary states that Valfell, also named in
  Gunnlaugs saga chapter 2, has been identified with the mountain
  now called Kambur.
- **Intended use:** Identification of Valfell with modern Kambur.
- **Reliability note:** Supports the name identification, but a precise
  geographic point has not yet been adopted by SagaRoutes.

## Geographic Source 006: Tandrasel place-name record

- **Source ID:** `geo-source-arnastofnun-tandrasel`
- **Institution:** Stofnun Árna Magnússonar í íslenskum fræðum
- **Resource:** Tandrasel örnefnaskrá
- **Resource type:** Official place-name archive
- **Date accessed:** 2026-08-07
- **Finding:** The place-name record documents Kamburinn and named
  landscape features associated with it in the Tandrasel area.
- **Intended use:** Corroboration of the modern Kambur/Kamburinn name.

## Geographic Source 007: Gufuá river

- **Source ID:** `geo-source-gufua-river`
- **Resource:** Modern geographic records for Gufuá, Borgarbyggð
- **Related Wikidata ID:** Q134355912
- **Related OpenStreetMap ID:** way/306096106
- **Date accessed:** 2026-08-07
- **Intended use:** Identification of the river associated with
  saga-place Gufuárós.
- **Reliability note:** Modern sources establish the river and its
  estuarine context. They do not by themselves establish the exact
  medieval harbor or landing point.
