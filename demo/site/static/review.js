// Draws the stored candidates and, only for a full region, the proposed circle.
// No coordinate or radius is computed here: everything comes from the page's JSON.
(function () {
  "use strict";
  function draw() {
    var el = document.getElementById("map");
    var dataEl = document.getElementById("map-data");
    if (!el || !dataEl || typeof L === "undefined") return;
    var data = JSON.parse(dataEl.textContent);
    var map = L.map(el, { scrollWheelZoom: false });
    L.tileLayer(
      "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 16, attribution: "USGS The National Map" }
    ).addTo(map);
    var bounds = [];
    data.candidates.forEach(function (c) {
      var marker = L.circleMarker([c.lat, c.lon], {
        radius: c.selected ? 8 : 6,
        weight: 2,
        color: c.selected ? "#b45309" : "#1d4ed8",
        fillOpacity: c.selected ? 0.9 : 0.5,
      }).addTo(map);
      marker.bindTooltip("#" + c.rank + " " + c.name + " (GNIS " + c.id + ")");
      bounds.push([c.lat, c.lon]);
    });
    if (data.circle) {
      // Bounds from the centre and radius: a circle's own getBounds needs a map view first.
      var centre = L.latLng(data.circle.lat, data.circle.lon);
      map.fitBounds(centre.toBounds(2 * data.circle.radius_m).pad(0.15));
      L.circle(centre, {
        radius: data.circle.radius_m,
        color: "#b45309",
        weight: 2,
        fillOpacity: 0.08,
      }).addTo(map);
    } else if (bounds.length) {
      map.fitBounds(L.latLngBounds(bounds).pad(0.3), { maxZoom: 12 });
    } else {
      map.setView([39.0, -105.5], 6); // Colorado, nothing to show
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw);
  else draw();
})();
