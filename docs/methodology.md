## Parallel-Text Alignment

SagaRoutes does not assume that chapter or paragraph numbers correspond across editions and translations.

Parallel passages are connected through explicit alignment records. Each record may connect one or more Old Norse passages with one or more English passages. This permits one-to-one, one-to-many, many-to-one, and many-to-many relationships.

An alignment indicates narrative or semantic correspondence, not exact word-for-word equivalence.

Each alignment records:

- The passages on both sides
- Alignment cardinality
- Degree of textual coverage
- Editorial confidence
- Review status
- An explanation of the editorial decision

Initial alignments are marked `provisional`. They may later be changed to `reviewed` after comparison with the source text and relevant editions or marked `disputed` when more than one alignment is defensible.

SagaRoutes will preserve segmentation differences rather than rewriting the source texts to make them appear structurally identical.
