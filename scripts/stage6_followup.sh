#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/build/matplotlib"
python_bin="${ANNNI_PYTHON:-.venv/bin/python}"

if (( $# > 1 )); then
  echo 'Usage: bash scripts/stage6_followup.sh [--verify|--redraw|--help]' >&2
  exit 2
fi

case "${1:---verify}" in
  --verify)
    "$python_bin" scripts/release.py verify-data --out build/stage6_followup/verification
    ;;
  --redraw)
    "$python_bin" research_scripts/plot_stage6_followup.py --out build/stage6_followup/figures
    ;;
  --help|-h)
    echo 'Usage: bash scripts/stage6_followup.sh [--verify|--redraw|--help]'
    echo 'Set ANNNI_PYTHON to the installed scientific or portable Python interpreter.'
    echo 'Verification and figure outputs are written to build/stage6_followup/.'
    ;;
  *)
    echo 'Usage: bash scripts/stage6_followup.sh [--verify|--redraw|--help]' >&2
    exit 2
    ;;
esac
