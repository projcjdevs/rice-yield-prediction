# Rice Yield Prediction — Intro to ML Final Project

Supervised regression project predicting province-level Philippine rice (palay) yield from combined fertilizer input, climate conditions, and soil pH. Built by a 3-person team, each owning one stage of the pipeline.

Full context (problem statement, architecture, data sources, canonical schema, model roster, roadmap, and pipeline contracts) lives in **`docs/`** — read those before touching code. `docs/04_unified_llm_prompt.md` is the block each member pastes into their own LLM session so all three stay aligned.

---

## Repository Structure

```
rice-yield-prediction/
├── README.md
├── requirements.txt
├── .gitignore
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── 01_project_overview_and_architecture.md
│   ├── 02_roadmap_and_contracts.md
│   ├── 03_task_delegation.md
│   └── 04_unified_llm_prompt.md
├── data/
│   ├── raw/                  # gitignored — raw pulls from each source (Member 1)
│   │   └── README.md
│   └── processed/            # Contract 1 deliverable (Member 1 → Member 2)
│       ├── README.md
│       ├── data_dictionary.md
│       └── merged_rice_yield_dataset.csv   (generated, not yet in repo)
├── notebooks/
│   ├── 01_data_acquisition_and_eda.ipynb        (Member 1)
│   ├── 02_feature_engineering_and_modeling.ipynb (Member 2)
│   └── 03_evaluation_and_deployment.ipynb        (Member 3)
├── src/
│   ├── data/
│   │   ├── acquire.py        # pulls PalayStat / Ricelytics / NASA POWER / SoilGrids
│   │   └── merge.py          # merges into the canonical schema
│   ├── features/
│   │   └── build_features.py # feature engineering + preprocessing pipeline
│   └── models/
│       ├── train.py          # trains all 4 models (baseline + 3 required)
│       └── evaluate.py       # metrics + one-time test-set confirmation
├── models/                   # Contract 2 deliverable (Member 2 → Member 3)
│   └── README.md
├── reports/
│   ├── README.md
│   ├── figures/
│   ├── eda_findings.md               (Member 1, generated)
│   ├── model_metrics.csv             (Member 2, generated)
│   └── final_model_justification.md  (Member 3, generated)
├── app/
│   └── app.py                # Streamlit deployment (Member 3)
└── tests/
    └── README.md
```

Files marked "(generated)" don't exist yet in this skeleton — they're produced as each member completes their stage and are committed once ready, per the contracts in `docs/02_roadmap_and_contracts.md`.

---

## Setup

```bash
git clone <your-repo-url>
cd rice-yield-prediction

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Running things

**Notebooks** (open in order, one per pipeline stage):
```bash
jupyter notebook notebooks/
```

**The deployed app** (once Member 2's model artifacts exist in `models/`):
```bash
streamlit run app/app.py
```

---

## Git Workflow

- **Branch per member/stage**, not per tiny change: `member1/data-eda`, `member2/feature-modeling`, `member3/eval-deploy`. Cut smaller feature branches off these if useful.
- **Never commit directly to `main`.** Open a PR (template auto-fills a contract checklist) and have at least one other member glance at it before merging — cheap insurance against silently breaking another member's contract.
- **If a PR changes a contract's shape** (renames a column, changes a filename, changes what a stage outputs), update `docs/02_roadmap_and_contracts.md` and `docs/04_unified_llm_prompt.md` in the *same* PR — don't let the docs drift from what the code actually does.
- **Keep `data/raw/` out of Git** (already handled by `.gitignore`) — it's either large or trivially re-fetchable from the source APIs/portals; only the cleaned `data/processed/` output is committed.
- **Commit messages:** short, imperative, and scoped — e.g. `feat(data): merge PalayStat and NASA POWER on province+year`, not `updates`.

## Team

| Member | Pipeline Stage | Contract Owned |
|---|---|---|
| Member 1 | Data Acquisition, Merging & EDA | Contract 1 |
| Member 2 | Feature Engineering & Model Training | Contract 2 |
| Member 3 | Evaluation, Selection & Deployment | Contract 3 |

See `docs/03_task_delegation.md` for the full task breakdown per member.
