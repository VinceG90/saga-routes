import * as maplibregl from "https://unpkg.com/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";

const GEOJSON_URL =
  "../data/gunnlaug/exports/places.geojson";
const UNMAPPED_URL =
  "../data/gunnlaug/exports/unmapped_places.json";
const JOURNEYS_URL =
  "../data/gunnlaug/exports/journeys.json";
const JOURNEY_ROUTES_URL =
  "../data/gunnlaug/exports/journey_routes.geojson";

const statusElement = getRequiredElement("status");
const placeDetailsElement =
  getRequiredElement("place-details");
const journeysElement =
  getRequiredElement("journeys");
const unmappedPlacesElement =
  getRequiredElement("unmapped-places");

let placeFeatureIndex = new Map();
let journeyRouteIndex = new Map();

const map = new maplibregl.Map({
  container: "map",
  style: "https://demotiles.maplibre.org/style.json",
  center: [-21.915145, 64.561782],
  zoom: 7.5
});

map.addControl(
  new maplibregl.NavigationControl(),
  "top-right"
);


function getRequiredElement(id) {
  const element = document.getElementById(id);

  if (!element) {
    throw new Error(
      `Required page element #${id} was not found.`
    );
  }

  return element;
}


function clearElement(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}


function makeElement(
  tagName,
  className = "",
  text = ""
) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (
    text !== undefined
    && text !== null
    && text !== ""
  ) {
    element.textContent = String(text);
  }

  return element;
}


function humanize(value) {
  if (
    value === undefined
    || value === null
    || value === ""
  ) {
    return "Not recorded";
  }

  return String(value)
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      character => character.toUpperCase()
    );
}


function languageName(code) {
  const names = {
    on: "Old Norse",
    en: "English"
  };

  return names[code] || humanize(code);
}


function addMetadataRow(
  list,
  label,
  value
) {
  if (
    value === undefined
    || value === null
    || value === ""
    || (
      Array.isArray(value)
      && value.length === 0
    )
  ) {
    return;
  }

  const row = makeElement(
    "div",
    "metadata-row"
  );

  const term = makeElement(
    "dt",
    "metadata-label",
    label
  );

  let displayValue = value;

  if (Array.isArray(value)) {
    displayValue = value.join(", ");
  } else if (typeof value === "object") {
    displayValue = Object.entries(value)
      .map(
        ([key, item]) =>
          `${humanize(key)}: ${item}`
      )
      .join(" · ");
  }

  const description = makeElement(
    "dd",
    "metadata-value",
    displayValue
  );

  row.append(
    term,
    description
  );

  list.append(row);
}


function passageFromMention(mention) {
  const passage =
    mention
    && typeof mention.passage === "object"
      ? mention.passage
      : mention;

  return {
    id:
      passage?.id
      || mention?.passage_id
      || "Passage ID not recorded",

    language:
      passage?.language
      || mention?.language
      || "unknown",

    chapter_number:
      passage?.chapter_number
      ?? mention?.chapter_number
      ?? "?",

    text:
      passage?.text
      || mention?.passage_text
      || mention?.text
      || "Passage text is not available "
        + "in this export."
  };
}


function createPassageCard(
  passage,
  mention = null
) {
  const article = makeElement(
    "article",
    "passage-card"
  );

  const labelParts = [
    languageName(passage.language),
    `Chapter ${passage.chapter_number}`
  ];

  if (mention?.surface_form) {
    labelParts.push(
      `“${mention.surface_form}”`
    );
  }

  article.append(
    makeElement(
      "div",
      "passage-label",
      labelParts.join(" · ")
    ),

    makeElement(
      "p",
      "passage-text",
      passage.text
    ),

    makeElement(
      "code",
      "passage-id",
      passage.id
    )
  );

  return article;
}


