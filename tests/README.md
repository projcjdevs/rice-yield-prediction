# tests/

**Owner:** Member 3 (primarily), open to all

Optional but recommended: lightweight tests for the merge/feature/model functions in `src/`, and the boundary/invalid-input checks for the Streamlit app referenced in Contract 3.

Suggested minimum: one test confirming `merge.validate_canonical_schema()` raises on a bad DataFrame, and one confirming `evaluate.compute_metrics()` returns the expected keys.
