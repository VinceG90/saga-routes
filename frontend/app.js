import * as maplibregl from "https://unpkg.com/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";


const GEOJSON_URL =
  "../data/gunnlaug/exports/places.geojson";

const UNMAPPED_URL =
  "../data/gunnlaug/exports/unmapped_places.json";

const JOURNEYS_URL =
  "../data/gunnlaug/exports/journeys.json";

const JOURNEY_ROUTES_URL =
  "../data/gunnlaug/exports/journey_routes.geojson";

const map = new maplibregl.Map({
  container: "map",
  style: "https://demotiles.maplibre.org/style.json",
  center: [-21.915145, 64.561782],
  zoom: 7.5,
  maxZoom: 16,
  attributionControl: true
});


map.addControl(
  new maplibregl.NavigationControl({
    visualizePitch: true
  }),
  "top-left"
);

map.addControl(
  new maplibregl.FullscreenControl(),
  "top-left"
);


function getRequiredElement(elementId) {
  const element = document.getElementById(elementId);

  if (!element) {
    throw new Error(
      `Required HTML element was not found: #${elementId}`
    );
  }

  return element;
}


const statusElement = getRequiredElement("data-status");
const errorElement = getRequiredElement("app-error");
const detailsElement = getRequiredElement("place-details");
const journeysElement = getRequiredElement("journeys");
const unmappedElement = getRequiredElement("unmapped-places");

const mappedFeatureIndex = new Map();


function clearElement(element) {
  element.replaceChildren();
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

  if (text !== "") {
    element.textContent = String(text);
  }

  return element;
}