function renderMappedPlace(feature) {
  clearElement(placeDetailsElement);

  const properties =
    feature.properties || {};

  placeDetailsElement.append(
    makeElement(
      "p",
      "eyebrow",
      "Reviewed geographic entity"
    ),

    makeElement(
      "h3",
      "place-name",
      properties.preferred_name
        || "Unnamed place"
    )
  );

  const metadata = makeElement(
    "dl",
    "metadata-list"
  );

  addMetadataRow(
    metadata,
    "Alternate names",
    properties.alternate_names
  );

  addMetadataRow(
    metadata,
    "Feature type",
    humanize(
      properties.feature_type
    )
  );

  addMetadataRow(
    metadata,
    "Region",
    properties.broader_region
  );

  addMetadataRow(
    metadata,
    "Identification",
    humanize(
      properties.identification_status
    )
  );

  addMetadataRow(
    metadata,
    "Spatial certainty",
    humanize(
      properties.spatial_certainty
    )
  );

  addMetadataRow(
    metadata,
    "Coordinate source",
    properties.coordinate_source_id
  );

  addMetadataRow(
    metadata,
    "Authorities",
    properties.authority_ids
  );

  placeDetailsElement.append(
    metadata
  );

  if (properties.editorial_note) {
    const noteSection = makeElement(
      "section",
      "editorial-note"
    );

    noteSection.append(
      makeElement(
        "h4",
        "panel-subheading",
        "Editorial note"
      ),

      makeElement(
        "p",
        "",
        properties.editorial_note
      )
    );

    placeDetailsElement.append(
      noteSection
    );
  }

  const mentions =
    Array.isArray(
      properties.mentions
    )
      ? properties.mentions
      : [];

  if (mentions.length > 0) {
    const evidenceSection =
      makeElement(
        "section",
        "place-evidence"
      );

    evidenceSection.append(
      makeElement(
        "h4",
        "panel-subheading",
        "Textual evidence"
      )
    );

    for (const mention of mentions) {
      evidenceSection.append(
        createPassageCard(
          passageFromMention(mention),
          mention
        )
      );
    }

    placeDetailsElement.append(
      evidenceSection
    );
  }
}


function renderUnmappedPlaces(dataset) {
  clearElement(
    unmappedPlacesElement
  );

  const places =
    Array.isArray(dataset.places)
      ? dataset.places
      : [];

  if (places.length === 0) {
    unmappedPlacesElement.append(
      makeElement(
        "p",
        "empty-state",
        "All current places have "
          + "reviewed coordinates."
      )
    );

    return;
  }

  for (const place of places) {
    const card = makeElement(
      "article",
      "unmapped-card"
    );

    card.append(
      makeElement(
        "h3",
        "unmapped-place-name",
        place.preferred_name
          || "Unnamed place"
      )
    );

    const badgeRow = makeElement(
      "div",
      "badge-row"
    );

    badgeRow.append(
      createBadge(
        `Identification: ${
          humanize(
            place.identification_status
          )
        }`
      ),

      createBadge(
        `Spatial certainty: ${
          humanize(
            place.spatial_certainty
          )
        }`
      )
    );

    card.append(badgeRow);

    if (place.editorial_note) {
      card.append(
        makeElement(
          "p",
          "unmapped-note",
          place.editorial_note
        )
      );
    }

    const mentions =
      Array.isArray(place.mentions)
        ? place.mentions
        : [];

    for (const mention of mentions) {
      card.append(
        createPassageCard(
          passageFromMention(mention),
          mention
        )
      );
    }

    unmappedPlacesElement.append(
      card
    );
  }
}


function createBadge(text) {
  return makeElement(
    "span",
    "badge",
    text
  );
}


function createPlaceFocusButton(place) {
  if (
    !place?.id
    || !placeFeatureIndex.has(
      place.id
    )
  ) {
    return null;
  }

  const button = makeElement(
    "button",
    "place-focus-button",
    `Show ${place.preferred_name} on map`
  );

  button.type = "button";

  button.addEventListener(
    "click",
    () => {
      selectFeature(
        place.id,
        true
      );
    }
  );

  return button;
}


function focusJourneyRoute(feature) {
  if (
    !feature
    || !feature.geometry
    || feature.geometry.type
      !== "LineString"
  ) {
    return;
  }

  const coordinates =
    feature.geometry.coordinates;

  if (
    !Array.isArray(coordinates)
    || coordinates.length === 0
  ) {
    return;
  }

  const bounds =
    new maplibregl.LngLatBounds();

  for (const coordinate of coordinates) {
    bounds.extend(coordinate);
  }

  map.fitBounds(
    bounds,
    {
      padding: 100,
      maxZoom: 11,
      duration: 900
    }
  );
}


