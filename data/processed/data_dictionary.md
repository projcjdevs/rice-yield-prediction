# Data Dictionary — merged_rice_yield_dataset.csv

**Owner:** Member 1. Fill in as the merge is finalized — this is required for Contract 1 handoff.

| Column | Type | Source | Unit / Values | Missing-value handling | Notes |
|---|---|---|---|---|---|
| province | categorical | PalayStat/PSA | | | |
| region | categorical | Ricelytics | | | |
| year | int | PalayStat/PSA | | | |
| season | categorical | PalayStat/PSA | wet / dry | | only if quarterly tables used |
| area_harvested_ha | float | PalayStat/PSA | hectares | | |
| fertilizer_total_kg_ha | float | PalayStat nutrient mgmt | kg/ha | | |
| fertilizer_cost_php_ha | float | PalayStat cost/returns or Ricelytics-FPA | PHP/ha | | fallback if quantity unavailable |
| rainfall_mm | float | NASA POWER | mm | | season-aligned if possible |
| avg_temp_c | float | NASA POWER | °C | | |
| solar_radiation | float | NASA POWER | | | include if consistently available |
| humidity_pct | float | NASA POWER | % | | |
| soil_ph | float | ISRIC SoilGrids | pH scale | | modeled estimate, not direct measurement |
| yield_kg_ha | float | PalayStat/PSA | kg/ha | none allowed | **target variable** |

## Known limitations
- (fill in — e.g. province-grouping changes across years, years with sparse survey coverage, etc.)
