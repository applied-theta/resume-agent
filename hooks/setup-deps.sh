#!/usr/bin/env bash
# SessionStart hook: ensure Python dependencies are installed.
# Non-blocking — warns but does not fail if uv is missing.

set -uo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v uv &>/dev/null; then
  echo "WARNING: 'uv' is not installed. Python scripts (PDF extraction, scoring, PDF export) may not work." >&2
  echo "Install uv: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 0
fi

cd "$PLUGIN_ROOT"
uv sync --quiet 2>/dev/null || {
  echo "WARNING: Failed to sync dependencies in $PLUGIN_ROOT. Some features may not work." >&2
  exit 0
}
