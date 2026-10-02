# EDA Findings

## Dataset profile

- Final dimensions: 287 rows x 21 columns.
- Duplicate rows: 0.
- Target nulls: 0.

|                                  |   count |   unique | top             |    freq |      mean |       std |     min |      25% |      50% |       75% |        max |
|:---------------------------------|--------:|---------:|:----------------|--------:|----------:|----------:|--------:|---------:|---------:|----------:|-----------:|
| season_period                    | 287.000 |    2.000 | 2021_Semester_2 | 149.000 |   nan     |   nan     | nan     |  nan     |  nan     |   nan     |    nan     |
| ecosystem                        | 287.000 |    2.000 | Irrigated       | 152.000 |   nan     |   nan     | nan     |  nan     |  nan     |   nan     |    nan     |
| province                         | 287.000 |   76.000 | Albay           |   4.000 |   nan     |   nan     | nan     |  nan     |  nan     |   nan     |    nan     |
| island_group                     | 287.000 |    3.000 | Luzon           | 135.000 |   nan     |   nan     | nan     |  nan     |  nan     |   nan     |    nan     |
| yield_mt_ha                      | 287.000 |  nan     | nan             | nan     |     3.610 |     0.851 |   1.220 |    3.040 |    3.590 |     4.245 |      6.770 |
| area_harvested_ha                | 287.000 |  nan     | nan             | nan     | 16150.258 | 24143.056 |  20.000 | 2108.000 | 8508.000 | 17586.000 | 153468.000 |
| n_application_rate               | 287.000 |  nan     | nan             | nan     |    74.644 |    20.217 |  16.950 |   62.510 |   77.050 |    87.550 |    129.650 |
| p_application_rate               | 287.000 |  nan     | nan             | nan     |    17.028 |     6.192 |   5.000 |   12.900 |   16.660 |    20.235 |     39.260 |
| k_application_rate               | 287.000 |  nan     | nan             | nan     |    16.599 |     6.323 |   5.030 |   11.750 |   16.070 |    20.110 |     36.270 |
| grade_ammophos_16_20_0_kg_ha     | 287.000 |  nan     | nan             | nan     |    17.705 |    16.477 |   0.000 |    4.290 |   13.040 |    26.270 |     77.870 |
| grade_ammosul_21_0_0_kg_ha       | 287.000 |  nan     | nan             | nan     |    28.398 |    32.618 |   0.000 |    2.205 |   16.030 |    46.920 |    142.830 |
| grade_complete_14_14_14_kg_ha    | 287.000 |  nan     | nan             | nan     |    80.355 |    39.834 |  23.350 |   55.255 |   70.190 |    97.610 |    264.120 |
| grade_mop_0_0_60_kg_ha           | 287.000 |  nan     | nan             | nan     |     4.725 |     6.338 |   0.000 |    0.000 |    2.080 |     6.670 |     26.250 |
| grade_urea_46_0_0_kg_ha          | 287.000 |  nan     | nan             | nan     |    91.855 |    44.164 |  14.870 |   58.490 |   83.830 |   113.230 |    244.500 |
| total_fertilizer_kg_ha           | 287.000 |  nan     | nan             | nan     |   223.037 |    91.588 |  47.000 |  161.125 |  208.650 |   277.460 |    599.780 |
| fertilizer_diversification_index | 287.000 |  nan     | nan             | nan     |     1.109 |     0.210 |   0.616 |    1.003 |    1.111 |     1.284 |      1.452 |
| rainfall_mm                      | 287.000 |  nan     | nan             | nan     |  1614.809 |   548.214 | 642.300 | 1199.400 | 1550.700 |  1939.150 |   3238.800 |
| temp_max_c                       | 287.000 |  nan     | nan             | nan     |    28.162 |     2.466 |  18.532 |   27.090 |   28.660 |    29.678 |     33.450 |
| temp_min_c                       | 287.000 |  nan     | nan             | nan     |    22.400 |     2.455 |  11.757 |   21.721 |   23.088 |    23.887 |     26.826 |
| solar_radiation_mj_m2            | 287.000 |  nan     | nan             | nan     |    17.821 |     1.397 |  14.820 |   16.879 |   17.546 |    18.806 |     21.136 |
| soil_ph                          | 287.000 |  nan     | nan             | nan     |     5.791 |     0.391 |   5.020 |    5.520 |    5.790 |     6.090 |      6.460 |

## Types and missing values

- `season_period`: `str`
- `ecosystem`: `str`
- `province`: `str`
- `island_group`: `str`
- `yield_mt_ha`: `float64`
- `area_harvested_ha`: `float64`
- `n_application_rate`: `float64`
- `p_application_rate`: `float64`
- `k_application_rate`: `float64`
- `grade_ammophos_16_20_0_kg_ha`: `float64`
- `grade_ammosul_21_0_0_kg_ha`: `float64`
- `grade_complete_14_14_14_kg_ha`: `float64`
- `grade_mop_0_0_60_kg_ha`: `float64`
- `grade_urea_46_0_0_kg_ha`: `float64`
- `total_fertilizer_kg_ha`: `float64`
- `fertilizer_diversification_index`: `float64`
- `rainfall_mm`: `float64`
- `temp_max_c`: `float64`
- `temp_min_c`: `float64`
- `solar_radiation_mj_m2`: `float64`
- `soil_ph`: `float64`

