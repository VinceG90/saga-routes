import * as maplibregl from
  "https://unpkg.com/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";

const GEOJSON_URL =
  "../data/gunnlaug/exports/places.geojson";

const UNMAPPED_URL =
  "../data/gunnlaug/exports/unmapped_places.json";

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

const statusElement = document.getElementById("data-status");
const errorElement = document.getElementById("app-error");
const detailsElement = document.getElementById("place-details");
const unmappedElement = document.getElementById("unmapped-places");

const mappedFeatureIndex = new Map();


function clearElement(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}


function makeElement(tagName, className = "", text = "") {
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
  if (value === null || value === undefined || value === "") {
    return "Not recorded";
  }

  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, character => character.toUpperCase());
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
  const card = makeElement("article", "passage-card");

  const title = makeElement(
    "h4",
    "",
    `${languageName(mention.language_code)}: ${mention.surface_form}`
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

  card.append(title, metadata, passage);

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
  const [longitude, latitude] = feature.geometry.coordinates;

  clearElement(detailsElement);

  detailsElement.append(
    makeElement("p", "eyebrow", "Mapped evidence"),
    makeElement("h2", "", properties.preferred_name)
  );

  const summary = makeElement("div", "place-summary");
  const metadata = makeElement("dl", "metadata-list");

  addMetadataRow(
    metadata,
    "Place ID",
    properties.place_id
  );

  addMetadataRow(
    metadata,
    "Alternate names",
    properties.alternate_names?.length
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
    `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
  );

  addMetadataRow(
    metadata,
    "Textual mentions",
    properties.mention_count
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

  const passagesHeading = makeElement(
    "h3",
    "passages-heading",
    "Textual evidence"
  );

  detailsElement.append(passagesHeading);

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
    detailsElement.append(createPassageCard(mention));
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
    const card = makeElement("article", "unmapped-card");

    const name = makeElement(
      "h3",
      "",
      place.preferred_name
    );

    const status = makeElement(
      "p",
      "unmapped-status",
      [
        humanize(place.identification_status),
        `${place.mention_count} textual mention(s)`
      ].join(" · ")
    );

    const note = makeElement(
      "p",
      "",
      place.editorial_note
    );

    card.append(name, status, note);
    unmappedElement.append(card);
  }
}


function showError(message) {
  errorElement.textContent = message;
  errorElement.hidden = false;
  statusElement.textContent = "Data loading failed";
}


async function fetchJSON(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Could not load ${url}: HTTP ${response.status}`
    );
  }

  return response.json();
}


function selectFeature(placeId, openPopup = false) {
  const feature = mappedFeatureIndex.get(placeId);

  if (!feature) {
    return;
  }

  renderMappedPlace(feature);

  const coordinates = feature.geometry.coordinates;

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
      .setText(feature.properties.preferred_name)
      .addTo(map);
  }
}


map.on("load", async () => {
  try {
    const [geojson, unmapped] = await Promise.all([
      fetchJSON(GEOJSON_URL),
      fetchJSON(UNMAPPED_URL)
    ]);

    if (
      geojson.type !== "FeatureCollection"
      || !Array.isArray(geojson.features)
    ) {
      throw new Error(
        "places.geojson is not a valid FeatureCollection."
      );
    }

    for (const feature of geojson.features) {
      const placeId = feature.properties?.place_id;

      if (placeId) {
        mappedFeatureIndex.set(placeId, feature);
      }
    }

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
          5, 6,
          10, 10
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
        "text-field": ["get", "preferred_name"],
        "text-font": ["Noto Sans Regular"],
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

    map.on("click", "saga-place-points", event => {
      const renderedFeature = event.features?.[0];
      const placeId = renderedFeature?.properties?.place_id;

      if (placeId) {
        selectFeature(placeId, true);
      }
    });

    map.on("mouseenter", "saga-place-points", () => {
      map.getCanvas().style.cursor = "pointer";
    });

    map.on("mouseleave", "saga-place-points", () => {
      map.getCanvas().style.cursor = "";
    });

    renderUnmappedPlaces(unmapped);

    statusElement.textContent =
      `${geojson.features.length} mapped place`
      + `${geojson.features.length === 1 ? "" : "s"}`
      + ` · ${unmapped.place_count} awaiting coordinates`;

    if (geojson.features.length === 1) {
      const onlyFeature = geojson.features[0];
      selectFeature(
        onlyFeature.properties.place_id,
        false
      );
    } else if (geojson.features.length > 1) {
      const bounds = new maplibregl.LngLatBounds();

      for (const feature of geojson.features) {
        bounds.extend(feature.geometry.coordinates);
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