function humanize(value) {
  if (
    value === null
    || value === undefined
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


function languageName(languageCode) {
  if (languageCode === "on") {
    return "Old Norse";
  }

  if (languageCode === "en") {
    return "English";
  }

  return languageCode || "Unknown language";
}


function addMetadataRow(list, label, value) {
  const term = makeElement("dt", "", label);
  const description = makeElement("dd", "", value);

  list.append(term, description);
}


function createPassageCard(mention) {
  const card = makeElement(
    "article",
    "passage-card"
  );

  const title = makeElement(
    "h4",
    "",
    `${languageName(mention.language_code)}: `
      + `${mention.surface_form}`
  );

  const metadataParts = [
    `Chapter ${mention.chapter_number}`,
    humanize(mention.mention_role),
    humanize(mention.visit_status),
    mention.passage_id
  ];

  const metadata = makeElement(
    "p",
    "passage-metadata",
    metadataParts.join(" · ")
  );

  const passage = makeElement(
    "blockquote",
    "passage-text",
    mention.text
  );

  card.append(
    title,
    metadata,
    passage
  );

  if (mention.editorial_note) {
    const note = makeElement(
      "p",
      "passage-note",
      mention.editorial_note
    );

    card.append(note);
  }

  return card;
}


function renderMappedPlace(feature) {
  const properties = feature.properties;
  const coordinates = feature.geometry.coordinates;
  const [longitude, latitude] = coordinates;

  clearElement(detailsElement);

  detailsElement.append(
    makeElement(
      "p",
      "eyebrow",
      "Mapped evidence"
    ),
    makeElement(
      "h2",
      "",
      properties.preferred_name
    )
  );

  const summary = makeElement(
    "div",
    "place-summary"
  );

  const metadata = makeElement(
    "dl",
    "metadata-list"
  );

  addMetadataRow(
    metadata,
    "Place ID",
    properties.place_id
  );

  addMetadataRow(
    metadata,
    "Alternate names",
    Array.isArray(properties.alternate_names)
      && properties.alternate_names.length > 0
      ? properties.alternate_names.join(", ")
      : "None recorded"
  );

  addMetadataRow(
    metadata,
    "Feature type",
    humanize(properties.feature_type)
  );

  addMetadataRow(
    metadata,
    "Region",
    properties.broader_region || "Not recorded"
  );

  addMetadataRow(
    metadata,
    "Identification",
    humanize(properties.identification_status)
  );

  addMetadataRow(
    metadata,
    "Spatial certainty",
    humanize(properties.spatial_certainty)
  );

  addMetadataRow(
    metadata,
    "Coordinates",
    `${latitude.toFixed(6)}, `
      + `${longitude.toFixed(6)}`
  );

  addMetadataRow(
    metadata,
    "Textual mentions",
    properties.mention_count ?? 0
  );

  summary.append(metadata);
  detailsElement.append(summary);

  if (properties.editorial_note) {
    detailsElement.append(
      makeElement(
        "p",
        "editorial-note",
        properties.editorial_note
      )
    );
  }

  detailsElement.append(
    makeElement(
      "h3",
      "passages-heading",
      "Textual evidence"
    )
  );

  const mentions = Array.isArray(properties.mentions)
    ? properties.mentions
    : [];

  if (mentions.length === 0) {
    detailsElement.append(
      makeElement(
        "p",
        "",
        "No passage annotations are currently attached."
      )
    );

    return;
  }

  for (const mention of mentions) {
    detailsElement.append(
      createPassageCard(mention)
    );
  }
}


function renderUnmappedPlaces(dataset) {
  clearElement(unmappedElement);

  const places = Array.isArray(dataset.places)
    ? dataset.places
    : [];

  if (places.length === 0) {
    unmappedElement.append(
      makeElement(
        "p",
        "",
        "No unresolved locations are currently recorded."
      )
    );

    return;
  }

  for (const place of places) {
    const card = makeElement(
      "article",
      "unmapped-card"
    );

    const name = makeElement(
      "h3",
      "",
      place.preferred_name
    );

    const mentionCount =
      Number.isInteger(place.mention_count)
        ? place.mention_count
        : 0;

    const status = makeElement(
      "p",
      "unmapped-status",
      [
        humanize(place.identification_status),
        `${mentionCount} textual mention`
          + `${mentionCount === 1 ? "" : "s"}`
      ].join(" · ")
    );

    const note = makeElement(
      "p",
      "",
      place.editorial_note
        || "No editorial note has been recorded."
    );

    card.append(
      name,
      status,
      note
    );

    unmappedElement.append(card);
  }
}


function createBadge(
  text,
  modifier = ""
) {
  const className = [
    "status-badge",
    modifier
  ]
    .filter(Boolean)
    .join(" ");

  return makeElement(
    "span",
    className,
    text
  );
}


function createPlaceFocusButton(place) {
  if (!mappedFeatureIndex.has(place.id)) {
    return null;
  }

  const button = makeElement(
    "button",
    "place-focus-button",
    `View ${place.preferred_name} on map`
  );

  button.type = "button";

  button.addEventListener("click", () => {
    selectFeature(place.id, true);
  });

  return button;
}


function createJourneyLeg(leg) {
  const item = makeElement(
    "li",
    "itinerary-leg"
  );

  const heading = makeElement(
    "h4",
    "leg-heading",
    `${leg.sequence}. `
      + `${leg.origin.preferred_name} → `
      + `${leg.destination.preferred_name}`
  );

  const participantNames = Array.isArray(
    leg.participants
  )
    ? leg.participants
        .map(person => person.preferred_name)
        .join(", ")
    : "Participants not recorded";

  const metadata = makeElement(
    "p",
    "leg-metadata",
    [
      humanize(leg.travel_mode),
      humanize(leg.route_classification),
      participantNames
    ].join(" · ")
  );

  const note = makeElement(
    "p",
    "leg-note",
    leg.editorial_note
      || "No editorial note has been recorded."
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

  const originButton = createPlaceFocusButton(
    leg.origin
  );

  const destinationButton =
    createPlaceFocusButton(
      leg.destination
    );

  if (originButton) {
    buttonRow.append(originButton);
  }

  if (destinationButton) {
    buttonRow.append(destinationButton);
  }

  if (buttonRow.childElementCount > 0) {
    item.append(buttonRow);
  }

  return item;
}


function renderJourneys(dataset) {
  clearElement(journeysElement);

  const journeys = Array.isArray(dataset.journeys)
    ? dataset.journeys
    : [];

  if (journeys.length === 0) {
    journeysElement.append(
      makeElement(
        "p",
        "",
        "No journeys are currently recorded."
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
        `Journey ${journey.narrative_order}`
      ),
      makeElement(
        "h3",
        "",
        journey.title
      )
    );

    const travelerNames = Array.isArray(
      journey.travelers
    )
      ? journey.travelers
          .map(person => person.preferred_name)
          .join(", ")
      : "Travelers not recorded";

    card.append(
      makeElement(
        "p",
        "journey-travelers",
        `Travelers: ${travelerNames}`
      )
    );

    const badges = makeElement(
      "div",
      "badge-row"
    );

    badges.append(
      createBadge(
        `${humanize(journey.route_certainty)} `
          + "route certainty"
      ),
      createBadge(
        humanize(journey.review_status)
      ),
      createBadge(
        `${journey.leg_count} leg`
          + `${journey.leg_count === 1 ? "" : "s"}`
      )
    );

    if (journey.mapped_leg_count === 0) {
      badges.append(
        createBadge(
          "Route geometry unresolved",
          "unmapped"
        )
      );
    } else if (
      journey.mapped_leg_count
      < journey.leg_count
    ) {
      badges.append(
        createBadge(
          "Route partially mapped",
          "unmapped"
        )
      );
    }

    card.append(badges);

    if (journey.editorial_note) {
      card.append(
        makeElement(
          "p",
          "journey-note",
          journey.editorial_note
        )
      );
    }

    const itinerary = makeElement(
      "ol",
      "itinerary"
    );

    const legs = Array.isArray(journey.legs)
      ? journey.legs
      : [];

    for (const leg of legs) {
      itinerary.append(
        createJourneyLeg(leg)
      );
    }

    card.append(itinerary);
    journeysElement.append(card);
  }
}


function showError(message) {
  errorElement.textContent = message;
  errorElement.hidden = false;
  statusElement.textContent =
    "Data loading failed";
}


async function fetchJSON(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Could not load ${url}: `
        + `HTTP ${response.status}`
    );
  }

  return response.json();
}


function selectFeature(
  placeId,
  openPopup = false
) {
  const feature =
    mappedFeatureIndex.get(placeId);

  if (!feature) {
    return;
  }

  renderMappedPlace(feature);

  const coordinates =
    feature.geometry.coordinates;

  map.easeTo({
    center: coordinates,
    zoom: Math.max(map.getZoom(), 9),
    duration: 700
  });

  if (openPopup) {
    new maplibregl.Popup({
      offset: 12,
      closeButton: true
    })
      .setLngLat(coordinates)
      .setText(
        feature.properties.preferred_name
      )
      .addTo(map);
  }
}


map.on("load", async () => {
  try {
const [
  geojson,
  unmapped,
  journeys,
  journeyRoutes
] = await Promise.all([
  fetchJSON(GEOJSON_URL),
  fetchJSON(UNMAPPED_URL),
  fetchJSON(JOURNEYS_URL),
  fetchJSON(JOURNEY_ROUTES_URL)
]);

    if (
      geojson.type !== "FeatureCollection"
      || !Array.isArray(geojson.features)
    ) {
      throw new Error(
        "places.geojson is not a valid "
          + "GeoJSON FeatureCollection."
      );
    }

    if (!Array.isArray(unmapped.places)) {
      throw new Error(
        "unmapped_places.json does not "
          + "contain a places array."
      );
    }

    if (!Array.isArray(journeys.journeys)) {
      throw new Error(
        "journeys.json does not contain "
          + "a journeys array."
      );
    }

    for (const feature of geojson.features) {
      const placeId =
        feature.properties?.place_id;

      if (placeId) {
        mappedFeatureIndex.set(
          placeId,
          feature
        );
      }
    }
map.addSource("saga-journey-routes", {
  type: "geojson",
  data: journeyRoutes
});

map.addLayer({
  id: "saga-schematic-routes",
  type: "line",
  source: "saga-journey-routes",

  filter: [
    "==",
    ["get", "display_type"],
    "schematic"
  ],

  layout: {
    "line-cap": "round",
    "line-join": "round"
  },

  paint: {
    "line-color": "#8a6742",
    "line-width": [
      "interpolate",
      ["linear"],
      ["zoom"],
      5, 2,
      10, 4
    ],
    "line-dasharray": [3, 3],
    "line-opacity": 0.8
  }
});
    map.addSource("saga-places", {
      type: "geojson",
      data: geojson
    });

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
          10
        ],
        "circle-color": "#365f52",
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": 2
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
        "text-font": [
          "Noto Sans Regular"
        ],
        "text-size": 13,
        "text-offset": [0, 1.3],
        "text-anchor": "top",
        "text-allow-overlap": false
      },
      paint: {
        "text-color": "#20251f",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.5
      }
    });
map.on(
  "click",
  "saga-schematic-routes",
  event => {
    const feature = event.features?.[0];

    if (!feature) {
      return;
    }

    const properties = feature.properties;

    const message =
      `${properties.origin_name} → `
      + `${properties.destination_name}\n\n`
      + "Schematic connection only. "
      + "This line connects reviewed place "
      + "coordinates and does not represent "
      + "a reconstructed historical route.";

    new maplibregl.Popup({
      closeButton: true
    })
      .setLngLat(event.lngLat)
      .setText(message)
      .addTo(map);
  }
);

map.on(
  "mouseenter",
  "saga-schematic-routes",
  () => {
    map.getCanvas().style.cursor =
      "pointer";
  }
);

map.on(
  "mouseleave",
  "saga-schematic-routes",
  () => {
    map.getCanvas().style.cursor = "";
  }
);
    map.on(
      "click",
      "saga-place-points",
      event => {
        const renderedFeature =
          event.features?.[0];

        const placeId =
          renderedFeature?.properties?.place_id;

        if (placeId) {
          selectFeature(placeId, true);
        }
      }
    );

    map.on(
      "mouseenter",
      "saga-place-points",
      () => {
        map.getCanvas().style.cursor =
          "pointer";
      }
    );

    map.on(
      "mouseleave",
      "saga-place-points",
      () => {
        map.getCanvas().style.cursor = "";
      }
    );

    renderJourneys(journeys);
    renderUnmappedPlaces(unmapped);

    const mappedPlaceCount =
      geojson.features.length;

    const unmappedPlaceCount =
      Number.isInteger(unmapped.place_count)
        ? unmapped.place_count
        : unmapped.places.length;

    const journeyCount =
      Number.isInteger(journeys.journey_count)
        ? journeys.journey_count
        : journeys.journeys.length;

    statusElement.textContent =
      `${mappedPlaceCount} mapped place`
      + `${mappedPlaceCount === 1 ? "" : "s"}`
      + ` · ${unmappedPlaceCount} awaiting coordinates`
      + ` · ${journeyCount} journey`
      + `${journeyCount === 1 ? "" : "s"}`;

    if (mappedPlaceCount === 1) {
      const onlyFeature =
        geojson.features[0];

      selectFeature(
        onlyFeature.properties.place_id,
        false
      );
    } else if (mappedPlaceCount > 1) {
      const bounds =
        new maplibregl.LngLatBounds();

      for (const feature of geojson.features) {
        bounds.extend(
          feature.geometry.coordinates
        );
      }

      map.fitBounds(bounds, {
        padding: 70,
        maxZoom: 9
      });
    }
  } catch (error) {
    console.error(error);

    showError(
      error instanceof Error
        ? error.message
        : "An unknown error occurred."
    );
  }
});