function createJourneyRouteFocusButton(
  leg
) {
  const feature =
    journeyRouteIndex.get(
      leg.id
    );

  if (!feature) {
    return null;
  }

  const button = makeElement(
    "button",
    "journey-route-focus",
    "Show route on map"
  );

  button.type = "button";

  button.addEventListener(
    "click",
    () => {
      focusJourneyRoute(feature);

      window.scrollTo({
       top: 0,
       behavior: "smooth"

      });
    }
  );

  return button;
}

function renderMovementEvidence(leg) {
  const container =
    getRequiredElement(
      "movement-evidence"
    );

  clearElement(container);

  const originName =
    leg.origin?.preferred_name
    || "Unknown origin";

  const destinationName =
    leg.destination?.preferred_name
    || "Unknown destination";

  const heading = makeElement(
    "h3",
    "evidence-route-heading",
    `${originName} → ${destinationName}`
  );

  const routeFeature =
  journeyRouteIndex.get(
    leg.id
  );

let displayDescription =
  "No mapped route";

if (routeFeature) {
  const displayType =
    routeFeature.properties
      ?.display_type;

  if (displayType === "schematic") {
    displayDescription =
      "Schematic connection";
  } else if (displayType === "curated") {
    displayDescription =
      "Reviewed route geometry";
  }
}

 const metadata = makeElement(
  "p",
  "evidence-metadata",
  [
    `Route: ${
      humanize(
        leg.route_classification
      )
    }`,

    `Travel: ${
      humanize(
        leg.travel_mode
      )
    }`,

    `Map display: ${displayDescription}`
  ].join(" · ")
 );

  const noteHeading =
    makeElement(
      "h4",
      "evidence-subheading",
      "Editorial interpretation"
    );

  const note = makeElement(
    "p",
    "evidence-note",
    leg.editorial_note
      || "No editorial note has "
        + "been recorded."
  );

  container.append(
    heading,
    metadata,
    noteHeading,
    note
  );

  const passages =
    Array.isArray(leg.passages)
      ? leg.passages
      : [];

  if (passages.length === 0) {
    container.append(
      makeElement(
        "p",
        "empty-state",
        "No textual evidence is "
          + "attached to this journey leg."
      )
    );

    return;
  }

  container.append(
    makeElement(
      "h4",
      "evidence-subheading",
      "Textual evidence"
    )
  );

  for (const passage of passages) {
    const article = makeElement(
      "article",
      "movement-passage"
    );

    const passageLanguage =
  passage.language
  || languageName(
    passage.language_code
  );

const chapterTitle =
  passage.chapter_title
    ? ` — ${passage.chapter_title}`
    : "";

const passageType =
  passage.passage_type
    ? ` · ${humanize(
        passage.passage_type
      )}`
    : "";

const label = makeElement(
  "div",
  "movement-passage-label",
  `${passageLanguage} · `
    + `Chapter ${passage.chapter_number}`
    + `${chapterTitle}`
    + `${passageType}`
);

    const text = makeElement(
      "p",
      "movement-passage-text",
      passage.text
    );

    const id = makeElement(
      "code",
      "movement-passage-id",
      passage.id
    );

    article.append(
      label,
      text,
      id
    );

    container.append(article);
  }
}


