# data/processed/

**Owner:** Member 1 · **Consumed by:** Member 2

This is where `merged_rice_yield_dataset.csv` — the Contract 1 deliverable — lives once the four raw sources have been merged and cleaned.

Must match the canonical schema in `docs/01_project_overview_and_architecture.md` §5, and satisfy the acceptance criteria in `docs/02_roadmap_and_contracts.md` (Contract 1): no missing values in `yield_kg_ha`, consistent categorical values, all documented in a companion `data_dictionary.md` in this folder.

This folder **is** committed to Git (unlike `data/raw/`) since it's the small, cleaned, reproducible dataset the rest of the pipeline depends on.
