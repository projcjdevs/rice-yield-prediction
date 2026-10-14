# Predicting Provincial Rice Yield in the Philippines

COM241 Introduction to Machine Learning. Charles John R. Cabatian, Nico Andrew O. Gallardo, Renz Jerik C. Viloria. Instructor: Dr. Armida P. Salazar.

Regression of province-level average rice yield (MT/ha) on fertilizer, climate and a simulated soil pH. 287 rows (province x season x ecosystem), 76 provinces, 2021 Semester 2 and 2022 Semester 1.

## Results (see the paper for details)

| Evaluation | RMSE | MAE | R2 |
|---|---|---|---|
| Validation, leave-one-province-out, 60 provinces (Ridge + 3x mixup) | 0.667 | 0.541 | 0.387 |
| Sealed test, 16 provinces, evaluated once | 0.702 | 0.475 | 0.282 |

Post hoc baselines (added after the test evaluation; they did not influence model selection):

| Predictor | Validation RMSE | Test RMSE |
|---|---|---|
| Overall mean | 0.859 | 0.845 |
| Mean per ecosystem | 0.725 | 0.722 |
| Mean per season x ecosystem x island group | 0.704 | 0.619 |
| Selected model | 0.667 | 0.702 |

The selected model and the 12-cell lookup are not statistically distinguishable (province-level paired bootstrap, all intervals include zero). Most predictable variation comes from irrigation status and island group. Soil pH is simulated and mostly encodes ecosystem. See `src/diagnostics/extra_checks.py`.

## Reproduce

```bash
pip install -r requirements.txt
# run notebooks 01 to 06 in order, or:
python src/diagnostics/extra_checks.py --out artifacts/extra_checks_results.json
streamlit run app/app.py
```

## Layout

- `data/processed/merged_rice_yield_dataset.csv`: the modeling dataset and `data_dictionary.md`
- `notebooks/01_eda.ipynb` to `06_evaluate.ipynb`: EDA, split, preprocessing, augmentation, training, evaluation
- `artifacts/`: metrics, out-of-fold and test predictions, split definition, bootstrap intervals
- `models/`: saved Ridge model and preprocessing pipeline used by the app
- `app/app.py`: Streamlit app (local)
- `src/`: shared code, `src/diagnostics/`: post hoc checks
- `docs/`: planning documents and EDA figures

## Known limitations

Soil pH is simulated, not measured. Fertilizer values are assumed to be kg/ha. Only two seasons (also two years). Hyperparameters were not tuned. Area harvested is known only after harvest. See the paper, Section IV.