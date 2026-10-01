# Data Dictionary — merged rice yield dataset

This file documents the final merged dataset in [data/processed/merged_rice_yield_dataset.csv](../data/processed/merged_rice_yield_dataset.csv). The table was assembled from the cleaned yield, harvested-area, fertilizer, and climate sources and includes the simulated soil pH layer required for the model.

## Final schema

| Column | Type | Source | Unit / values | Notes |
|---|---|---|---|---|
| season_period | categorical | normalized from yield + fertilizer season labels | `2021_Semester_2`, `2022_Semester_1` | Used as the merge key along with ecosystem |
| ecosystem | categorical | normalized yield/area source labels | `Irrigated`, `Non-irrigated` | Normalized from source-specific casing differences |
| island_group | categorical | climate source province mapping | `Luzon`, `Visayas`, `Mindanao` | Used instead of raw province in the model to preserve leave-one-province-out validity |
| yield_mt_ha | float | yield source | metric tons per hectare | Target variable; no missing values in the final dataset |
| area_harvested_ha | float | harvested-area source | hectares | Province-level harvested area for the relevant season |
| n_application_rate | float | fertilizer by-element source | kg/ha | Nitrogen application rate |
| p_application_rate | float | fertilizer by-element source | kg/ha | Phosphorus application rate |
| k_application_rate | float | fertilizer by-element source | kg/ha | Potassium application rate |
| grade_ammophos_16_20_0_kg_ha | float | fertilizer by-grade source | kg/ha | Ranked grade product after reshaping and pivoting |
| grade_ammosul_21_0_0_kg_ha | float | fertilizer by-grade source | kg/ha | Ranked grade product after reshaping and pivoting |
| grade_complete_14_14_14_kg_ha | float | fertilizer by-grade source | kg/ha | Ranked grade product after reshaping and pivoting |
| grade_mop_0_0_60_kg_ha | float | fertilizer by-grade source | kg/ha | Ranked grade product after reshaping and pivoting |
| grade_urea_46_0_0_kg_ha | float | fertilizer by-grade source | kg/ha | Ranked grade product after reshaping and pivoting |
| total_fertilizer_kg_ha | float | derived from by-grade columns | kg/ha | Sum of all five by-grade fertilizer columns |
| fertilizer_diversification_index | float | derived from grade shares | entropy index | Shannon diversity across the five grade shares |
| rainfall_mm | float | climate source | mm | Season total rainfall, aggregated over the period |
| temp_max_c | float | climate source | °C | Mean daily maximum temperature during the season |
| temp_min_c | float | climate source | °C | Mean daily minimum temperature during the season |
| solar_radiation_mj_m2 | float | climate source | MJ/m² | Mean daily shortwave radiation for the season |
| soil_ph | float | simulated layer | pH units | Generated per province + ecosystem with a fixed random seed, anchored roughly between 5.0 and 6.5; not a direct field measurement |

## Assumptions and notes

- The fertilizer by-element values are treated as kg/ha, following the agronomic magnitude of the source tables. The documentation in the raw files says "in kg," though the project treats them as kg/ha for modeling consistency.
- The final model uses island_group rather than raw province because province-level one-hot encoding breaks leave-one-province-out validation whenever the held-out province has no training examples in that dummy feature.
- Provinces absent from a source were removed by the merge naturally; this includes cases such as Basilan not appearing in the fertilizer tables.
- Nulls inside a source were resolved as 0 where a missing value meant “no recorded application/grade” rather than a missing observation. This preserves the meaning of zero usage without introducing false missingness.
- soil_ph is a simulated feature. It is included because the project contract requires a soil layer, but it is not measured data.

## Province-to-island_group rationale

The climate source already includes the island_group value for each province, so the final merged table uses that geography field directly. This is a better representation for modeling than a raw province label because the dataset is small and province-level one-hot encoding creates fragile train/test splits under leave-one-province-out evaluation.
