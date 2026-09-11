# data/raw/

**Owner:** Member 1

Untouched pulls from each source go here, one subfolder or file per source:

- `palaystat/` — raw SERBIS / PSA rice economy table exports
- `ricelytics/` — raw fertilizer/pesticide price and regional aggregate exports
- `nasa_power/` — raw climate query responses (rainfall, temperature, solar radiation, humidity)
- `soilgrids/` — raw soil pH query responses

This folder is gitignored (see root `.gitignore`) since raw pulls can be large or re-fetched directly from the source APIs/portals. Document exactly how to reproduce each pull (URL, query parameters, date accessed) in `docs/01_project_overview_and_architecture.md` §4, not just in code comments.
