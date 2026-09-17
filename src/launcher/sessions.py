"""Sessions — the unit the launcher works in.

A session is a self-contained directory under ``sessions/``::

    sessions/<stamp>__<label>/
      session.json   id, label, created, last_used, forked_from, claude_session_id
      .claude/       the agent system (roster, rules, skills) + its memory slates
      docs/          the documentation library, bound read-only at /sfitter_docs
      prompts/       the lead's system-prompt appends
      agent_wikis/   the wiki, bound at /agent_wikis
      output/        deliverables; the session's project root (/output)
      workspace/     scratch, bound at /workspace; kept across launches
      run/           lock + one workdir per launch (logs, $HOME)
      cluster_runs/  shared scratch for cluster jobs (unless CLUSTER_RUNS_BASE is set)

A new session copies ``.claude/``, ``docs/`` and ``prompts/`` from its source —
the shipped ``sfitteragents/`` (a cold start) or an earlier session (a fork,
which also carries the wiki over). The shipped tree is never written to, and
each session is an immutable fork source for later ones: a bad session is a
dead branch, you fork the last good one.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .paths import AGENT_SYSTEM_DIR, REPO_ROOT, SESSIONS_DIR, resolve_path

#: What a session copies from its source (the shipped system or another session).
SESSION_TREES = (".claude", "docs", "prompts")

#: ``forked_from`` of a session cold-started from the shipped agent system.
BASE_SOURCE = "sfitteragents"

#: Prefix of every apptainer instance the launcher starts.
INSTANCE_PREFIX = "sfitteragents"

#: Claude Code config dir used when CLAUDE_CONFIG_DIR is not set. Git-ignored.
DEFAULT_CLAUDE_CONFIG_DIR = REPO_ROOT / "claude_config"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(label: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", label.strip()).strip("-").lower()
    return slug or "session"


def claude_config_dir() -> Path:
    """The host Claude Code config dir bound into the container (login, settings, transcripts)."""
    return resolve_path(os.environ.get("CLAUDE_CONFIG_DIR")) or DEFAULT_CLAUDE_CONFIG_DIR


def cluster_runs_dir(sdir: Path) -> Path:
    """The session's cluster scratch: under CLUSTER_RUNS_BASE if set, else inside the session."""
    base = resolve_path(os.environ.get("CLUSTER_RUNS_BASE"))
    return base / sdir.name if base is not None else sdir / "cluster_runs"


def instance_prefix(session_id: str) -> str:
    """The apptainer instance-name prefix of one session.

    Stale instances are found by ``startswith(prefix)``, so a prefix must be
    unique AND never a prefix of another session's. A fixed-length content hash
    up front guarantees both; the slug tail only makes ``apptainer instance
    list`` readable.
    """
    h = hashlib.sha1(session_id.encode()).hexdigest()[:8]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", session_id).strip("-").lower()[:24].strip("-")
    return f"{INSTANCE_PREFIX}-{h}-{slug}" if slug else f"{INSTANCE_PREFIX}-{h}"


# --------------------------------------------------------------------------- #
# discovery + creation
# --------------------------------------------------------------------------- #
def discover_sessions() -> list[dict]:
    """Load every ``sessions/*/session.json`` (with a ``_dir`` Path). Unreadable ones are skipped."""
    out: list[dict] = []
    if not SESSIONS_DIR.is_dir():
        return out
    for meta_path in sorted(SESSIONS_DIR.glob("*/session.json")):
        try:
            meta = json.loads(meta_path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"  (skipping unreadable session {meta_path.parent.name}: {e})", file=sys.stderr)
            continue
        meta["_dir"] = meta_path.parent
        meta.setdefault("id", meta_path.parent.name)
        out.append(meta)
    return out


