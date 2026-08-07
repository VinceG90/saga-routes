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

## Display Geometry and Historical Route Geometry

SagaRoutes distinguishes geographic data used for interface display from
geometry presented as a historical reconstruction.

When both endpoints of a journey leg have reviewed coordinates but the
historical course between them is unknown, the system may generate a
straight schematic connection.

A schematic connection:

- is generated from endpoint coordinates;
- is not stored as curated historical route geometry;
- is marked `display_type: schematic`;
- records `geometry_basis: schematic_endpoints`;
- records `historical_route_claim: false`;
- must use visually distinct styling in the interface.

Such a line expresses the proposition that a narrative movement connects
two identified places. It does not claim that a traveler followed the
displayed line.

Future reconstructed routes must be stored and documented separately,
with their evidence, assumptions, method, and uncertainty recorded.
