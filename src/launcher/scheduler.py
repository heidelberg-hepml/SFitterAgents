"""Make the host's SLURM reachable from inside the container.

Binds the host's SLURM configuration and its auth socket, so the ``sbatch`` /
``squeue`` / ``sinfo`` clients baked into the image talk to the same controller
the host does. Both deployment styles are supported:

- **classic** — a real ``/etc/slurm/slurm.conf`` plus munge auth: bind the
  config dir and the munge socket.
- **configless + auth/slurm** — no ``/etc/slurm/slurm.conf``; the fetched
  config lives under ``/run/slurm/conf`` (a symlink into slurmd's conf cache)
  and auth goes through ``/run/slurm/sack.socket``.

Controlled by ``BIND_SLURM`` (config.env or the caller env):

- unset / ``auto`` — bind when the host looks like a SLURM submit host.
- ``0`` — never bind.
- ``1`` — require it; fail at launch if the host has no SLURM configuration.

Other schedulers are not integrated.
"""
from __future__ import annotations

import os
from pathlib import Path

from .errors import LaunchError

#: Intentionally empty SPANK plugstack, bound over the host's (see below).
_EMPTY_PLUGSTACK = Path(__file__).with_name("slurm_empty_plugstack.conf")


def host_passthrough() -> tuple[
    list[tuple[str, str, str | None]], dict[str, str], list[str]
]:
    """Probe the host for SLURM and return the integration data.

    Returns ``(binds, env_vars, detected)``: ``binds`` are ``(host_path,
    container_path, mode)`` tuples (``mode`` is ``"ro"`` or ``None`` for rw),
    ``env_vars`` are env vars the container should see, and ``detected`` names
    what was found, for logging. All three are empty on a host without SLURM,
    so the same image runs unchanged on a workstation.
    """
    binds: list[tuple[str, str, str | None]] = []
    envs: dict[str, str] = {}
    detected: list[str] = []

    setting = (os.environ.get("BIND_SLURM") or "auto").strip().lower()
    if setting in ("0", "off", "no", "false"):
        return binds, envs, detected

    classic_conf = Path("/etc/slurm/slurm.conf")
    run_dir = Path("/run/slurm")
    sack = run_dir / "sack.socket"
    configless_conf = run_dir / "conf"  # symlink -> slurmd conf cache
    if not (classic_conf.exists() or sack.exists() or configless_conf.exists()):
        if setting in ("1", "on", "yes", "true"):
            raise LaunchError(
                "BIND_SLURM=1 but this host has no SLURM configuration "
                "(/etc/slurm/slurm.conf or /run/slurm).",
                hint="Unset BIND_SLURM (or set it to 0) to run without a scheduler, "
                     "or launch from a SLURM submit host.",
            )
        return binds, envs, detected

    if classic_conf.exists():
        binds.append(("/etc/slurm", "/etc/slurm", "ro"))
    if run_dir.is_dir():
        # Brings sack.socket and the conf symlink into the container at the same path.
        binds.append(("/run/slurm", "/run/slurm", None))
        # The configless conf is a symlink; bind its real target too so it
        # resolves in the container, and point the client at it explicitly.
        try:
            target = configless_conf.resolve()
            if target.is_dir() and str(target) != "/run/slurm/conf":
                binds.append((str(target), str(target), "ro"))
                # The site's plugstack.conf may `required` a SPANK plugin that
                # is absent from the image or built for another SLURM version,
                # which aborts in-container sbatch. The container needs none of
                # them, so bind an empty plugstack over it; RPC to the
                # controller is unaffected.
                plugstack = target / "plugstack.conf"
                if _EMPTY_PLUGSTACK.is_file() and plugstack.exists():
                    binds.append((str(_EMPTY_PLUGSTACK), str(plugstack), "ro"))
            if (configless_conf / "slurm.conf").exists():
                envs["SLURM_CONF"] = "/run/slurm/conf/slurm.conf"
        except OSError:
            pass
    # Auth: the sack socket if present (auth/slurm), else the munge socket.
    if not sack.exists():
        for munge_dir in ("/var/run/munge", "/run/munge"):
            if Path(munge_dir).is_dir() and any(Path(munge_dir).iterdir()):
                binds.append((munge_dir, munge_dir, None))
                break
    detected.append("SLURM")
    return binds, envs, detected
