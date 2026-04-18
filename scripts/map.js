(function () {
  const root = window.MealsOnWheels || (window.MealsOnWheels = {});
  const utils = root.utils;

  function markerIcon(stop, isActive) {
    return L.divIcon({
      className: "hub-marker",
      html:
        '<div class="hub-pin' +
        (isActive ? " active" : "") +
        '">' +
        utils.escapeHtml(stop.shortLabel || stop.short) +
        "</div>",
      iconSize: [92, 36],
      iconAnchor: [46, 18]
    });
  }

  function popupMarkup(stop) {
    return (
      '<div class="map-popup">' +
      "<strong>" +
      utils.escapeHtml(stop.name) +
      "</strong>" +
      "<span>" +
      utils.escapeHtml(stop.area) +
      "</span>" +
      "<span>" +
      utils.escapeHtml(stop.type) +
      "</span>" +
      "</div>"
    );
  }

  function createCoverageMap(options) {
    const map = L.map(options.elementId, {
      zoomControl: false,
      scrollWheelZoom: true,
      minZoom: 10
    });

    L.control.zoom({ position: "topright" }).addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    const stopGroup = L.featureGroup().addTo(map);
    const originGroup = L.layerGroup().addTo(map);
    const stopLayers = new Map();

    function fitToNetwork() {
      if (!stopGroup.getLayers().length) {
        return;
      }

      map.fitBounds(stopGroup.getBounds().pad(0.15));
    }

    function setStops(stops, activeStopId) {
      stopGroup.clearLayers();
      stopLayers.clear();

      stops.forEach(function (stop) {
        const isActive = stop.id === activeStopId;
        const circle = L.circle([stop.lat, stop.lng], {
          radius: options.radiusMeters,
          color: isActive ? "#d86c34" : "#1a6a59",
          fillColor: isActive ? "#f3b44d" : "#3aa083",
          fillOpacity: isActive ? 0.18 : 0.11,
          weight: isActive ? 2 : 1.5
        });

        const marker = L.marker([stop.lat, stop.lng], {
          icon: markerIcon(stop, isActive),
          title: stop.name,
          keyboard: true
        });

        circle.addTo(stopGroup);
        marker.addTo(stopGroup);

        marker.bindPopup(popupMarkup(stop));

        circle.on("click", function () {
          options.onSelectStop(stop.id);
        });

        marker.on("click", function () {
          options.onSelectStop(stop.id);
        });

        stopLayers.set(stop.id, {
          stop: stop,
          circle: circle,
          marker: marker
        });
      });

      fitToNetwork();
    }

    function setActiveStop(stopId, focusMap) {
      stopLayers.forEach(function (entry) {
        const isActive = entry.stop.id === stopId;

        entry.circle.setStyle({
          color: isActive ? "#d86c34" : "#1a6a59",
          fillColor: isActive ? "#f3b44d" : "#3aa083",
          fillOpacity: isActive ? 0.18 : 0.11,
          weight: isActive ? 2 : 1.5
        });

        entry.marker.setIcon(markerIcon(entry.stop, isActive));

        if (isActive && focusMap !== false) {
          const nextZoom = Math.max(map.getZoom(), 12);
          map.flyTo([entry.stop.lat, entry.stop.lng], nextZoom, { duration: 0.45 });
          entry.marker.openPopup();
        }
      });
    }

    function setOrigin(origin) {
      originGroup.clearLayers();

      if (!origin || typeof origin.lat !== "number" || typeof origin.lng !== "number") {
        return;
      }

      const marker = L.marker([origin.lat, origin.lng], {
        icon: L.divIcon({
          className: "hub-marker",
          html: '<div class="origin-dot"></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        }),
        keyboard: false
      });

      marker.bindTooltip(origin.label, {
        direction: "top",
        offset: [0, -12]
      });

      marker.addTo(originGroup);
    }

    return {
      fitToNetwork: fitToNetwork,
      setActiveStop: setActiveStop,
      setOrigin: setOrigin,
      setStops: setStops
    };
  }

  root.createCoverageMap = createCoverageMap;
})();
