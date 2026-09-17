#!/usr/bin/env bash
# SFitterAgents — run the SFitter agent in a session.
#
#   ./sfitteragents.sh            menu: run a new session (fork it from the shipped
#                                 agent system or an earlier session), continue a
#                                 session, or remove one
#   ./sfitteragents.sh --help     usage
#
# Every argument is forwarded to `claude`, e.g. --model. The shipped agent system
# pre-approves no tools, so a plain session asks before each tool use; skipping
# those checks is your decision, per launch:
#
#   ./sfitteragents.sh --dangerously-skip-permissions
#
# Sessions live under sessions/ (git-ignored), each with its own output/, memory,
# wiki and container instance, so several can run concurrently.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec env PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
     python3 -m launcher interactive "$@"
