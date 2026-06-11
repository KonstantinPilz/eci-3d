#!/usr/bin/env python3
"""Fetch Epoch AI ECI data and build docs/data.json for the 3D explorer.

Sources (all public, CC-BY, published by Epoch AI):
  https://epoch.ai/data/benchmarked_models.csv  - model versions, release date,
                                                  training compute (FLOP), ECI + CI
  https://epoch.ai/data/eci_benchmarks.csv      - per-model per-benchmark scores
  https://epoch.ai/data/benchmarks.json         - benchmark metadata incl. domains

Stdlib only. Run: python3 fetch_data.py
"""
import csv
import io
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://epoch.ai/data/"
OUT = Path(__file__).parent / "docs" / "data.json"

# benchmark-name aliases where slug-normalization alone fails
# (csv name -> benchmarks.json id)
ALIASES = {"gsobench": "gso"}


def fetch(name: str) -> str:
    req = urllib.request.Request(BASE + name, headers={"User-Agent": "eci-3d-explorer/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main() -> None:
    models_csv = list(csv.DictReader(io.StringIO(fetch("benchmarked_models.csv"))))
    bench_csv = list(csv.DictReader(io.StringIO(fetch("eci_benchmarks.csv"))))
    bench_meta = json.loads(fetch("benchmarks.json"))

    # benchmark name (as used in eci_benchmarks.csv) -> list of domains
    jmap = {}
    for v in bench_meta.values():
        if isinstance(v, dict) and v.get("id"):
            jmap[norm(v["id"])] = v
            if v.get("title"):
                jmap.setdefault(norm(v["title"]), v)

    def domains_of(bench_name: str) -> list:
        key = norm(bench_name)
        key = ALIASES.get(key, key)
        meta = jmap.get(key)
        return (meta.get("domains") or []) if meta else []

    # per-model domain performance: model -> domain -> list of (benchmark, perf)
    dom_perf = {}
    for r in bench_csv:
        model, bench = r["Model"], r["benchmark"]
        try:
            perf = float(r["performance"])
        except (ValueError, TypeError):
            continue
        for d in domains_of(bench):
            dom_perf.setdefault(model, {}).setdefault(d, {})[bench] = perf

    out_models = []
    seen = set()
    for r in models_csv:
        name = r["Display name"] or r["Model"]
        if name in seen:
            continue
        if not (r["eci"] and r["Version release date"]):
            continue
        seen.add(name)
        try:
            compute = float(r["Training compute (FLOP)"]) if r["Training compute (FLOP)"] else None
        except ValueError:
            compute = None
        doms = {}
        for d, scores in dom_perf.get(r["Model"], {}).items():
            vals = list(scores.values())
            doms[d] = {"mean": sum(vals) / len(vals), "n": len(vals)}
        out_models.append(
            {
                "name": name,
                "org": r["Organization"] or "Unknown",
                "country": r["Country (of organization)"] or "Unknown",
                "date": r["Version release date"],
                "compute": compute,
                "eci": float(r["eci"]),
                "ci": [
                    float(r["eci_ci_low"]) if r["eci_ci_low"] else None,
                    float(r["eci_ci_high"]) if r["eci_ci_high"] else None,
                ],
                "domains": doms,
            }
        )

    all_domains = sorted({d for m in out_models for d in m["domains"]})
    payload = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "domains": all_domains,
        "models": out_models,
    }
    OUT.write_text(json.dumps(payload, separators=(",", ":")))

    n_compute = sum(1 for m in out_models if m["compute"])
    print(
        f"wrote {OUT}: {len(out_models)} models ({n_compute} with training compute), "
        f"{len(all_domains)} domains"
    )
    if n_compute < 50:
        print("WARNING: suspiciously few models with compute - check upstream schema", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
