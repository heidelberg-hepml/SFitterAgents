"""Stop the apptainer instance(s) a session left behind.

``./cleanup_sfitteragents.sh`` lands here. A launch stops its own instance on
exit; this is for a wedged launch or a dead terminal. Sessions are independent
and several can be live at once, so with a terminal it shows what is running
and asks; without one it acts only when the choice is unambiguous.

It stops instances only. Session directories — and the memory in them — are
left alone; remove a session from the ``./sfitteragents.sh`` menu.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import apptainer, sessions
from .settings import load_config_env

USAGE = """\
Usage: cleanup_sfitteragents.sh [options]

With no options: show the running SFitterAgents sessions and ask which to stop.

Options:
      --instance_name NAME    Stop this apptainer instance, no questions asked
      --all                   Stop every running SFitterAgents session
  -h, --help                  Show this help and exit

Stops instances only — session directories (and the memory in them) are left alone.
"""


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--instance_name", default=None)
    p.add_argument("--all", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    args, _ = p.parse_known_args(argv)
    return args


def _running(apptainer_bin: Path) -> list[str]:
    return [
        name for name in apptainer.list_instances(apptainer_bin)
        if name.startswith(f"{sessions.INSTANCE_PREFIX}-")
    ]


def _owners() -> dict[str, dict]:
    """Map apptainer instance name → the session that started it.

    Every launch records its instance name under
    ``sessions/<id>/run/workdirs/<stamp>/logs/instance_name.txt``.
    """
    owners: dict[str, dict] = {}
    for session in sessions.discover_sessions():
        for mark in (session["_dir"] / "run" / "workdirs").glob("*/logs/instance_name.txt"):
            try:
                name = mark.read_text().splitlines()[0].strip()
            except (OSError, IndexError):
                continue
            if name:
                owners[name] = session
    return owners


def _describe(name: str, owners: dict[str, dict]) -> str:
    session = owners.get(name)
    if session is None:
        return f"{name}\n       (no session claims this — orphan?)"
    return f"{session.get('label', session['id'])}\n       {session['_dir']}\n       {name}"


def _choose(running: list[str], owners: dict[str, dict]) -> list[str]:
    """Ask which instances to stop. Returns the chosen instance names."""
    print("\nRunning SFitterAgents sessions:\n")
    for n, name in enumerate(running, 1):
        print(f"  {n}) {_describe(name, owners)}")
    print("\n  a) all of them")
    print("  q) quit, stop nothing\n")

    # One running session is unambiguous, so Enter means "that one"; with
    # several, Enter must not stop anything.
    default = "1" if len(running) == 1 else ""
    hint = f" [default {default}]" if default else " (e.g. 1,3)"
    while True:
        try:
            raw = input(f"Stop which?{hint}: ").strip().lower() or default
        except (EOFError, KeyboardInterrupt):
            print()
            return []
        if raw in ("q", "quit", ""):
            return []
        if raw in ("a", "all"):
            return list(running)
        picks = [tok for tok in raw.replace(",", " ").split() if tok]
        chosen = [
            running[int(tok) - 1] for tok in picks
            if tok.isdigit() and 1 <= int(tok) <= len(running)
        ]
        if chosen and len(chosen) == len(picks):
            return chosen
        print("  ? pick numbers from the list, or a / q.")


def _stop(apptainer_bin: Path, names: list[str]) -> None:
    for name in names:
        print(f"  stopping {name}")
        apptainer.stop_instance(apptainer_bin, name, force=True)
    print("Done.")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = _parse_args(argv)
    if args.help:
        print(USAGE)
        return 0

    load_config_env()
    apptainer_bin = apptainer.locate()

    if args.instance_name:
        if apptainer.instance_exists(apptainer_bin, args.instance_name):
            _stop(apptainer_bin, [args.instance_name])
        else:
            print(f"No running instance named {args.instance_name!r}.")
        return 0

    running = _running(apptainer_bin)
    if not running:
        print("No SFitterAgents session is running.")
        return 0

    if args.all:
        print(f"Stopping all {len(running)} SFitterAgents session(s):")
        _stop(apptainer_bin, running)
        return 0

    if sys.stdin.isatty():
        chosen = _choose(running, _owners())
        if not chosen:
            print("Nothing stopped.")
            return 0
        _stop(apptainer_bin, chosen)
        return 0

    # No terminal to ask at. One candidate is unambiguous; with several,
    # stopping a sibling would kill a live session unrelated to this call.
    if len(running) == 1:
        _stop(apptainer_bin, running)
        return 0
    owners = _owners()
    print(f"{len(running)} SFitterAgents sessions are running:")
    for name in running:
        print(f"  {_describe(name, owners)}")
    print("\nRefusing to guess which one to stop. Re-run with "
          "--instance_name NAME, or --all to stop them all.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
