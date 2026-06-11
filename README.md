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

A GitHub Actions workflow ([update-data.yml](.github/workflows/update-data.yml)) re-runs the fetch daily at
06:23 UTC and commits `data.json` if it changed; GitHub Pages (serving `/docs` on `main`) redeploys automatically.

## Local development

```bash
python3 fetch_data.py
cd docs && python3 -m http.server 8013 --bind 127.0.0.1
```

Built by Konstantin's Claude, 2026-06-11.
