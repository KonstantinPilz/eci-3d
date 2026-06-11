# ECI 3D Explorer

Interactive 3D version of [Epoch AI's Capabilities Index graph](https://epoch.ai/eci?view=graph&tab=training-compute):
**release date × training compute (FLOP, log) × capability score**, rendered with Plotly.js.

**Live site:** https://konstantinpilz.github.io/eci-3d/

- z-axis switchable between overall ECI and domain subsets (e.g. [Software engineering](https://konstantinpilz.github.io/eci-3d/?subset=Software+engineering)). Domain scores are the unweighted mean across that domain's benchmarks each model was evaluated on — a rough summary, not Epoch's official domain analysis.
- Color by organization or country; optional ECI 90% CI bars; only models with a known training-compute estimate are plotted.
- `?subset=<domain>` URL parameter preselects a domain.

## Data & auto-update

Data is Epoch AI's public CC-BY data (`benchmarked_models.csv`, `eci_benchmarks.csv`, `benchmarks.json` from
[epoch.ai/data](https://epoch.ai/data)). Epoch's endpoints don't send CORS headers, so
[`fetch_data.py`](fetch_data.py) (stdlib-only) mirrors and joins them into `docs/data.json`.

A daily cron job on Konstantin's Oracle VM (06:23 ET, `~/projects/eci-3d/update.sh`) re-runs the fetch and pushes
`docs/data.json` if it changed; GitHub Pages (serving `/docs` on `main`) redeploys automatically.

(A GitHub Actions workflow for the same job exists locally in `.github/workflows/` but is untracked: the VM's gh
OAuth token lacks the `workflow` scope to push it. To switch to Actions, run `gh auth refresh -s workflow`,
commit the workflow, and remove the VM cron entry.)

## Local development

```bash
python3 fetch_data.py
cd docs && python3 -m http.server 8013 --bind 127.0.0.1
```

Built by Konstantin's Claude, 2026-06-11.
