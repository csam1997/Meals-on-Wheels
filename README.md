# Meals on Wheels DC

Static frontend prototype for a DC-wide grocery coverage network.

## What changed

- Rebuilt the page around citywide grocery access instead of a campus-first story.
- Split the old single-file prototype into dedicated HTML, CSS, and JavaScript files.
- Replaced the single-stop map flow with a multi-stop coverage map that shows every pit stop and every 1-mile service ring at once.
- Kept Google Maps links for per-stop navigation while moving the main coverage experience into the page itself.

## File structure

- `index.html` - page structure and section layout
- `styles/main.css` - visual system, responsive layout, map styling, and drawer styles
- `scripts/data.js` - pit stop data, catalog data, and local search aliases
- `scripts/utils.js` - shared formatting, distance, stock, and lookup helpers
- `scripts/map.js` - Leaflet map setup and pit stop coverage rendering
- `scripts/app.js` - UI state, rendering, cart behavior, and event wiring

## Notes

- This is still a static prototype with demo checkout behavior.
- The map uses Leaflet with OpenStreetMap tiles for the multi-stop coverage view.
- Google Maps links remain available for single-stop directions.
