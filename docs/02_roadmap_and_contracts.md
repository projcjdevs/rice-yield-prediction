# Roadmap & Pipeline Contracts

---

## Part A — Roadmap

Phases are relative (Phase 1, 2, 3...) rather than tied to fixed calendar dates — map these onto your actual submission deadline as a team.

| Phase | Focus | Rubric workflow step(s) | Lead |
|---|---|---|---|
| **Phase 0** | Define problem, target, users, success criteria (together) | Step 1 | All 3 |
| **Phase 1** | Source, document, and merge PalayStat + Ricelytics + NASA POWER + SoilGrids into one panel dataset; run full EDA | Steps 2–3 | Member 1 |
| **Phase 2** | Feature engineering, preprocessing pipeline, train all 4 models (baseline + 3 required) under identical split/CV/metric conditions | Steps 4–5 | Member 2 |
| **Phase 3** | Compare validation results, confirm best of the 3 required models on the held-out test set, write justification, build and stress-test the Streamlit deployment | Steps 6–7 | Member 3 |
| **Phase 4** | Integration, full pipeline rehearsal, final report assembly, presentation prep | — | All 3 |

Each phase should end with the relevant contract below being satisfied and handed off — don't start the next phase's work against an unfinished contract; that's how silent mismatches creep in.

---

## Part B — Pipeline Contracts

A contract defines exactly what one stage must hand off to the next: file(s), schema, format, and the acceptance criteria that make it "done." Treat these as fixed unless the whole team agrees to change them — since two other people's work depends on the shape staying stable.

### Contract 1 — Data/EDA → Feature Engineering (Member 1 → Member 2)

**Deliverable file:** `merged_rice_yield_dataset.csv`

**Required columns:** exactly the canonical schema in `01_project_overview_and_architecture.md` §5 — same names, same order preferred.

**Format rules:**
- One row = one province-year(-season) observation.
- No missing values in `yield_kg_ha` (the target) — rows without a target are dropped, not imputed.
- Missing values in feature columns are either imputed with a documented method or flagged in a companion `data_dictionary.md`, not silently dropped.
- Categorical columns (`province`, `region`, `season`) use consistent, final string values — no mixed casing, no province renaming mid-file (resolve PSGC/Negros Island Region grouping issues before handoff).

**Also required:** a short `eda_findings.md` summarizing the ≥5 visualizations, correlation findings, and outlier decisions — Member 2 needs this to know which features are safe to trust as-is.

**Acceptance criteria (handoff is "done" when):** the CSV loads cleanly with no target nulls, all canonical columns present with correct types, and `eda_findings.md` explicitly states which columns (if any) are unreliable or excluded going forward.

---

### Contract 2 — Feature Engineering/Modeling → Evaluation/Deployment (Member 2 → Member 3)

**Deliverable files:**
- `preprocessing_pipeline.joblib` — the fitted scaler/encoder object(s), fit on the training split only.
- `model_linear_baseline.joblib`, `model_ridge.joblib`, `model_random_forest.joblib`, `model_gradient_boosting.joblib` — all four trained models.
- `train_test_split_seed.txt` — the exact random seed and split ratio used, so results are reproducible.
- `model_metrics.csv` — one row per model, columns: `model_name, cv_rmse, cv_mae, cv_r2` (validation-time metrics only — no test-set numbers yet; those belong to Member 3's confirmation step).
- `feature_order.json` — the exact ordered list of feature names/columns the models expect at inference time.

**Format rules:** All four models must have been trained on the *same* train split, the *same* preprocessing logic, and evaluated with the *same* cross-validation strategy — this is a rubric requirement, not just good practice, since the comparison has to be fair.

**Acceptance criteria:** Member 3 can load `preprocessing_pipeline.joblib` + any model file + `feature_order.json`, run a prediction on a raw sample row, and get a sane numeric yield output — without needing to ask Member 2 anything.

---

### Contract 3 — Evaluation/Deployment → Final Delivery (Member 3 → whole team)

**Deliverable files:**
- `final_model_justification.md` — which of the three required models was selected, backed by validation metrics, one-time test-set confirmation, interpretability, and speed tradeoffs; explicitly states the Linear Regression baseline comparison as context, not as a competing "fourth required" model.
- `app.py` — the Streamlit app, loading only the final selected model + `preprocessing_pipeline.joblib`.
- `deployment_test_log.md` — documented results of testing the app with valid, invalid, and boundary inputs (per rubric requirement).

**Acceptance criteria:** any team member can run `streamlit run app.py` on a clean machine (with `requirements.txt` installed) and get a working prediction demo without additional setup steps that aren't documented.

---

## Quick Reference: Who Owns What Contract

| Contract | Produced by | Consumed by |
|---|---|---|
| Contract 1 | Member 1 | Member 2 |
| Contract 2 | Member 2 | Member 3 |
| Contract 3 | Member 3 | Whole team (final submission) |
