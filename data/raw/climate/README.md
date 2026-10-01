# Climate Sources

## Supplied workbook

`climate_datasets.csv.xlsx` is preserved as received. Its daily summary block has been extracted to `climate_manila_2022_semester1_daily.csv` with 181 daily observations from 2022-01-01 through 2022-06-30. The workbook metadata gives one coordinate, 14.586995 N, 121.002785 E, at elevation 9 m (Manila area). Variables are daily maximum/minimum temperature, precipitation sum, and shortwave-radiation sum.

This is one point location and one season only. It is not a province-level dataset and contains no 2021 Semester 2 observations, so it must not be replicated across provinces or used as a substitute for those missing spatial/temporal observations.

## Merge input

`climate_all_provinces.csv` is the province-level table expected by `build_dataset.py`, containing province-season aggregates for both target periods and an island group for each province. Keep it as the merge source only when its coverage and provenance are confirmed. The supplied Manila-area workbook is retained as a separate source and is not used to create provincial records.
