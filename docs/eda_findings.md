# Exploratory Data Analysis Findings

## Dataset snapshot

The final merged dataset in [data/processed/merged_rice_yield_dataset.csv](../data/processed/merged_rice_yield_dataset.csv) contains 287 rows and 20 columns. There are no missing values in the target field, yield_mt_ha, and the overall dataset is complete for the merged features used in the model.

## Null handling decisions

Two different null scenarios were resolved explicitly:

1. Source-coverage gaps: provinces missing entirely from a source were not filled. They simply dropped out on the merge step. The clearest known example is Basilan, which is present in the yield/area tables but absent from the fertilizer files.
2. In-file missing values: when a province was present but an application-rate or grade value was null, the value was treated as 0 when it represented “no recorded usage.” This preserves the semantics of zero fertilizer contribution instead of inventing a missing observation.

## Core findings

- Yield distribution is moderately spread across the two season-periods and both ecosystem categories, with most observations clustering around typical irrigated and non-irrigated provincial yields.
- The irrigated subset shows higher and more stable yield values than the non-irrigated subset, which aligns with the known agronomic distinction in the source data.
- Fertilizer application rates and the total fertilizer quantity are both strongly associated with yield in the expected direction, but the relationship is not strictly linear, which makes the problem suitable for nonlinear models.
- Climate variables show the expected provincial variation across Luzon, Visayas, and Mindanao, and island_group acts as a useful summary geography for modeling.
- soil_ph remains in a relatively narrow band (roughly 5.0–6.5), with irrigated ecotypes slightly less acidic than non-irrigated ones, consistent with the synthetic generation rule used during merge.

## Planned and reviewed visualizations

At least five types of plots are relevant to the analysis and should be kept in the EDA package:

1. Distribution of yield_mt_ha by ecosystem
2. Yield versus total_fertilizer_kg_ha scatterplot
3. Yield versus rainfall_mm scatterplot / trend line
4. Soil pH boxplot by ecosystem and island_group
5. Correlation heatmap of climate, fertilizer, and yield variables
6. Fertilizer diversification index distribution and relationship with yield
7. Seasonal comparison of yield across 2021_Semester_2 and 2022_Semester_1

## Modeling implications

- Use island_group instead of raw province to avoid train/test leakage caused by one-hot province columns under leave-one-province-out evaluation.
- Keep the synthetic soil_ph feature as a documented modeled variable, not measured field data.
- Do not impute source-coverage gaps with placeholders; they are genuine structural missingness in the dataset.
- Treat fertilizer missingness as zero only when the null is functionally “no usage recorded,” not when the province is absent from the source entirely.

## Final status

The merged dataset is complete for Contract 1 and is ready for downstream model preprocessing. The final row count is 287, with no missing target values and no unresolved nulls in the final merged feature set.
