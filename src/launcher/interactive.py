"""Session launcher — ``./sfitteragents.sh`` lands here.

Asks what to do — run the agent in a new session, continue a session, or remove
one — and, for a new session, what to fork it from: the shipped agent system (a
clean cold start) or an earlier session, whose learned memory and wiki carry
over. It then hands off to ``launcher.code``, which starts the container for
that session. Plain prompts, run before any container starts.

Each session is isolated — its own output/, memory, wiki, run lock, overlay and
apptainer instance — so several sessions can run concurrently from one clone.
Arguments are forwarded verbatim to ``claude`` (``--model``,
``--dangerously-skip-permissions``, ...).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from . import apptainer, sessions
from .errors import LaunchError
from .lock import is_locked
from .paths import AGENT_SYSTEM_DIR
from .settings import load_config_env

USAGE = """\
Usage: ./sfitteragents.sh [claude arguments...]

Interactive: asks whether to run the agent in a new session (forked from the
shipped agent system or from an earlier session), continue a session, or remove
one, then starts it in the container. Sessions live under sessions/.

Every argument is forwarded to `claude`, e.g.
  ./sfitteragents.sh --model opus
  ./sfitteragents.sh --dangerously-skip-permissions
"""


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(130)


def ask_number(prompt: str, options: list[str]) -> int:
    """Print an enumerated menu and return the chosen 0-based index. Re-asks on bad input."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        raw = _ask("> ")
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print(f"  Please enter a number between 1 and {len(options)}.")


def ask_text(prompt: str, default: str) -> str:
    return _ask(f"{prompt} [{default}]: ") or default


# --------------------------------------------------------------------------- #
# fork sources
# --------------------------------------------------------------------------- #
def _last_used(s: dict) -> str:
    return s.get("last_used") or s.get("created") or ""


def order_fork_sources(all_sessions: list[dict]) -> list[dict]:
    """Ordered, de-duplicated fork options: the most recent session, the shipped
    system, the session the newest one was forked from, then all remaining
    sessions newest first. Each option is ``{"kind": "base"}`` or
    ``{"kind": "session", "session": s}``."""
    options: list[dict] = []
    seen: set[str] = set()

    def add_session(s: dict | None) -> None:
        if s and s["id"] not in seen:
            seen.add(s["id"])
            options.append({"kind": "session", "session": s})

    by_last_used = sorted(all_sessions, key=_last_used, reverse=True)
    by_created = sorted(all_sessions, key=lambda s: s.get("created") or "", reverse=True)
    if by_last_used:
        add_session(by_last_used[0])
    options.append({"kind": "base"})
    if by_created:
        parent_id = by_created[0].get("forked_from", "")
        add_session(next((s for s in all_sessions if s["id"] == parent_id), None))
    for s in by_created:
        add_session(s)
    return options


def _fork_option_label(opt: dict) -> str:
    if opt["kind"] == "base":
        return "The shipped agent system  — clean cold start"
    s = opt["session"]
    return (f"{s.get('label', s['id'])}   ({s['id']}; from {s.get('forked_from', '?')}; "
            f"created {s.get('created', '?')})")


def pick_session(all_sessions: list[dict], action: str) -> dict:
    """Newest-first session picker."""
    ordered = sorted(all_sessions, key=_last_used, reverse=True)
    labels = [
        f"{s.get('label', s['id'])}   ({s['id']}; from {s.get('forked_from', '?')})"
        for s in ordered
    ]
    return ordered[ask_number(f"Which session to {action}?", labels)]


# --------------------------------------------------------------------------- #
# actions
# --------------------------------------------------------------------------- #
def launch(sdir, argv: list[str], *, resume: bool = False) -> int:
    """Start (or, with *resume*, continue) the session in *sdir* via ``launcher.code``.

    A new session starts its pinned conversation with ``--session-id``;
    Continue reattaches to it with ``--resume`` — not ``--continue``, which
    picks the most recent conversation of any session. A conversation flag
    already in *argv* wins.
    """
    os.environ["SFA_SESSION_DIR"] = str(sdir)
    sessions.touch_last_used(sdir)

    conv_args: list[str] = []
    conv_note = "new conversation"
    if sessions.argv_pins_conversation(argv):
        conv_note = "conversation set by the passed-through claude flags"
    elif resume:
        cid = sessions.resumable_claude_id(sdir)
        if cid:
            conv_args = ["--resume", cid]
            conv_note = f"resuming conversation {cid}"
        else:
            conv_note = "no earlier conversation to resume — starting a fresh one"
    else:
        cid = sessions.pinned_claude_id(sdir)
        if cid:
            conv_args = ["--session-id", cid]
            conv_note = f"new conversation {cid}"

    print(f"\nSession:   {sdir.name}")
    print(f"  output:      {sdir / 'output'}")
    print(f"  cluster:     {sessions.cluster_runs_dir(sdir)}")
    print(f"  instance:    {sessions.instance_prefix(sdir.name)}-<stamp>")
    print(f"  claude:      {conv_note}")

    from .code import main as code_main

    return code_main([*conv_args, *argv])


