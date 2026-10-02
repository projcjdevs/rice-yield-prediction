# Data Dictionary — merged_rice_yield_dataset.csv

This file documents the final merged dataset in [merged_rice_yield_dataset.csv](merged_rice_yield_dataset.csv). The table was assembled from the cleaned yield, area, fertilizer, and climate sources and includes the simulated soil pH layer required for the project model.

## Final schema

| Column | Type | Source | Unit / values | Notes |
|---|---|---|---|---|
| season_period | categorical | normalized season labels | `2021_Semester_2`, `2022_Semester_1` | merge key |
| ecosystem | categorical | normalized yield + area source labels | `Irrigated`, `Non-irrigated` | normalized casing |
| province | categorical | yield and harvested-area source | province names | retained for auditability and leave-one-province-out grouping; exclude from model features |
| island_group | categorical | climate province mapping | `Luzon`, `Visayas`, `Mindanao` | geographic model feature |
| yield_mt_ha | float | yield source | metric tons per hectare | target variable; zero missing values |
| area_harvested_ha | float | harvested-area source | hectares | season-specific provincial area |
| n_application_rate | float | fertilizer by-element source | kg/ha | nitrogen |
| p_application_rate | float | fertilizer by-element source | kg/ha | phosphorus |
| k_application_rate | float | fertilizer by-element source | kg/ha | potassium |
| grade_ammophos_16_20_0_kg_ha | float | fertilizer by-grade source | kg/ha | reshaped product column |
| grade_ammosul_21_0_0_kg_ha | float | fertilizer by-grade source | kg/ha | reshaped product column |
| grade_complete_14_14_14_kg_ha | float | fertilizer by-grade source | kg/ha | reshaped product column |
| grade_mop_0_0_60_kg_ha | float | fertilizer by-grade source | kg/ha | reshaped product column |
| grade_urea_46_0_0_kg_ha | float | fertilizer by-grade source | kg/ha | reshaped product column |
| total_fertilizer_kg_ha | float | derived | kg/ha | sum of all five grade columns |
| fertilizer_diversification_index | float | derived | entropy index | Shannon diversity of the five grade shares |
| rainfall_mm | float | climate source | mm | season total |
| temp_max_c | float | climate source | °C | mean daily maximum |
| temp_min_c | float | climate source | °C | mean daily minimum |
| solar_radiation_mj_m2 | float | climate source | MJ/m² | mean daily shortwave radiation |
| soil_ph | float | simulated value | pH units | generated per province + ecosystem using a fixed random seed, not measured |

## Assumptions and handling notes

- The fertilizer by-element values are treated as kg/ha, even though the raw file label says "in kg". This follows the project agronomic assumption and the final model input design.
- The model uses `island_group` as its geographic feature; `province` remains available for auditability and leave-one-province-out grouping, not feature encoding.
- Source-coverage gaps were not filled; they were left out by the merge. Basilan is the clearest example of a legitimate data gap in the fertilizer tables.
- In-source missing values were set to 0 when the missing value meant “no usage recorded,” rather than dropping rows outright.
- soil_ph is intentionally disclosed as a synthetic modeled feature anchored roughly between 5.0 and 6.5 and slightly less acidic in irrigated ecosystems.

## Data quality summary

- Final row count: 287
- Target variable `yield_mt_ha`: no missing values
- Overall merged feature set: no nulls
- Province/scope coverage: consistent with the final trimmed set used in the project's contract deliverable
