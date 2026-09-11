# Task Delegation

Three members, three pipeline components, mapped directly to the contracts in `02_roadmap_and_contracts.md`.

---

## Member 1 — Data Acquisition, Merging & EDA

**Owns:** Contract 1 (output)

**Tasks:**
- Source and document PalayStat (SERBIS + PSA rice economy tables), Ricelytics (FPA fertilizer/pesticide pricing), NASA POWER (climate), and ISRIC SoilGrids (soil pH) — for each, record source, license/permission, collection method, unit of analysis, and known limitations.
- Resolve province-naming/grouping mismatches across years (e.g., PSGC updates like the Negros Island Region split) before merging.
- Merge all sources into `merged_rice_yield_dataset.csv` on `province + year(+ season)`, matching the canonical schema exactly.
- Handle missing values, duplicates, and inconsistent entries; document every action taken.
- Produce ≥5 meaningful visualizations: target distribution, feature distributions, correlation heatmap against `yield_kg_ha`, outlier investigation, and at least one more that supports a real modeling decision.
- Write `eda_findings.md`: a concise summary tying every visualization to a decision (e.g., a feature to drop, a transform to apply, an outlier to keep vs. remove).

**Deliverables:** `merged_rice_yield_dataset.csv`, `data_dictionary.md`, `eda_findings.md`.

---

## Member 2 — Feature Engineering, Preprocessing & Model Training

**Owns:** Contract 2 (output) · **Consumes:** Contract 1

**Tasks:**
- Build engineered features: combined fertilizer figure (quantity or cost-based), season-aligned climate aggregates, categorical encodings for `province`/`region`/`season`.
- Split data into train/test; fit all scaling/encoding on the training split only.
- Train all four models under identical conditions: Linear Regression (baseline), Ridge Regression, Random Forest Regressor, Gradient Boosting Regressor — same split, same preprocessing, same cross-validation strategy.
- Tune the main hyperparameters for each of the three required models; document what was tried and why the final settings were chosen.
- Record cross-validated RMSE/MAE/R² per model in `model_metrics.csv`.
- Serialize the fitted preprocessing pipeline and all four trained models; record the exact feature order and random seed used.

**Deliverables:** `preprocessing_pipeline.joblib`, four `model_*.joblib` files, `model_metrics.csv`, `feature_order.json`, `train_test_split_seed.txt`.

---

## Member 3 — Evaluation, Selection & Deployment

**Owns:** Contract 3 (output) · **Consumes:** Contract 2

**Tasks:**
- Compare the three required models' validation metrics; confirm the strongest one exactly once on the held-out test set (no repeated test-set peeking).
- Write `final_model_justification.md`, weighing performance, interpretability, and speed — referencing the Linear Regression baseline as context, not as a fourth competing candidate for selection.
- Build `app.py` (Streamlit): a simple form for the canonical feature inputs, loading the final model + preprocessing pipeline, returning a predicted yield.
- Test the app with valid inputs, invalid inputs (wrong types, out-of-range values), and boundary inputs (e.g., zero fertilizer, extreme rainfall); log results in `deployment_test_log.md`.
- Confirm the whole pipeline runs cleanly on a fresh environment using a `requirements.txt`.

**Deliverables:** `final_model_justification.md`, `app.py`, `requirements.txt`, `deployment_test_log.md`.

---

## Shared Responsibilities (all three members)

- **Phase 0:** Defining the problem statement, target variable, intended users, and success criteria together, before splitting off.
- **Final report assembly:** merging each member's documentation into the single submitted report.
- **Presentation/demo rehearsal:** everyone should be able to explain every stage of the pipeline, not just their own, in case questions land outside their assigned part.
