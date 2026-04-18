(function () {
  const root = window.MealsOnWheels || (window.MealsOnWheels = {});
  const data = root.data;

  function formatCurrency(value) {
    return "$" + Number(value).toFixed(2);
  }

  function normalizeQuery(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[.,#]/g, " ")
      .replace(/\s+/g, " ");
  }

  function toRadians(value) {
    return (value * Math.PI) / 180;
  }

  function haversineMiles(pointA, pointB) {
    const earthRadiusKm = 6371;
    const deltaLat = toRadians(pointB.lat - pointA.lat);
    const deltaLng = toRadians(pointB.lng - pointA.lng);
    const base =
      Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
      Math.cos(toRadians(pointA.lat)) *
        Math.cos(toRadians(pointB.lat)) *
        Math.sin(deltaLng / 2) *
        Math.sin(deltaLng / 2);

    const distanceKm = earthRadiusKm * 2 * Math.atan2(Math.sqrt(base), Math.sqrt(1 - base));
    return distanceKm * 0.621371;
  }

  function geocodeLocal(query) {
    const normalized = normalizeQuery(query);

    if (!normalized) {
      return null;
    }

    const coordinateMatch = normalized.match(/(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)/);
    if (coordinateMatch) {
      return {
        label: "Custom coordinates",
        lat: parseFloat(coordinateMatch[1]),
        lng: parseFloat(coordinateMatch[2]),
        query: query
      };
    }

    if (data.knownLocations[normalized]) {
      return Object.assign({ query: query }, data.knownLocations[normalized]);
    }

    const knownKeys = Object.keys(data.knownLocations).sort(function (left, right) {
      return right.length - left.length;
    });

    for (let index = 0; index < knownKeys.length; index += 1) {
      const key = knownKeys[index];
      if (normalized.indexOf(key) !== -1) {
        return Object.assign({ query: query }, data.knownLocations[key]);
      }
    }

    return null;
  }

  function stockFor(item, stop) {
    const seed =
      item.id.split("").reduce(function (total, character) {
        return total + character.charCodeAt(0);
      }, 0) +
      stop.id.length * 9;
    const modifier = 0.72 + (seed % 31) / 100 + (stop.stockBoost - 1);
    return Math.max(0, Math.round(item.baseStock * modifier));
  }

  function buildDirectionsUrl(origin, stop) {
    const originValue =
      origin && typeof origin.lat === "number" && typeof origin.lng === "number"
        ? origin.lat + "," + origin.lng
        : encodeURIComponent((origin && (origin.query || origin.label)) || "");

    return (
      "https://www.google.com/maps/dir/?api=1&origin=" +
      originValue +
      "&destination=" +
      stop.lat +
      "," +
      stop.lng +
      "&travelmode=walking"
    );
  }

  function buildStopUrl(stop) {
    return "https://www.google.com/maps/search/?api=1&query=" + stop.lat + "," + stop.lng;
  }

  function abbreviateLabel(text, fallback) {
    const parts = String(text || "")
      .split(/[^A-Za-z0-9]+/)
      .filter(Boolean);

    if (!parts.length) {
      return fallback || "MW";
    }

    if (parts.length === 1) {
      return parts[0].slice(0, 2).toUpperCase();
    }

    return (parts[0][0] + parts[1][0]).toUpperCase();
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  root.utils = {
    abbreviateLabel: abbreviateLabel,
    buildDirectionsUrl: buildDirectionsUrl,
    buildStopUrl: buildStopUrl,
    escapeHtml: escapeHtml,
    formatCurrency: formatCurrency,
    geocodeLocal: geocodeLocal,
    haversineMiles: haversineMiles,
    normalizeQuery: normalizeQuery,
    stockFor: stockFor
  };
})();