Missing values after merge:

- `season_period`: 0
- `ecosystem`: 0
- `province`: 0
- `island_group`: 0
- `yield_mt_ha`: 0
- `area_harvested_ha`: 0
- `n_application_rate`: 0
- `p_application_rate`: 0
- `k_application_rate`: 0
- `grade_ammophos_16_20_0_kg_ha`: 0
- `grade_ammosul_21_0_0_kg_ha`: 0
- `grade_complete_14_14_14_kg_ha`: 0
- `grade_mop_0_0_60_kg_ha`: 0
- `grade_urea_46_0_0_kg_ha`: 0
- `total_fertilizer_kg_ha`: 0
- `fertilizer_diversification_index`: 0
- `rainfall_mm`: 0
- `temp_max_c`: 0
- `temp_min_c`: 0
- `solar_radiation_mj_m2`: 0
- `soil_ph`: 0

Null policy: A present fertilizer record with a missing element rate or incomplete named grade rank is excluded, not filled with zero. A grade absent from the reported top-five list is encoded as zero, meaning unlisted rather than confirmed zero use. A province absent from a source is not imputed.

## Province coverage and exclusions

Counts by source: `{"area": 80, "climate": 82, "fertilizer_elements": 77, "fertilizer_grades": 77, "yield": 81}`. Full province-by-source flags and names absent from sources are in `province_reconciliation.csv` and `sourcing_audit.json`. Incomplete fertilizer rows excluded: `{"incomplete_element_records": 0, "incomplete_grade_records": 0, "required_nulls_after_merge": 0, "yield_without_area_match": 4}`.

## Yield/area coverage and pH checks

| season_period   | ecosystem     |   yield_source_rows |   area_matches |   yield_rows_without_area |
|:----------------|:--------------|--------------------:|---------------:|--------------------------:|
| 2021_Semester_2 | Irrigated     |                  79 |             78 |                         1 |
| 2021_Semester_2 | Non-irrigated |                  78 |             77 |                         1 |
| 2022_Semester_1 | Irrigated     |                  78 |             77 |                         1 |
| 2022_Semester_1 | Non-irrigated |                  65 |             64 |                         1 |

For 2022 Semester 1 Non-irrigated, the source contains 65 yield rows and 64 matching harvested-area rows. The unmatched yield record is Maguindanao. The lower row count is present in the source coverage; the merge did not discard a row with a matching area key. An absent source record is unreported data, not proof of zero rice area. The final soil-pH check found 0 province/ecosystem groups with differing values across season-years (expected: 0).

Rows remaining through successive source joins:

| season_period   | ecosystem     |   +climate |   +elements |   +grades |   yield+area |
|:----------------|:--------------|-----------:|------------:|----------:|-------------:|
| 2021_Semester_2 | Irrigated     |         76 |          76 |        76 |           78 |
| 2021_Semester_2 | Non-irrigated |         73 |          73 |        73 |           77 |
| 2022_Semester_1 | Irrigated     |         76 |          76 |        76 |           77 |
| 2022_Semester_1 | Non-irrigated |         62 |          62 |        62 |           64 |

Later reductions occur at the corresponding inner join when a source key is absent; the stage counts make those exclusions explicit rather than silently attributing them to the yield/area merge.

## Target correlations

- `area_harvested_ha`: 0.437
- `soil_ph`: 0.380
- `total_fertilizer_kg_ha`: 0.353
- `n_application_rate`: 0.335
- `grade_urea_46_0_0_kg_ha`: 0.316
- `grade_ammophos_16_20_0_kg_ha`: 0.302
- `grade_complete_14_14_14_kg_ha`: 0.248
- `temp_max_c`: 0.214
- `p_application_rate`: 0.214
- `fertilizer_diversification_index`: 0.164
- `k_application_rate`: 0.136
- `rainfall_mm`: -0.112
- `solar_radiation_mj_m2`: 0.102
- `grade_ammosul_21_0_0_kg_ha`: 0.095
- `temp_min_c`: 0.076
- `grade_mop_0_0_60_kg_ha`: 0.060

These are descriptive associations, not causal effects. Soil pH is simulated and climate summaries hide within-province variation.

## Outliers

The 1.5 x IQR rule flags 2 yield observations. See `yield_iqr_outliers.csv`; verify them against source workbooks before exclusion.

## Visualizations

- `figures/yield_distribution.png: inspects target spread and skew.`
- `figures/yield_by_ecosystem.png: compares irrigated/non-irrigated yield distributions.`
- `figures/correlation_matrix.png: summarizes pairwise numeric associations.`
- `figures/yield_vs_fertilizer.png: compares yield with listed grade totals.`
- `figures/season_ecosystem_yield.png: compares means by season and ecosystem.`

## Notes for Member 2

- Use `island_group` as the geographic model feature and retain `province` for leave-one-province-out grouping and auditability.
- Do not describe `soil_ph` as measured data.
- The fertilizer kg-to-kg/ha conversion is an assumption.
- Grade totals and entropy use only reported top-five quantities; absent grades are encoded as zero/unlisted.
- Only two season-years are included; split validation by province to avoid leakage.
