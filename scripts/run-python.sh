#!/usr/bin/env bash
# Environment-aware Python script runner.
# Routes through uv (Claude Code) or python3 (Cowork) based on workspace/.env-config.
#
# Usage:
#   run-python.sh scripts/foo.py arg1 arg2
#   run-python.sh python -c "import sys; print(sys.version)"
#
# Exit code: propagated from the underlying Python process via exec.

set -uo pipefail

# Determine plugin root: prefer CLAUDE_PLUGIN_ROOT, fall back to script location.
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
  PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT"
else
  PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

# Read environment config if available; default to no-uv.
HAS_UV=false
ENV_CONFIG="$PLUGIN_ROOT/workspace/.env-config"
if [ -f "$ENV_CONFIG" ]; then
  # shellcheck source=/dev/null
  . "$ENV_CONFIG"
fi

if [ "$HAS_UV" = "true" ]; then
  exec uv run --quiet --directory "$PLUGIN_ROOT" "$@"
else
  # Strip leading "python" or "python3" arg (used in inline -c patterns)
  # so we can dispatch through the system python3 directly.
  if [ "${1:-}" = "python" ] || [ "${1:-}" = "python3" ]; then
    shift
  fi
  exec python3 "$@"
fi
