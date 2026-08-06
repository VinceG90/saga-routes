## Geographic Entities and Place Mentions

SagaRoutes distinguishes a normalized geographic entity from each textual occurrence of its name.

### Place

A `Place` represents a geographic entity proposed by SagaRoutes. A place may have:

- A preferred name
- Variant or translated names
- A feature type
- A broader geographic region
- An identification status
- A spatial-certainty level
- Optional GeoJSON geometry
- External authority identifiers
- An editorial explanation

A place is not required to have coordinates. An unresolved place is preferable to a falsely precise map point.

### Place Mention

A `PlaceMention` represents a specific geographic expression in a source passage.

Each mention records:

- The source passage
- The normalized place
- The exact textual surface form
- The language
- Its narrative role
- Whether a character is present, arriving, departing, visiting, passing through, or merely mentioning the place
- Any associated parallel-text alignment
- An editorial note

This separation allows forms such as `Borg`, `Burg`, `Valfell`, and `Hawkfell` to be connected without erasing differences between the source text and translation.

### Coordinate Order

SagaRoutes stores GeoJSON coordinates in longitude-latitude order:

```text
[longitude, latitude]