function createJourneyLeg(leg) {
  const item = makeElement(
    "li",
    "itinerary-leg"
  );

  const originName =
    leg.origin?.preferred_name
    || "Unknown origin";

  const destinationName =
    leg.destination?.preferred_name
    || "Unknown destination";

  const heading = makeElement(
    "h4",
    "leg-heading",
    `${leg.sequence}. `
      + `${originName} → `
      + `${destinationName}`
  );

  const participantNames =
    Array.isArray(
      leg.participants
    )
      ? leg.participants
          .map(
            person =>
              person.preferred_name
          )
          .filter(Boolean)
          .join(", ")
      : "Participants not recorded";

  const metadata = makeElement(
    "p",
    "leg-metadata",
    [
      humanize(
        leg.travel_mode
      ),

      humanize(
        leg.route_classification
      ),

      participantNames
        || "Participants not recorded"
    ].join(" · ")
  );

  const note = makeElement(
    "p",
    "leg-note",
    leg.editorial_note
      || "No editorial note has "
        + "been recorded."
  );

  item.append(
    heading,
    metadata,
    note
  );

  const buttonRow = makeElement(
    "div",
    "journey-button-row"
  );

  const originButton =
    createPlaceFocusButton(
      leg.origin
    );

  const destinationButton =
    createPlaceFocusButton(
      leg.destination
    );

  if (originButton) {
    buttonRow.append(
      originButton
    );
  }

  if (destinationButton) {
    buttonRow.append(
      destinationButton
    );
  }

  if (
    buttonRow.childElementCount > 0
  ) {
    item.append(buttonRow);
  }

  const actionRow = makeElement(
    "div",
    "journey-action-row"
  );

  const evidenceButton =
    makeElement(
      "button",
      "journey-evidence-button",
      "View movement evidence"
    );

  evidenceButton.type = "button";

  evidenceButton.addEventListener(
    "click",
    () => {
      renderMovementEvidence(leg);

      getRequiredElement(
        "movement-evidence-heading"
      ).scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  );

  actionRow.append(
    evidenceButton
  );

  const routeFocusButton =
    createJourneyRouteFocusButton(
      leg
    );

  if (routeFocusButton) {
    actionRow.append(
      routeFocusButton
    );
  }

  item.append(actionRow);

  return item;
}


function renderJourneys(dataset) {
  clearElement(
    journeysElement
  );

  const journeys =
    Array.isArray(
      dataset.journeys
    )
      ? dataset.journeys
      : [];

  if (journeys.length === 0) {
    journeysElement.append(
      makeElement(
        "p",
        "empty-state",
        "No journeys are "
          + "currently recorded."
      )
    );

    return;
  }

  for (const journey of journeys) {
    const card = makeElement(
      "article",
      "journey-card"
    );

    card.append(
      makeElement(
        "p",
        "eyebrow",
        `Journey ${
          journey.narrative_order
        }`
      ),

      makeElement(
        "h3",
        "journey-title",
        journey.title
      )
    );

    const travelerNames =
      Array.isArray(
        journey.travelers
      )
        ? journey.travelers
            .map(
              person =>
                person.preferred_name
            )
            .filter(Boolean)
            .join(", ")
        : "Travelers not recorded";

    card.append(
      makeElement(
        "p",
        "journey-travelers",
        `Travelers: ${
          travelerNames
            || "Not recorded"
        }`
      )
    );

    const badges = makeElement(
      "div",
      "badge-row"
    );

    if (journey.purpose) {
      badges.append(
        createBadge(
          `Purpose: ${
            humanize(
              journey.purpose
            )
          }`
        )
      );
    }

    if (journey.route_certainty) {
      badges.append(
        createBadge(
          `Route certainty: ${
            humanize(
              journey.route_certainty
            )
          }`
        )
      );
    }

    if (journey.review_status) {
      badges.append(
        createBadge(
          `Review: ${
            humanize(
              journey.review_status
            )
          }`
        )
      );
    }

    if (
      badges.childElementCount > 0
    ) {
      card.append(badges);
    }

    if (journey.editorial_note) {
      card.append(
        makeElement(
          "p",
          "journey-note",
          journey.editorial_note
        )
      );
    }

    const legs =
      Array.isArray(
        journey.legs
      )
        ? [...journey.legs].sort(
            (a, b) =>
              a.sequence
              - b.sequence
          )
        : [];

    if (legs.length > 0) {
      const itineraryHeading =
        makeElement(
          "h4",
          "journey-itinerary-heading",
          "Itinerary"
        );

      const itinerary =
        makeElement(
          "ol",
          "journey-itinerary"
        );

      for (const leg of legs) {
        itinerary.append(
          createJourneyLeg(leg)
        );
      }

      card.append(
        itineraryHeading,
        itinerary
      );
    }

    journeysElement.append(card);
  }
}


function showError(message) {
  statusElement.textContent =
    "Unable to load research data.";

  const containers = [
    placeDetailsElement,
    journeysElement,
    unmappedPlacesElement,
    getRequiredElement(
      "movement-evidence"
    )
  ];

  for (const container of containers) {
    clearElement(container);

    container.append(
      makeElement(
        "p",
        "error-message",
        message
      )
    );
  }
}


async function fetchJSON(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Could not load ${url}: `
        + `${response.status} `
        + `${response.statusText}`
    );
  }

  return response.json();
}


function selectFeature(
  placeId,
  moveMap = true
) {
  const feature =
    placeFeatureIndex.get(
      placeId
    );

  if (!feature) {
    return;
  }

  renderMappedPlace(feature);

  if (
    moveMap
    && feature.geometry?.type
      === "Point"
  ) {
    map.easeTo({
      center:
        feature.geometry.coordinates,

      zoom:
        Math.max(
          map.getZoom(),
          9
        ),

      duration: 700
    });
  }
}


map.on(
  "load",
  async () => {
    try {
      const [
        geojson,
        unmapped,
        journeys,
        journeyRoutes
      ] = await Promise.all([
        fetchJSON(
          GEOJSON_URL
        ),

        fetchJSON(
          UNMAPPED_URL
        ),

        fetchJSON(
          JOURNEYS_URL
        ),

        fetchJSON(
          JOURNEY_ROUTES_URL
        )
      ]);

      if (
        !Array.isArray(
          geojson.features
        )
      ) {
        throw new Error(
          "places.geojson does not "
            + "contain a features array."
        );
      }

      if (
        !Array.isArray(
          unmapped.places
        )
      ) {
        throw new Error(
          "unmapped_places.json does "
            + "not contain a places array."
        );
      }

      if (
        !Array.isArray(
          journeys.journeys
        )
      ) {
        throw new Error(
          "journeys.json does not "
            + "contain a journeys array."
        );
      }

      if (
        !Array.isArray(
          journeyRoutes.features
        )
      ) {
        throw new Error(
          "journey_routes.geojson does "
            + "not contain a features array."
        );
      }

      placeFeatureIndex =
        new Map(
          geojson.features.map(
            feature => [
              feature.properties
                .place_id,
              feature
            ]
          )
        );

      journeyRouteIndex =
        new Map(
          journeyRoutes.features.map(
            feature => [
              feature.properties
                .leg_id,
              feature
            ]
          )
        );


      /*
       * Journey routes
       */

      map.addSource(
        "saga-journey-routes",
        {
          type: "geojson",
          data: journeyRoutes
        }
      );

      map.addLayer({
        id: "saga-curated-routes",

        type: "line",

        source:
          "saga-journey-routes",

        filter: [
          "==",
          [
            "get",
            "display_type"
          ],
          "curated"
        ],

        layout: {
          "line-cap": "round",
          "line-join": "round"
        },

        paint: {
          "line-color":
            "#5f4932",

          "line-width": [
            "interpolate",
            ["linear"],
            ["zoom"],
            5,
            2,
            10,
            4
          ],

          "line-opacity": 0.9
        }
      });

      map.addLayer({
        id:
          "saga-schematic-routes",

        type: "line",

        source:
          "saga-journey-routes",

        filter: [
          "==",
          [
            "get",
            "display_type"
          ],
          "schematic"
        ],

        layout: {
          "line-cap": "round",
          "line-join": "round"
        },

        paint: {
          "line-color":
            "#8a6742",

          "line-width": [
            "interpolate",
            ["linear"],
            ["zoom"],
            5,
            2,
            10,
            4
          ],

          "line-dasharray":
            [3, 3],

          "line-opacity": 0.8
        }
      });


      /*
       * Place points
       */

      map.addSource(
        "saga-places",
        {
          type: "geojson",
          data: geojson
        }
      );

      map.addLayer({
        id: "saga-place-points",

        type: "circle",

        source: "saga-places",

        paint: {
          "circle-radius": [
            "interpolate",
            ["linear"],
            ["zoom"],
            5,
            6,
            10,
            9
          ],

          "circle-color":
            "#294c3a",

          "circle-stroke-color":
            "#f6f1e6",

          "circle-stroke-width":
            2
        }
      });

      map.addLayer({
        id: "saga-place-labels",

        type: "symbol",

        source: "saga-places",

        layout: {
          "text-field": [
            "get",
            "preferred_name"
          ],

          "text-size": 13,

          "text-offset":
            [0, 1.25],

          "text-anchor":
            "top"
        },

        paint: {
          "text-color":
            "#24342b",

          "text-halo-color":
            "#ffffff",

          "text-halo-width":
            1.5
        }
      });


      /*
       * Place interactions
       */

      map.on(
        "click",
        "saga-place-points",
        event => {
          const feature =
            event.features?.[0];

          const placeId =
            feature?.properties
              ?.place_id;

          if (placeId) {
            selectFeature(
              placeId,
              false
            );
          }
        }
      );

      map.on(
        "mouseenter",
        "saga-place-points",
        () => {
          map.getCanvas()
            .style.cursor =
            "pointer";
        }
      );

      map.on(
        "mouseleave",
        "saga-place-points",
        () => {
          map.getCanvas()
            .style.cursor =
            "";
        }
      );


      /*
       * Schematic route interactions
       */

      map.on(
        "click",
        "saga-schematic-routes",
        event => {
          const feature =
            event.features?.[0];

          if (!feature) {
            return;
          }

          const properties =
            feature.properties || {};

          const message =
            `${
              properties.origin_name
            } → `
            + `${
              properties
                .destination_name
            }\n\n`
            + "Schematic connection only. "
            + "This line connects reviewed "
            + "place coordinates and does "
            + "not represent a reconstructed "
            + "historical route.";

          new maplibregl.Popup({
            closeButton: true
          })
            .setLngLat(
              event.lngLat
            )
            .setText(message)
            .addTo(map);
        }
      );

      map.on(
        "mouseenter",
        "saga-schematic-routes",
        () => {
          map.getCanvas()
            .style.cursor =
            "pointer";
        }
      );

      map.on(
        "mouseleave",
        "saga-schematic-routes",
        () => {
          map.getCanvas()
            .style.cursor =
            "";
        }
      );


      /*
       * Render research panels
       */

      renderJourneys(journeys);

      renderUnmappedPlaces(
        unmapped
      );


      /*
       * Status summary
       */

      const mappedPlaceCount =
        geojson.features.length;

      const unmappedPlaceCount =
        Number.isInteger(
          unmapped.place_count
        )
          ? unmapped.place_count
          : unmapped.places.length;

      const journeyCount =
        Number.isInteger(
          journeys.journey_count
        )
          ? journeys.journey_count
          : journeys.journeys.length;

      statusElement.textContent =
        `${mappedPlaceCount} mapped place`
        + `${
          mappedPlaceCount === 1
            ? ""
            : "s"
        }`
        + ` · ${unmappedPlaceCount}`
        + " awaiting coordinates"
        + ` · ${journeyCount} journey`
        + `${
          journeyCount === 1
            ? ""
            : "s"
        }`;


      /*
       * Initial map position
       */

      if (mappedPlaceCount === 1) {
        const onlyFeature =
          geojson.features[0];

        selectFeature(
          onlyFeature.properties
            .place_id,
          false
        );
      } else if (
        mappedPlaceCount > 1
      ) {
        const bounds =
          new maplibregl
            .LngLatBounds();

        for (
          const feature
          of geojson.features
        ) {
          if (
            feature.geometry?.type
              === "Point"
          ) {
            bounds.extend(
              feature.geometry
                .coordinates
            );
          }
        }

        map.fitBounds(
          bounds,
          {
            padding: 70,
            maxZoom: 9
          }
        );
      }
    } catch (error) {
      console.error(error);

      showError(
        error instanceof Error
          ? error.message
          : "An unknown error occurred."
      );
    }
  }
);
