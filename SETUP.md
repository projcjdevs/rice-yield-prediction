# Setup Guide — New Member Onboarding

Follow these steps in order. Should take about 10 minutes if nothing goes wrong.

---

## 1. Clone the repo

```bash
git clone <your-repo-url>
cd <repo-name>
```

## 2. Check your Python version

This project is pinned to **Python 3.10 or 3.11** — newer versions can have delayed compatibility with some ML libraries, and version mismatches between teammates cause confusing bugs.

```bash
python --version
```

If it's not 3.10/3.11, install one via [pyenv](https://github.com/pyenv/pyenv) (Mac/Linux) or the official installer (Windows) before continuing.

## 3. Create and activate a virtual environment

```bash
# macOS / Linux
python3.11 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

You'll know it worked if your terminal prompt now shows `(.venv)` at the start.

## 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Verify your environment

Run this — it should print `environment OK` with no errors:

```bash
python -c "import pandas, numpy, sklearn, matplotlib, seaborn, streamlit, joblib, requests; print('environment OK')"
```

If something's missing, re-run `pip install -r requirements.txt` and check you're inside the activated `.venv`.

## 6. A note on API access

Two of our data sources are queried live and **neither requires an API key** — no `.env` or secrets setup needed:

- **NASA POWER** (climate data) — quick test:
  ```bash
  curl "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN&community=AG&longitude=121.31&latitude=13.32&start=20230101&end=20230107&format=JSON"
  ```
- **SoilGrids** (soil pH) — heads up: ISRIC's live REST API has been intermittently paused. If `fetch_soilgrids_ph()` isn't returning data, check ISRIC's status before assuming it's a bug on our end — there's a fallback plan (static raster download + local sampling) documented in `docs/01_project_overview_and_architecture.md`.

## 7. Editor setup (optional but recommended)

If using VS Code: install the **Python** and **Jupyter** extensions, then `Cmd/Ctrl+Shift+P → Python: Select Interpreter` and choose the one inside `.venv`. This makes sure autocomplete and notebook execution use the right environment.

## 8. Final smoke test

```bash
streamlit hello
```

This opens a demo app in your browser. If it loads, your environment can run the deployment half of the project too — you're fully set up.

---

## If something's wrong

- Wrong Python version picked up? Check `which python` (Mac/Linux) or `where python` (Windows) to confirm it's pointing inside `.venv`, not a system install.
- `pip install` failing on one package? Note the exact error and check with the team before pinning a different version — everyone needs matching versions for reproducible results.
- Still stuck: ask in the team chat before spending more than ~15 minutes solo on an environment issue — it's almost always faster to compare against a teammate's working setup.