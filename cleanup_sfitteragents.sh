#!/usr/bin/env bash
# Stop SFitterAgents container instances left behind by a wedged launch or a dead
# terminal. Session directories are never touched. See --help.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec env PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
     python3 -m launcher cleanup "$@"
