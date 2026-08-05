# SagaDB Source Files

This directory contains the parallel Old Norse and English working texts used by the initial SagaRoutes prototype.

## Files

### `gunnlaugs_saga_ormstungu.on.xml`

A normalized Old Norse version of *Gunnlaugs saga ormstungu* obtained from the Icelandic Saga Database source repository.

### `gunnlaugs_saga_ormstungu.en.xml`

The William Morris and Eiríkr Magnússon English translation obtained from the Icelandic Saga Database source repository.

### `UPSTREAM_COMMIT.txt`

The Git commit identifier for the version of the SagaDB repository from which these files were downloaded.

### `checksums.sha256`

SHA-256 checksums used to verify that the local source files have not changed unexpectedly.

## Rights

The Icelandic Saga Database identifies its saga source texts as public domain. These copies are retained in the SagaRoutes repository to support reproducibility, annotation, textual comparison, and computational processing.

## Editorial Status

These files are unmodified upstream source copies.

Do not manually correct or annotate these XML files. Corrections, normalization, alignments, place-name annotations, and editorial observations must be stored separately under:

```text
data/gunnlaug/curated/
```

This separation preserves a clear distinction between source material and SagaRoutes editorial data.

## Important Limitation

The Old Norse and English texts do not use matching chapter divisions. Parallel alignment must therefore be represented through SagaRoutes identifiers rather than assumed from chapter numbering.