def create_session(
    *, source_dir: Path, source_wiki: Path | None, forked_from: str, label: str
) -> Path:
    """Seed a new session from *source_dir* (the shipped system or a session) and return it.

    Full copies, symlinks dereferenced, so the session never aliases its source.
    A source session that predates ``docs/``/``prompts/`` riding along gets the
    shipped ones.
    """
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sid = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__{_slugify(label)}"
    sdir = SESSIONS_DIR / sid
    n = 0
    while sdir.exists():
        n += 1
        sdir = SESSIONS_DIR / f"{sid}_{n}"
    sdir.mkdir(parents=True)

    for tree in SESSION_TREES:
        src = source_dir / tree
        if not src.is_dir():
            src = AGENT_SYSTEM_DIR / tree
        shutil.copytree(src, sdir / tree, symlinks=False, ignore_dangling_symlinks=True)
    if source_wiki is not None and source_wiki.is_dir():
        shutil.copytree(source_wiki, sdir / "agent_wikis", symlinks=False,
                        ignore_dangling_symlinks=True)
    else:
        (sdir / "agent_wikis").mkdir()

    now = utc_now_iso()
    meta = {
        "id": sdir.name,
        "label": label,
        "created": now,
        "forked_from": forked_from,
        "last_used": now,
        # Stable claude conversation id: the first launch starts it with
        # `--session-id <id>`, every Continue resumes it with `--resume <id>`.
        # Pinned here because all sessions share one Claude config dir and the
        # /output project key, so `--continue` (most recent) would be ambiguous.
        "claude_session_id": str(uuid.uuid4()),
    }
    (sdir / "session.json").write_text(json.dumps(meta, indent=2) + "\n")
    return sdir


def touch_last_used(sdir: Path) -> None:
    """Bump ``last_used`` in the session's metadata (best-effort)."""
    meta_path = sdir / "session.json"
    try:
        meta = json.loads(meta_path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    meta["last_used"] = utc_now_iso()
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")


# --------------------------------------------------------------------------- #
# conversation continuity
# --------------------------------------------------------------------------- #
def argv_pins_conversation(argv: list[str]) -> bool:
    """True when argv already fixes which claude conversation to use.

    ``--resume``/``-r`` and ``--continue``/``-c`` resume one (a ``--session-id``
    next to them makes claude reject the run), and a second ``--session-id`` is
    always an error. Both long and short forms must match.
    """
    for a in argv:
        if a in ("--resume", "-r", "--continue", "-c", "--session-id"):
            return True
        if a.startswith("--session-id="):
            return True
    return False


def pinned_claude_id(sdir: Path) -> str | None:
    """The conversation id pinned in ``session.json`` at creation."""
    try:
        meta = json.loads((sdir / "session.json").read_text())
    except (OSError, json.JSONDecodeError):
        return None
    cid = meta.get("claude_session_id")
    return cid if isinstance(cid, str) and cid else None


def _recorded_run_ids(sdir: Path) -> list[str]:
    """Conversation ids ``code.py`` recorded for past launches, newest first.

    The newest can be a dead one — an id is recorded even when the launch never
    persisted a turn — so callers must check for a transcript before resuming.
    """
    ids: list[str] = []
    for rec in sorted((sdir / "run" / "workdirs").glob("*/logs/session_uuid"), reverse=True):
        try:
            u = rec.read_text().strip()
        except OSError:
            continue
        if u and u not in ids:
            ids.append(u)
    return ids


def _transcript_exists(cid: str) -> bool:
    """Whether claude has a transcript for conversation *cid* (``projects/*/<cid>.jsonl``).

    Fail-open: an unreadable config dir must not silently downgrade a good
    resume to a fresh conversation.
    """
    try:
        return any((claude_config_dir() / "projects").glob(f"*/{cid}.jsonl"))
    except OSError:
        return True


def resumable_claude_id(sdir: Path) -> str | None:
    """The conversation id **Continue** should resume, or None to start fresh.

    Prefer the pinned id when it has a transcript. If it does not — an aborted
    first launch never persisted a turn, so a later launch started a fresh
    conversation under an id ``code.py`` minted — take the newest recorded id
    that does.
    """
    pinned = pinned_claude_id(sdir)
    if pinned is not None and _transcript_exists(pinned):
        return pinned
    for cid in _recorded_run_ids(sdir):
        if _transcript_exists(cid):
            return cid
    return None
