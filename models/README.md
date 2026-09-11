# models/

**Owner:** Member 2 (produces) · **Consumed by:** Member 3

Serialized artifacts required by Contract 2 go here:

- `preprocessing_pipeline.joblib` — fitted on the training split only
- `model_linear_baseline.joblib`
- `model_ridge.joblib`
- `model_random_forest.joblib`
- `model_gradient_boosting.joblib`
- `feature_order.json` — exact ordered feature list expected at inference time
- `train_test_split_seed.txt` — random seed + split ratio used

These are committed to Git as-is (they should be small for a tabular dataset this size). If any single file approaches GitHub's ~50MB soft limit, uncomment the relevant line in the root `.gitignore` and store it via Git LFS or an external link instead.
