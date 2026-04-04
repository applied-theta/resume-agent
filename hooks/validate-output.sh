#!/usr/bin/env bash
# Validate JSON output files against their schemas.
# Called by PreToolUse hook on Write operations.
# Exits 0 on success or if no matching schema exists (pass-through).

set -euo pipefail

FILE_PATH="${1:-}"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PLUGIN_ROOT"
"$PLUGIN_ROOT/scripts/run-python.sh" scripts/validate-output.py "$FILE_PATH"