def remove_session(session: dict) -> int:
    """Delete a session after a typed confirmation, stopping its instance first.

    Irreversible (sessions/ is git-ignored), so it refuses to delete while a
    launch holds the session's lock (on any host) or an instance of it is up.
    """
    sdir = session["_dir"]
    if not sdir.is_dir():
        print(f"Session dir {sdir} is gone already — nothing to remove.")
        return 0
    if is_locked(sdir / "run" / ".lock"):
        print(f"Session {session['id']} is running (its lock is held) — stop it first, "
              "then remove it.", file=sys.stderr)
        return 1
    prefix = sessions.instance_prefix(session["id"])

    try:
        apptainer_bin = apptainer.locate()
    except LaunchError as e:
        apptainer_bin = None
        print(f"  (apptainer not found — cannot check for a running instance: {e.message})",
              file=sys.stderr)

    def _live() -> list[str]:
        if apptainer_bin is None:
            return []
        return [n for n in apptainer.list_instances(apptainer_bin) if n.startswith(prefix)]

    live = _live()
    print(f"\nRemove session:  {session['id']}")
    print(f"  label: {session.get('label', '?')}   dir: {sdir}")
    if live:
        print(f"  RUNNING — will force-stop: {', '.join(live)}")
    elif apptainer_bin is None:
        print("  could not verify it is stopped — make sure no launch of it is running.")
    if _ask("Irreversible. Type 'yes' to remove: ") != "yes":
        print("Aborted — nothing removed.")
        return 1

    if live:
        apptainer.stop_instances(apptainer_bin, prefix)
        if _live():
            print("  instance still up after stop — aborting (won't delete a live session).",
                  file=sys.stderr)
            return 1

    # chmod first: overlayfs work/ dirs can be mode 000, which rmtree cannot descend.
    subprocess.run(["chmod", "-R", "u+rwX", str(sdir)], check=False)
    shutil.rmtree(sdir)
    print(f"Removed session {session['id']}.")
    external_scratch = sessions.cluster_runs_dir(sdir)
    if external_scratch.is_dir():
        print(f"  Its cluster scratch outside the session was left in place: {external_scratch}")
    return 0


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return 0
    if not sys.stdin.isatty():
        print("./sfitteragents.sh is interactive and needs a terminal.", file=sys.stderr)
        return 2

    load_config_env()
    if not (AGENT_SYSTEM_DIR / ".claude").is_dir():
        print(f"Agent system not found at {AGENT_SYSTEM_DIR}.", file=sys.stderr)
        return 2

    all_sessions = sessions.discover_sessions()
    modes = ["Run the agent (new session)"]
    if all_sessions:
        modes += ["Continue a session", "Remove a session"]
    print("SFitterAgents — session launcher")
    mode = modes[ask_number("What do you want to do?", modes)]

    if mode == "Remove a session":
        return remove_session(pick_session(all_sessions, "remove"))

    if mode == "Continue a session":
        session = pick_session(all_sessions, "continue")
        return launch(session["_dir"], argv, resume=True)

    options = order_fork_sources(all_sessions)
    if len(options) == 1:
        source = options[0]
        print("\nFirst run — starting fresh from the shipped agent system.")
    else:
        source = options[ask_number("Fork from where?", [_fork_option_label(o) for o in options])]

    if source["kind"] == "base":
        source_dir, source_wiki = AGENT_SYSTEM_DIR, None
        forked_from, default_label = sessions.BASE_SOURCE, "session"
    else:
        s = source["session"]
        source_dir, source_wiki = s["_dir"], s["_dir"] / "agent_wikis"
        forked_from, default_label = s["id"], s.get("label", "session")

    label = ask_text("Name this session (short label)", default_label)
    sdir = sessions.create_session(
        source_dir=source_dir, source_wiki=source_wiki, forked_from=forked_from, label=label,
    )
    print(f"\nCreated session {sdir.name} (forked from {forked_from}).")
    return launch(sdir, argv)
