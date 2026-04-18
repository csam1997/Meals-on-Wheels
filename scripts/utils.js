(function () {
  const root = window.MealsOnWheels || (window.MealsOnWheels = {});
  const data = root.data;
  const itemImageCache = {};

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

    if (/^20[2-5]\d{2}$/.test(normalized)) {
      return {
        label: "Federal core " + normalized,
        lat: 38.8977,
        lng: -77.0366,
        query: query
      };
    }

    if (/^200\d{2}$/.test(normalized)) {
      return {
        label: "DC ZIP " + normalized,
        lat: 38.9072,
        lng: -77.0369,
        query: query
      };
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
    if (!stop) {
      return Math.max(0, Math.round(item.baseStock * 0.94));
    }

    const seed =
      item.id.split("").reduce(function (total, character) {
        return total + character.charCodeAt(0);
      }, 0) +
      stop.id.length * 9;
    const modifier = 0.72 + (seed % 31) / 100 + (stop.stockBoost - 1);
    return Math.max(0, Math.round(item.baseStock * modifier));
  }

  function buildGoogleSearchUrl(queryOrLocation) {
    let query = "Washington, DC";

    if (typeof queryOrLocation === "string" && queryOrLocation.trim()) {
      query = queryOrLocation.trim();
    } else if (
      queryOrLocation &&
      typeof queryOrLocation.lat === "number" &&
      typeof queryOrLocation.lng === "number"
    ) {
      query = queryOrLocation.lat + "," + queryOrLocation.lng;
    } else if (queryOrLocation && queryOrLocation.label) {
      query = queryOrLocation.label;
    }

    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(query);
  }

  function buildGoogleEmbedUrl(origin, stop) {
    let query = "Washington, DC";

    if (stop && typeof stop.lat === "number" && typeof stop.lng === "number") {
      query = stop.lat + "," + stop.lng;
    } else if (origin && typeof origin.lat === "number" && typeof origin.lng === "number") {
      query = origin.lat + "," + origin.lng;
    } else if (origin && origin.label) {
      query = origin.label + ", Washington, DC";
    }

    return "https://www.google.com/maps?q=" + encodeURIComponent(query) + "&z=13&output=embed";
  }

  function buildDirectionsUrl(origin, stop) {
    if (!stop) {
      return buildGoogleSearchUrl(origin || "Washington, DC");
    }

    if (origin && typeof origin.lat === "number" && typeof origin.lng === "number") {
      return (
        "https://www.google.com/maps/dir/?api=1&origin=" +
        origin.lat +
        "," +
        origin.lng +
        "&destination=" +
        stop.lat +
        "," +
        stop.lng +
        "&travelmode=walking"
      );
    }

    return buildStopUrl(stop);
  }

  function buildStopUrl(stop) {
    if (!stop) {
      return buildGoogleSearchUrl("Washington, DC");
    }

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

  function escapeXml(value) {
    return escapeHtml(value);
  }

  function svgDataUrl(svg) {
    return "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg);
  }

  function shortenText(value, maxLength) {
    const text = String(value || "");
    if (text.length <= maxLength) {
      return text;
    }
    return text.slice(0, maxLength - 1) + "...";
  }

  function plateShadow(width, y) {
    return '<ellipse cx="320" cy="' + String(y || 360) + '" rx="' + String(width || 148) + '" ry="28" fill="rgba(16,34,40,0.08)" />';
  }

  function bowlScene(fill, toppings, accent) {
    return (
      plateShadow(146, 360) +
      '<path d="M196 220C208 306 244 346 320 346C396 346 432 306 444 220Z" fill="#ffffff" stroke="rgba(17,34,40,0.09)" stroke-width="3" />' +
      '<ellipse cx="320" cy="220" rx="130" ry="36" fill="' +
      fill +
      '" />' +
      toppings +
      '<path d="M220 246C246 312 270 334 320 334C370 334 394 312 420 246" fill="none" stroke="' +
      accent +
      '" stroke-width="6" stroke-linecap="round" opacity="0.2" />'
    );
  }

  function cupScene(layerMarkup, accent) {
    return (
      plateShadow(126, 360) +
      '<path d="M248 158H392L372 338H268Z" fill="rgba(255,255,255,0.58)" stroke="rgba(17,34,40,0.12)" stroke-width="3" />' +
      layerMarkup +
      '<path d="M248 158H392" stroke="' +
      accent +
      '" stroke-width="10" stroke-linecap="round" opacity="0.26" />'
    );
  }

  function pouchScene(color, details, accent) {
    return (
      plateShadow(124, 360) +
      '<path d="M232 138H408L392 338H248Z" fill="' +
      color +
      '" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
      '<rect x="246" y="164" width="148" height="18" rx="9" fill="rgba(255,255,255,0.45)" />' +
      details +
      '<path d="M252 196H388" stroke="' +
      accent +
      '" stroke-width="8" stroke-linecap="round" opacity="0.24" />'
    );
  }

  function trayScene(base, contents) {
    return (
      plateShadow(140, 364) +
      '<rect x="214" y="172" width="212" height="150" rx="28" fill="' +
      base +
      '" stroke="rgba(17,34,40,0.11)" stroke-width="3" />' +
      contents
    );
  }

  function boxScene(base, lid, contents) {
    return (
      plateShadow(150, 366) +
      '<rect x="208" y="176" width="224" height="140" rx="30" fill="' +
      base +
      '" stroke="rgba(17,34,40,0.12)" stroke-width="3" />' +
      '<path d="M236 176H404L388 140H252Z" fill="' +
      lid +
      '" />' +
      contents
    );
  }

  function breadScene(baseColor, slicesMarkup) {
    return (
      plateShadow(146, 364) +
      '<path d="M228 238C228 194 250 174 290 174H350C390 174 412 194 412 238V312H228Z" fill="' +
      baseColor +
      '" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
      '<path d="M242 238C242 206 258 190 290 190H350C382 190 398 206 398 238V298H242Z" fill="rgba(255,255,255,0.24)" />' +
      slicesMarkup
    );
  }

  function cartonScene(cartonColor, detailMarkup) {
    return (
      plateShadow(132, 364) +
      '<path d="M266 150H356L388 184V336H266Z" fill="' +
      cartonColor +
      '" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
      '<path d="M356 150V184H388" fill="rgba(255,255,255,0.25)" />' +
      detailMarkup
    );
  }

  function sceneFor(item) {
    switch (item.id) {
      case "apple_pb":
        return {
          bgA: "#ebf8ef",
          bgB: "#fff1dc",
          accent: "#1d7c62",
          artwork:
            plateShadow(138, 360) +
            '<circle cx="278" cy="242" r="56" fill="#ef5845" />' +
            '<ellipse cx="300" cy="202" rx="18" ry="10" fill="#52b56f" transform="rotate(-28 300 202)" />' +
            '<path d="M278 184C282 170 290 160 304 154" fill="none" stroke="#385b24" stroke-width="6" stroke-linecap="round" />' +
            '<ellipse cx="350" cy="264" rx="70" ry="46" fill="#fffaf3" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<ellipse cx="350" cy="252" rx="52" ry="24" fill="#c88a4d" />' +
            '<path d="M316 250C332 234 352 234 370 250C388 266 406 266 418 248" fill="none" stroke="rgba(255,255,255,0.42)" stroke-width="6" stroke-linecap="round" />'
        };
      case "yogurt_parfait":
        return {
          bgA: "#eef8ff",
          bgB: "#fff2e8",
          accent: "#1683c7",
          artwork: cupScene(
            '<rect x="272" y="188" width="96" height="26" rx="12" fill="#f1d17d" />' +
              '<rect x="272" y="214" width="96" height="40" rx="10" fill="#ffffff" />' +
              '<rect x="272" y="254" width="96" height="26" rx="10" fill="#9a4fcb" opacity="0.84" />' +
              '<rect x="272" y="280" width="96" height="34" rx="10" fill="#f9f7f3" />' +
              '<circle cx="296" cy="268" r="10" fill="#e3445f" />' +
              '<circle cx="324" cy="264" r="10" fill="#4058d8" />' +
              '<circle cx="348" cy="270" r="8" fill="#d63052" />',
            "#1683c7"
          )
        };
      case "hummus_carrots":
        return {
          bgA: "#eef8ef",
          bgB: "#fff5e7",
          accent: "#2f8b5c",
          artwork:
            bowlScene(
              "#e5d0a7",
              '<ellipse cx="320" cy="220" rx="90" ry="20" fill="#e8cf9d" />' +
                '<path d="M270 218C294 194 344 194 370 220" fill="none" stroke="#d8bf87" stroke-width="6" stroke-linecap="round" />' +
                '<path d="M238 174L254 286" stroke="#ef7a38" stroke-width="18" stroke-linecap="round" />' +
                '<path d="M262 170L282 286" stroke="#f2943c" stroke-width="18" stroke-linecap="round" />' +
                '<path d="M404 174L388 286" stroke="#ef7a38" stroke-width="18" stroke-linecap="round" />',
              "#2f8b5c"
            )
        };
      case "trail_mix":
        return {
          bgA: "#fff6e9",
          bgB: "#f3f7ff",
          accent: "#8e5a2d",
          artwork: pouchScene(
            "#f1d4a9",
            '<circle cx="290" cy="254" r="18" fill="#955d35" />' +
              '<ellipse cx="330" cy="246" rx="16" ry="12" fill="#b97e44" />' +
              '<circle cx="360" cy="270" r="12" fill="#d7b06d" />' +
              '<ellipse cx="332" cy="282" rx="22" ry="10" fill="#7f4f27" />',
            "#8e5a2d"
          )
        };
      case "popcorn":
        return {
          bgA: "#f6fbef",
          bgB: "#fff1d7",
          accent: "#e27b2e",
          artwork:
            plateShadow(132, 364) +
            '<path d="M260 188H380L360 334H280Z" fill="#ffffff" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<rect x="272" y="198" width="22" height="122" fill="#ef6b42" />' +
            '<rect x="308" y="198" width="22" height="122" fill="#ef6b42" />' +
            '<rect x="344" y="198" width="22" height="122" fill="#ef6b42" />' +
            '<circle cx="286" cy="174" r="22" fill="#fff3ba" />' +
            '<circle cx="318" cy="162" r="24" fill="#fff0a0" />' +
            '<circle cx="350" cy="176" r="22" fill="#fff4c4" />' +
            '<circle cx="332" cy="194" r="18" fill="#fff0a0" />'
        };
      case "banana_oat":
        return {
          bgA: "#f3fbef",
          bgB: "#fff3de",
          accent: "#b88a1c",
          artwork:
            plateShadow(138, 364) +
            '<ellipse cx="320" cy="266" rx="118" ry="60" fill="#fffaf3" stroke="rgba(17,34,40,0.09)" stroke-width="3" />' +
            '<rect x="244" y="232" width="58" height="42" rx="21" fill="#a26b3d" />' +
            '<rect x="314" y="232" width="58" height="42" rx="21" fill="#8d5a2f" />' +
            '<path d="M284 200C302 184 328 182 350 196" fill="none" stroke="#f2d560" stroke-width="20" stroke-linecap="round" />' +
            '<circle cx="274" cy="292" r="14" fill="#f0dba2" />' +
            '<circle cx="320" cy="304" r="14" fill="#f0dba2" />' +
            '<circle cx="364" cy="292" r="14" fill="#f0dba2" />'
        };
      case "salad_kit":
        return {
          bgA: "#eaf8ef",
          bgB: "#fdf6e7",
          accent: "#1b8e57",
          artwork:
            bowlScene(
              "#9ed886",
              '<circle cx="276" cy="216" r="24" fill="#69b85b" />' +
                '<circle cx="308" cy="228" r="26" fill="#57ac55" />' +
                '<circle cx="338" cy="214" r="24" fill="#6abf5d" />' +
                '<circle cx="364" cy="228" r="22" fill="#7fcf70" />' +
                '<circle cx="294" cy="236" r="10" fill="#ef5a47" />' +
                '<circle cx="340" cy="240" r="10" fill="#ef5a47" />',
              "#1b8e57"
            )
        };
      case "lentil_bowl":
        return {
          bgA: "#eef7ef",
          bgB: "#fff0e6",
          accent: "#2d7d67",
          artwork:
            bowlScene(
              "#d5c59d",
              '<path d="M236 222C260 196 304 190 334 212C358 228 392 230 404 216" fill="none" stroke="#84b559" stroke-width="20" stroke-linecap="round" />' +
                '<ellipse cx="314" cy="224" rx="58" ry="22" fill="#7a5b36" />' +
                '<circle cx="280" cy="220" r="7" fill="#9a7a4d" />' +
                '<circle cx="302" cy="216" r="7" fill="#9a7a4d" />' +
                '<circle cx="326" cy="228" r="7" fill="#9a7a4d" />' +
                '<ellipse cx="368" cy="232" rx="26" ry="18" fill="#efe4c4" />',
              "#2d7d67"
            )
        };
      case "tofu_kit":
        return {
          bgA: "#eef7ff",
          bgB: "#fef3e6",
          accent: "#1c7e6f",
          artwork:
            trayScene(
              "#f7faf6",
              '<rect x="236" y="194" width="78" height="48" rx="14" fill="#efe4cf" />' +
                '<rect x="244" y="202" width="22" height="18" rx="4" fill="#fff6e4" />' +
                '<rect x="272" y="202" width="22" height="18" rx="4" fill="#fff6e4" />' +
                '<rect x="258" y="224" width="22" height="18" rx="4" fill="#fff6e4" />' +
                '<rect x="326" y="194" width="76" height="48" rx="14" fill="#d7f0ca" />' +
                '<circle cx="348" cy="214" r="14" fill="#ef5a47" />' +
                '<circle cx="374" cy="214" r="14" fill="#f0c14d" />' +
                '<circle cx="360" cy="232" r="14" fill="#4db866" />' +
                '<rect x="248" y="254" width="142" height="44" rx="18" fill="#f0ead6" />'
            )
        };
      case "frozen_veg":
        return {
          bgA: "#edf7ff",
          bgB: "#effcf4",
          accent: "#2f76c7",
          artwork: pouchScene(
            "#c8e7f6",
            '<circle cx="286" cy="252" r="14" fill="#63b95f" />' +
              '<circle cx="322" cy="250" r="14" fill="#ef7a38" />' +
              '<circle cx="352" cy="268" r="14" fill="#7ac7ef" />' +
              '<path d="M324 212V244M308 228H340M313 217L335 239M335 217L313 239" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.9" />',
            "#2f76c7"
          )
        };
      case "fruit_cup":
        return {
          bgA: "#eef9ef",
          bgB: "#fff2df",
          accent: "#25a76a",
          artwork: cupScene(
            '<rect x="272" y="188" width="96" height="122" rx="14" fill="rgba(255,255,255,0.26)" />' +
              '<circle cx="292" cy="222" r="18" fill="#f05b43" />' +
              '<circle cx="336" cy="224" r="18" fill="#f6c84f" />' +
              '<circle cx="314" cy="262" r="20" fill="#63bc64" />' +
              '<circle cx="348" cy="268" r="16" fill="#ef7a94" />',
            "#25a76a"
          )
        };
      case "egg_box":
        return {
          bgA: "#eef9f1",
          bgB: "#fff3e6",
          accent: "#2f8065",
          artwork:
            trayScene(
              "#f8faf5",
              '<rect x="236" y="194" width="82" height="50" rx="16" fill="#f1ead7" />' +
                '<ellipse cx="262" cy="219" rx="16" ry="20" fill="#f5f0df" />' +
                '<ellipse cx="292" cy="219" rx="16" ry="20" fill="#f5f0df" />' +
                '<rect x="332" y="194" width="72" height="50" rx="16" fill="#e5f3d9" />' +
                '<circle cx="352" cy="214" r="13" fill="#7fc863" />' +
                '<circle cx="378" cy="214" r="13" fill="#a34db8" />' +
                '<circle cx="366" cy="234" r="13" fill="#ef7a38" />' +
                '<rect x="248" y="258" width="144" height="42" rx="18" fill="#ffffff" opacity="0.68" />'
            )
        };
      case "chicken_rice":
        return {
          bgA: "#eef8ef",
          bgB: "#fff0e5",
          accent: "#2d7a69",
          artwork:
            bowlScene(
              "#efe2bf",
              '<ellipse cx="288" cy="224" rx="40" ry="18" fill="#fbf3dc" />' +
                '<rect x="316" y="206" width="26" height="20" rx="8" fill="#cf7d3c" />' +
                '<rect x="346" y="212" width="26" height="20" rx="8" fill="#bb6d33" />' +
                '<rect x="332" y="236" width="26" height="20" rx="8" fill="#cf7d3c" />' +
                '<path d="M240 236C264 214 284 208 304 216" fill="none" stroke="#77b85f" stroke-width="14" stroke-linecap="round" />',
              "#2d7a69"
            )
        };
      case "tuna_pack":
        return {
          bgA: "#edf7ff",
          bgB: "#fff4e7",
          accent: "#2c7fc7",
          artwork:
            plateShadow(142, 364) +
            '<ellipse cx="288" cy="266" rx="66" ry="38" fill="#d9ecfb" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<ellipse cx="288" cy="266" rx="50" ry="24" fill="#72b8e6" />' +
            '<path d="M256 256C274 246 298 246 318 256" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" />' +
            '<rect x="332" y="224" width="74" height="18" rx="9" fill="#efd5ad" />' +
            '<rect x="332" y="250" width="74" height="18" rx="9" fill="#efd5ad" />' +
            '<rect x="332" y="276" width="74" height="18" rx="9" fill="#efd5ad" />'
        };
      case "turkey_wrap":
        return {
          bgA: "#eef9ef",
          bgB: "#fff1e2",
          accent: "#2a815f",
          artwork:
            plateShadow(144, 364) +
            '<path d="M220 298L282 202L344 298Z" fill="#efd1a2" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<path d="M296 298L358 202L420 298Z" fill="#efd1a2" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<path d="M252 246C270 224 292 220 314 232" fill="none" stroke="#6dbd63" stroke-width="14" stroke-linecap="round" />' +
            '<path d="M324 246C342 224 364 220 386 232" fill="none" stroke="#6dbd63" stroke-width="14" stroke-linecap="round" />' +
            '<path d="M254 262C270 254 286 254 300 262" fill="none" stroke="#d67c52" stroke-width="10" stroke-linecap="round" />' +
            '<path d="M326 262C342 254 358 254 372 262" fill="none" stroke="#d67c52" stroke-width="10" stroke-linecap="round" />'
        };
      case "chicken_pack":
        return {
          bgA: "#eef8ef",
          bgB: "#fff2e5",
          accent: "#258165",
          artwork:
            trayScene(
              "#edf7ef",
              '<path d="M248 220C258 198 284 194 304 210C318 220 318 244 304 254C284 268 254 258 248 220Z" fill="#d78953" />' +
                '<path d="M324 226C332 206 354 200 372 214C384 224 384 244 372 254C354 266 330 258 324 226Z" fill="#cf7a46" />' +
                '<path d="M274 198C290 194 304 200 314 214" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="6" stroke-linecap="round" />' +
                '<path d="M350 206C364 206 374 212 382 224" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="6" stroke-linecap="round" />'
            )
        };
      case "wheat_bread":
        return {
          bgA: "#fff7e7",
          bgB: "#eef7ef",
          accent: "#8a5b2d",
          artwork:
            breadScene(
              "#bb7a3c",
              '<rect x="236" y="208" width="42" height="90" rx="16" fill="#d9a564" opacity="0.9" />' +
                '<rect x="362" y="208" width="42" height="90" rx="16" fill="#d9a564" opacity="0.9" />'
            )
        };
      case "wraps":
        return {
          bgA: "#fff7ea",
          bgB: "#eef7f1",
          accent: "#a96a2f",
          artwork:
            plateShadow(144, 364) +
            '<circle cx="284" cy="252" r="58" fill="#efd4aa" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<circle cx="360" cy="268" r="58" fill="#f3dbb7" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<path d="M248 252C270 236 296 236 316 252" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="6" stroke-linecap="round" />' +
            '<path d="M324 268C346 252 372 252 392 268" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="6" stroke-linecap="round" />'
        };
      case "bagels":
        return {
          bgA: "#fff7e8",
          bgB: "#eef8f0",
          accent: "#946030",
          artwork:
            plateShadow(142, 364) +
            '<circle cx="280" cy="252" r="56" fill="#d6a06a" />' +
            '<circle cx="280" cy="252" r="18" fill="#f4efe3" />' +
            '<circle cx="356" cy="264" r="56" fill="#cf9460" />' +
            '<circle cx="356" cy="264" r="18" fill="#f4efe3" />' +
            '<circle cx="270" cy="232" r="4" fill="#8b5c2d" />' +
            '<circle cx="292" cy="276" r="4" fill="#8b5c2d" />' +
            '<circle cx="340" cy="246" r="4" fill="#8b5c2d" />' +
            '<circle cx="372" cy="282" r="4" fill="#8b5c2d" />'
        };
      case "pita":
        return {
          bgA: "#fff8eb",
          bgB: "#edf8f0",
          accent: "#8c6130",
          artwork:
            plateShadow(144, 364) +
            '<path d="M234 298C240 240 288 210 334 228C364 240 390 270 398 298Z" fill="#e6c08c" />' +
            '<path d="M212 286C220 238 264 210 306 228C336 242 360 270 366 298Z" fill="#efd2a7" />' +
            '<path d="M258 304C264 248 312 218 358 236C388 248 412 276 420 304Z" fill="#f4ddb8" />'
        };
      case "rice":
        return {
          bgA: "#eef7ff",
          bgB: "#fff4e8",
          accent: "#1f7cb5",
          artwork: pouchScene(
            "#d9ebf7",
            '<ellipse cx="320" cy="264" rx="54" ry="26" fill="#f9f3df" />' +
              '<path d="M284 260C300 248 320 248 336 260" fill="none" stroke="#d9cda7" stroke-width="6" stroke-linecap="round" />' +
              '<path d="M292 278C308 266 328 266 344 278" fill="none" stroke="#d9cda7" stroke-width="6" stroke-linecap="round" />',
            "#1f7cb5"
          )
        };
      case "beans":
        return {
          bgA: "#eef8ef",
          bgB: "#fff3e6",
          accent: "#2b8468",
          artwork:
            plateShadow(138, 364) +
            '<rect x="234" y="198" width="102" height="122" rx="20" fill="#8cb5d2" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<rect x="234" y="198" width="102" height="26" rx="12" fill="#d6e7f3" />' +
            '<ellipse cx="370" cy="274" rx="54" ry="34" fill="#fffaf3" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<ellipse cx="370" cy="264" rx="38" ry="16" fill="#3d2720" />' +
            '<ellipse cx="358" cy="262" rx="8" ry="6" fill="#6a4736" />' +
            '<ellipse cx="380" cy="268" rx="8" ry="6" fill="#6a4736" />'
        };
      case "oats":
        return {
          bgA: "#eef8ef",
          bgB: "#fff4e5",
          accent: "#278468",
          artwork:
            plateShadow(138, 364) +
            '<rect x="242" y="182" width="96" height="132" rx="22" fill="#6eb89e" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<rect x="258" y="162" width="64" height="26" rx="13" fill="#57a486" />' +
            '<ellipse cx="372" cy="274" rx="58" ry="34" fill="#fffaf2" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<ellipse cx="372" cy="264" rx="42" ry="18" fill="#ead6a8" />' +
            '<circle cx="348" cy="260" r="5" fill="#d7ba76" />' +
            '<circle cx="372" cy="258" r="5" fill="#d7ba76" />' +
            '<circle cx="392" cy="266" r="5" fill="#d7ba76" />'
        };
      case "pasta":
        return {
          bgA: "#eef7ff",
          bgB: "#fff3e4",
          accent: "#277fc4",
          artwork: cartonScene(
            "#7db8eb",
            '<rect x="286" y="208" width="82" height="86" rx="16" fill="rgba(255,255,255,0.28)" />' +
              '<path d="M300 232C320 210 340 210 350 226C360 242 348 258 328 264C308 270 294 252 300 232Z" fill="none" stroke="#f6df7f" stroke-width="10" stroke-linecap="round" />' +
              '<path d="M300 276C320 254 340 254 350 270C360 286 348 302 328 308C308 314 294 296 300 276Z" fill="none" stroke="#f6df7f" stroke-width="10" stroke-linecap="round" />'
          )
        };
      case "milk":
        return {
          bgA: "#eef7ff",
          bgB: "#eefbf2",
          accent: "#2581c4",
          artwork:
            plateShadow(136, 364) +
            '<path d="M254 160H338L360 190V336H254Z" fill="#9dd1f7" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<path d="M338 160V190H360" fill="rgba(255,255,255,0.3)" />' +
            '<rect x="268" y="206" width="76" height="86" rx="18" fill="rgba(255,255,255,0.28)" />' +
            '<path d="M390 220H426L418 318H398Z" fill="#ffffff" stroke="rgba(17,34,40,0.1)" stroke-width="3" />' +
            '<path d="M390 220C398 204 418 204 426 220" fill="#ffffff" />'
        };
      case "solo_box":
        return {
          bgA: "#eef9ef",
          bgB: "#fff4e6",
          accent: "#24805f",
          artwork: boxScene(
            "#d0ad78",
            "#c29559",
            '<circle cx="270" cy="240" r="22" fill="#68b95e" />' +
              '<circle cx="320" cy="232" r="20" fill="#f05b43" />' +
              '<rect x="350" y="214" width="28" height="52" rx="10" fill="#8cc4ec" />' +
              '<ellipse cx="320" cy="288" rx="94" ry="18" fill="rgba(255,255,255,0.2)" />'
          )
        };
      case "produce_box":
        return {
          bgA: "#eef9ef",
          bgB: "#fff7e8",
          accent: "#23875d",
          artwork: boxScene(
            "#ccab73",
            "#be9758",
            '<circle cx="268" cy="236" r="20" fill="#5eb55b" />' +
              '<circle cx="308" cy="226" r="18" fill="#f6c84f" />' +
              '<circle cx="348" cy="236" r="18" fill="#ef7a38" />' +
              '<circle cx="324" cy="266" r="18" fill="#4aa860" />'
          )
        };
      case "protein_box":
        return {
          bgA: "#eef8ef",
          bgB: "#fff2e5",
          accent: "#248163",
          artwork: boxScene(
            "#cdaa76",
            "#c29156",
            '<ellipse cx="274" cy="240" rx="18" ry="22" fill="#f2eddc" />' +
              '<ellipse cx="308" cy="236" rx="18" ry="22" fill="#f2eddc" />' +
              '<rect x="334" y="220" width="30" height="48" rx="10" fill="#c97943" />' +
              '<ellipse cx="354" cy="278" rx="22" ry="12" fill="#3c2a22" />'
          )
        };
      case "family_box":
        return {
          bgA: "#eef9ef",
          bgB: "#fff2e4",
          accent: "#21805f",
          artwork: boxScene(
            "#c8a36e",
            "#bb8d4e",
            '<circle cx="262" cy="232" r="18" fill="#5cb85c" />' +
              '<circle cx="300" cy="226" r="16" fill="#ef5b43" />' +
              '<rect x="330" y="214" width="34" height="54" rx="12" fill="#8cc4ec" />' +
              '<ellipse cx="386" cy="236" rx="18" ry="22" fill="#f1ecd9" />' +
              '<rect x="286" y="264" width="72" height="16" rx="8" fill="rgba(255,255,255,0.24)" />'
          )
        };
      default:
        return {
          bgA: "#eef8ef",
          bgB: "#fff2e6",
          accent: "#227d64",
          artwork:
            plateShadow(140, 364) +
            '<circle cx="320" cy="252" r="78" fill="rgba(255,255,255,0.7)" stroke="rgba(17,34,40,0.08)" stroke-width="3" />' +
            '<text x="320" y="264" text-anchor="middle" fill="#153c35" font-size="54" font-family="Segoe UI, Arial, sans-serif" font-weight="800">' +
            escapeXml(abbreviateLabel(item.name, "MW")) +
            "</text>"
        };
    }
  }

  function itemIllustrationUrl(item) {
    if (itemImageCache[item.id]) {
      return itemImageCache[item.id];
    }

    const scene = sceneFor(item);
    const title = shortenText(item.name, 34);
    const unit = shortenText(item.unit, 32);
    const portion = shortenText(item.portion, 22);
    const category = data.categoryMeta[item.cat] ? data.categoryMeta[item.cat].short : "Food";

    const svg =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="' +
      escapeXml(item.name) +
      '">' +
      "<defs>" +
      '<linearGradient id="bg" x1="0%" x2="100%" y1="0%" y2="100%">' +
      '<stop offset="0%" stop-color="' +
      scene.bgA +
      '" />' +
      '<stop offset="100%" stop-color="' +
      scene.bgB +
      '" />' +
      "</linearGradient>" +
      "</defs>" +
      '<rect width="640" height="480" rx="34" fill="url(#bg)" />' +
      '<circle cx="96" cy="84" r="78" fill="rgba(255,255,255,0.55)" />' +
      '<circle cx="546" cy="84" r="54" fill="rgba(255,255,255,0.32)" />' +
      '<rect x="30" y="28" width="178" height="40" rx="20" fill="rgba(255,255,255,0.82)" />' +
      '<text x="48" y="54" fill="' +
      scene.accent +
      '" font-size="20" font-family="Segoe UI, Arial, sans-serif" font-weight="800">' +
      escapeXml(portion) +
      "</text>" +
      '<text x="64" y="106" fill="rgba(16,34,40,0.45)" font-size="16" font-family="Segoe UI, Arial, sans-serif" font-weight="700" letter-spacing="1.6">' +
      escapeXml(category.toUpperCase()) +
      "</text>" +
      scene.artwork +
      '<rect x="30" y="384" width="580" height="70" rx="24" fill="rgba(255,255,255,0.82)" />' +
      '<text x="54" y="416" fill="#122d2a" font-size="28" font-family="Segoe UI, Arial, sans-serif" font-weight="800">' +
      escapeXml(title) +
      "</text>" +
      '<text x="54" y="442" fill="rgba(16,34,40,0.68)" font-size="18" font-family="Segoe UI, Arial, sans-serif" font-weight="700">' +
      escapeXml(unit) +
      "</text>" +
      "</svg>";

    itemImageCache[item.id] = svgDataUrl(svg);
    return itemImageCache[item.id];
  }

  root.utils = {
    abbreviateLabel: abbreviateLabel,
    buildDirectionsUrl: buildDirectionsUrl,
    buildGoogleEmbedUrl: buildGoogleEmbedUrl,
    buildGoogleSearchUrl: buildGoogleSearchUrl,
    buildStopUrl: buildStopUrl,
    escapeHtml: escapeHtml,
    escapeXml: escapeXml,
    formatCurrency: formatCurrency,
    geocodeLocal: geocodeLocal,
    haversineMiles: haversineMiles,
    itemIllustrationUrl: itemIllustrationUrl,
    normalizeQuery: normalizeQuery,
    stockFor: stockFor
  };
})();
