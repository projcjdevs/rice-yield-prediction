# Data Dictionary

One row represents a province-season-ecosystem observation. `province` is retained for auditability and leave-one-province-out grouping; use `island_group` as the geographic model feature. See `province_reconciliation.csv` and `sourcing_audit.json`.

By-element source headers say `kg` without an explicit per-hectare denominator. Treating those values as `kg/ha` is an assumption based on plausible magnitudes, not a confirmed source unit. `soil_ph` is simulated, reproducible, and not a measurement.

## Columns

| Column | Description / source | Unit or type |
|---|---|---|
| `season_period` | PSA yield period/year matched to the corresponding fertilizer season. | category |
| `ecosystem` | PSA rice ecosystem. | category |
| `province` | See source audit. | source-derived |
| `island_group` | PSGC island group; used instead of raw province for geographic modeling. | category |
| `yield_mt_ha` | Average palay yield from PSA. | metric tons/ha |
| `area_harvested_ha` | Rice area harvested from PSA; see source definition. | as reported |
| `n_application_rate` | Nitrogen rate. Source says kg; per-hectare interpretation is assumed, not confirmed. | assumed kg/ha |
| `p_application_rate` | Phosphorus rate. Source says kg; per-hectare interpretation is assumed, not confirmed. | assumed kg/ha |
| `k_application_rate` | Potassium rate. Source says kg; per-hectare interpretation is assumed, not confirmed. | assumed kg/ha |
| `grade_ammophos_16_20_0_kg_ha` | Quantity of reported top-five grade ammophos 16 20 0; absent means unlisted, not proven zero use. | assumed kg/ha |
| `grade_ammosul_21_0_0_kg_ha` | Quantity of reported top-five grade ammosul 21 0 0; absent means unlisted, not proven zero use. | assumed kg/ha |
| `grade_complete_14_14_14_kg_ha` | Quantity of reported top-five grade complete 14 14 14; absent means unlisted, not proven zero use. | assumed kg/ha |
| `grade_mop_0_0_60_kg_ha` | Quantity of reported top-five grade mop 0 0 60; absent means unlisted, not proven zero use. | assumed kg/ha |
| `grade_urea_46_0_0_kg_ha` | Quantity of reported top-five grade urea 46 0 0; absent means unlisted, not proven zero use. | assumed kg/ha |
| `total_fertilizer_kg_ha` | Sum of listed top-five fertilizer grades; inherits the unit assumption. | assumed kg/ha |
| `fertilizer_diversification_index` | Shannon entropy of shares among listed top-five grades. | dimensionless |
| `rainfall_mm` | Semester total daily precipitation from Open-Meteo archive. | mm |
| `temp_max_c` | Mean daily maximum temperature over semester. | deg C |
| `temp_min_c` | Mean daily minimum temperature over semester. | deg C |
| `solar_radiation_mj_m2` | Mean daily shortwave radiation over semester. | MJ/m^2/day |
| `soil_ph` | Fixed-seed simulated proxy per province/ecosystem; not measured. | simulated pH |
