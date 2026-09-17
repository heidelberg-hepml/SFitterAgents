from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Iterable

from .errors import LaunchError
from .paths import resolve_path

Bind = tuple[str, str, str | None]  # (host, container, options)


def ensure_env_dirs() -> None:
    """Create the apptainer scratch dirs named by env, if set but missing.

    ``APPTAINER_TMPDIR`` / ``APPTAINER_CACHEDIR`` / ``APPTAINER_CONFIGDIR`` are
    commonly pointed at a per-user path under a node's local ``/tmp``. On a
    freshly booted node that path may not exist yet, and apptainer then fails
    early. Creating them is a no-op where they already exist.
    """
    for var in ("APPTAINER_TMPDIR", "APPTAINER_CACHEDIR", "APPTAINER_CONFIGDIR"):
        val = os.environ.get(var)
        if val:
            try:
                Path(val).mkdir(parents=True, exist_ok=True)
            except OSError:
                # Leave it to apptainer to surface a precise error if this fails.
                pass


def locate(apptainer_dir_env: str | None = None) -> Path:
    if apptainer_dir_env is None:
        apptainer_dir_env = os.environ.get("APPTAINER_DIR", "")
    if apptainer_dir_env:
        apptainer_dir = resolve_path(apptainer_dir_env)
        candidate = (apptainer_dir / "apptainer") if apptainer_dir else None
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise LaunchError(
            f"apptainer not found at {candidate}.",
            hint="Set APPTAINER_DIR in config.env or add apptainer to PATH.",
        )
    which = shutil.which("apptainer")
    if which:
        return Path(which)
    raise LaunchError(
        "apptainer not found.",
        hint="Set APPTAINER_DIR in config.env or add apptainer to PATH.",
    )


def list_instances(apptainer_bin: Path) -> list[str]:
    result = subprocess.run(
        [str(apptainer_bin), "instance", "list"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    names: list[str] = []
    for i, line in enumerate(result.stdout.splitlines()):
        if i == 0:
            continue
        parts = line.split()
        if parts:
            names.append(parts[0])
    return names


def instance_exists(apptainer_bin: Path, name: str) -> bool:
    return name in list_instances(apptainer_bin)


def stop_instance(apptainer_bin: Path, name: str, *, force: bool = False) -> None:
    cmd = [str(apptainer_bin), "instance", "stop"]
    if force:
        cmd.append("-F")
    cmd.append(name)
    subprocess.run(cmd, capture_output=True)


def stop_instances(apptainer_bin: Path, prefix: str) -> None:
    """Stop every running instance whose name starts with *prefix*.

    Used before a session starts, to clear an instance its previous launch left
    behind. We do not use ``fuser`` here: on hosts with stale autofs mounts it
    can sit in uninterruptible D-state and hang the launcher. ``-F`` keeps
    ``instance stop`` from blocking on a daemon that ignores SIGTERM.
    """
    stopped_any = False
    for inst in list_instances(apptainer_bin):
        if inst == prefix or inst.startswith(prefix):
            print(f"Stopping stale apptainer instance: {inst}", flush=True)
            stop_instance(apptainer_bin, inst, force=True)
            stopped_any = True
    if stopped_any:
        time.sleep(1)


def start_instance(
    apptainer_bin: Path,
    name: str,
    image: Path,
    *,
    cleanenv: bool = True,
    overlay: Path | None = None,
    binds: Iterable[Bind] = (),
    envs: dict[str, str] | None = None,
    log_path: Path | None = None,
    no_mount: Iterable[str] = (),
) -> subprocess.CompletedProcess:
    # Intentionally no --fakeroot: the LD_PRELOAD/libfakeroot path apptainer
    # uses without /etc/subuid entries deadlocks the host-bound claude binary
    # at startup. The session runs with the invoking user's uid; the writable
    # overlay is user-owned, so /opt, /usr/local, ... stay writable.
    cmd: list[str] = [str(apptainer_bin), "instance", "start"]
    if cleanenv:
        cmd.append("--cleanenv")
    if no_mount:
        cmd += ["--no-mount", ",".join(no_mount)]
    for k, v in (envs or {}).items():
        cmd += ["--env", f"{k}={v}"]
    for host, cont, opts in binds:
        spec = f"{host}:{cont}" + (f":{opts}" if opts else "")
        cmd += ["-B", spec]
    if overlay:
        cmd += ["--overlay", str(overlay)]
    cmd += [str(image), name]

    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "wb") as f:
            return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return subprocess.run(cmd, capture_output=True)


def prep_overlay_dirs(
    apptainer_bin: Path, image: Path, overlay: Path, dirs: Iterable[str],
) -> None:
    """Create the bind-mount targets inside the overlay before the instance starts."""
    script = (
        f'for d in {" ".join(dirs)}; do\n'
        f'  [ -e "$d" ] || [ -L "$d" ] || mkdir -p "$d"\n'
        f'done'
    )
    subprocess.run(
        [str(apptainer_bin), "exec", "--overlay", str(overlay), str(image), "bash", "-c", script],
        capture_output=True,
    )


def _instance_state_root() -> Path:
    """Apptainer per-user instance state dir: ~/.apptainer/instances/app/<host>/<user>."""
    base = os.environ.get("APPTAINER_CONFIGDIR") or os.path.join(
        os.path.expanduser("~"), ".apptainer",
    )
    host = subprocess.run(
        ["hostname", "-s"], capture_output=True, text=True,
    ).stdout.strip() or "localhost"
    user = subprocess.run(
        ["id", "-un"], capture_output=True, text=True,
    ).stdout.strip() or os.environ.get("USER", "unknown")
    return Path(base) / "instances" / "app" / host / user


def _state_pid(state_file: Path) -> int | None:
    try:
        data = json.loads(state_file.read_text())
    except (OSError, ValueError):
        return None
    pid = data.get("ppid") or data.get("pid")
    try:
        return int(pid) if pid is not None else None
    except (TypeError, ValueError):
        return None


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def cleanup_orphan_instance_state(prefix: str) -> None:
    """Remove orphan apptainer instance state dirs for ``<prefix>*``.

    A SIGKILL'd run can leave ``~/.apptainer/instances/.../<name>/<name>.json``
    behind although the daemon is gone. The next ``instance start`` would then
    dodge the stale entry with a ``-1``/``-2`` suffix, and the stop on exit
    would not find it. Deleting dirs whose recorded PID is dead lets the new
    run reuse the canonical name.
    """
    root = _instance_state_root()
    if not root.is_dir():
        return
    for inst_dir in root.glob(f"{prefix}*"):
        if not inst_dir.is_dir():
            continue
        state_file = inst_dir / f"{inst_dir.name}.json"
        if not state_file.is_file():
            continue
        pid = _state_pid(state_file)
        if pid is None or not _pid_alive(pid):
            shutil.rmtree(inst_dir, ignore_errors=True)


def force_kill_instance_state(name: str) -> None:
    """SIGKILL the daemon recorded in ``<name>/<name>.json`` and remove the dir.

    A backstop for when ``instance stop -F`` was ignored. No-op when the state
    file is already gone.
    """
    state_file = _instance_state_root() / name / f"{name}.json"
    if not state_file.is_file():
        return
    pid = _state_pid(state_file)
    if pid is not None and _pid_alive(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    shutil.rmtree(state_file.parent, ignore_errors=True)
