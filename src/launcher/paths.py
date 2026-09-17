from __future__ import annotations

from pathlib import Path

from .errors import LaunchError

# .../<repo>/src/launcher/paths.py -> <repo>
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

#: The shipped agent system: ``.claude/`` (roster, rules, skills), ``docs/``, ``prompts/``.
AGENT_SYSTEM_DIR: Path = REPO_ROOT / "sfitteragents"

#: One directory per session — the fork forest. Git-ignored.
SESSIONS_DIR: Path = REPO_ROOT / "sessions"


def resolve_path(p: str | Path | None, base: Path = REPO_ROOT) -> Path | None:
    if p is None or p == "":
        return None
    p = Path(p).expanduser()
    return p if p.is_absolute() else base / p


def ensure_image(path: Path, hint: str | None = None) -> None:
    """Validate a container image: a ``.sif`` file or a sandbox directory.

    On hosts without squashfuse, apptainer cannot mount a squashfs ``.sif`` and
    extracts the whole image into a temporary sandbox on every launch. A sandbox
    *directory* built once avoids that, so an image is legitimately either a
    single file or a directory tree.
    """
    if not (path.is_file() or path.is_dir()):
        raise LaunchError(f"Container image not found at {path}.", hint)
