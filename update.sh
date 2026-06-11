#!/bin/bash
# Daily refresh of Epoch ECI data for the 3D explorer (run from cron).
set -euo pipefail
cd "$(dirname "$0")"
LOG=/home/ubuntu/.local/state/eci-3d-update.log
{
  echo "=== $(date -u +'%F %T UTC')"
  git pull --rebase --quiet
  timeout 300 python3 fetch_data.py
  if ! git diff --quiet docs/data.json; then
    git add docs/data.json
    git commit -q -m "Update ECI data ($(date -u +%F))"
    git push -q
    echo "pushed update"
  else
    echo "no changes"
  fi
} >>"$LOG" 2>&1
