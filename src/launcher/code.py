"""Start one SFitter agent session inside the container.

``./sfitteragents.sh`` picks or creates a session and hands off here with
``SFA_SESSION_DIR`` set (see ``sessions.py`` for the session layout). The
session is bound into an Apptainer instance and Claude Code runs in it:

    host                                   container
    <session>/output                    -> /output           CWD and project root
    <session>/.claude                   -> /output/.claude   roster, skills, memory slates
    <session>/agent_wikis               -> /agent_wikis
    <session>/docs                      -> /sfitter_docs     read-only
    <session>/workspace                 -> /workspace        scratch, kept across launches
    <session>/run/workdirs/<stamp>/home -> /session-home     $HOME, fresh per launch
    CLAUDE_CONFIG_DIR                   -> /opt/.config/.claude
    cluster scratch                     -> same path ($CLUSTER_RUNS)
    internals/ (if present)             -> /internals        read-only

The host home directory and working directory are not mounted.

Arguments are forwarded verbatim to ``claude``. Without the menu (e.g. for a
script), a session can be started directly:

    SFA_SESSION_DIR=sessions/<id> PYTHONPATH=src python3 -m launcher code --resume <conversation-id>
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import apptainer, claude_binary, cluster_jobs, scheduler, sessions
from .errors import LaunchError, die
from .lock import session_lock
from .paths import AGENT_SYSTEM_DIR, REPO_ROOT, ensure_image, resolve_path
from .settings import assert_no_api_keys, load_config_env, scrub_api_keys
from .workdir import make_session_uuid, make_stamp, make_workdir

#: Default images, in order of preference, when APPTAINER_IMAGE is not set. The
#: sandbox directory comes first: it starts without squashfuse, where a .sif
#: would be extracted into a temporary sandbox on every launch.
_DEFAULT_IMAGES = ("image/sfitteragents_sandbox", "image/sfitteragents.sif")

#: Bind-mount targets created inside the overlay before the instance starts.
_MOUNT_POINTS = (
    "/workspace", "/output", "/sfitter_docs", "/agent_wikis", "/session-home",
    "/opt/claude", "/opt/.config/.claude",
)

#: In-container paths that may surface as a session cwd. Pre-trusting them
#: keeps the first-time trust dialog from blocking startup — and trust is what
#: makes Claude Code honor the session's settings.local.json (auto-memory).
#: Trust is exact-match; subdirectories do not inherit it.
_TRUSTED_CONTAINER_PATHS = ("/output", "/workspace", "/tmp", "/sfitter_docs", "/agent_wikis")

#: Appended to the lead's system prompt, in this order. Subagents never see them.
SYSTEM_PROMPT_FILES = ("lead-discipline.md", "sf-discipline.md")

#: Where the lead's auto-memory slate lives in the container.
LEAD_MEMORY_DIR = "/output/.claude/lead-memory"


def _resolve_image() -> Path:
    explicit = resolve_path(os.environ.get("APPTAINER_IMAGE"))
    if explicit is not None:
        return explicit
    for rel in _DEFAULT_IMAGES:
        if (REPO_ROOT / rel).exists():
            return REPO_ROOT / rel
    return REPO_ROOT / _DEFAULT_IMAGES[-1]


def _new_overlay() -> Path:
    """Create a fresh directory overlay for one launch, private to its user.

    A directory overlay's upper/work layers must live on a filesystem that can
    back overlayfs; a network filesystem (NFS, Lustre, ...) cannot, and that is
    often where a repository lives on a cluster. ``mkdtemp`` creates it with
    mode 0700 under an unpredictable name — in the system temp dir, or in
    OVERLAY_BASE (e.g. /dev/shm/<user>) when set — so no other local user can
    prepare or swap it.
    """
    base = resolve_path(os.environ.get("OVERLAY_BASE"))
    if base is not None:
        base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="sfitteragents-overlay-",
                                 dir=str(base) if base is not None else None))


def _rm_writable_tree(path: Path) -> None:
    """Remove a tree whose overlayfs work/ layer may be mode 000 (chmod first, then rmtree)."""
    subprocess.run(["chmod", "-R", "u+rwX", str(path)], capture_output=True)
    shutil.rmtree(path, ignore_errors=True)


def _session_tree(session_dir: Path, name: str) -> Path:
    """The session's own ``docs/`` / ``prompts/``, or the shipped one for an older session."""
    own = session_dir / name
    return own if own.is_dir() else AGENT_SYSTEM_DIR / name


def _seed_trusted_projects(claude_config_dir: Path) -> None:
    """Mark the in-container mount roots as trusted in ``<config>/.claude.json``.

    Idempotent: only adds ``hasTrustDialogAccepted`` where it is missing and
    leaves every other key untouched. Claude Code fills in the rest of a fresh
    file on first run.
    """
    config_path = claude_config_dir / ".claude.json"
    try:
        data = json.loads(config_path.read_text())
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    projects = data.get("projects")
    if not isinstance(projects, dict):
        projects = {}
        data["projects"] = projects
    changed = False
    for path in _TRUSTED_CONTAINER_PATHS:
        entry = projects.get(path)
        if not isinstance(entry, dict):
            entry = {}
            projects[path] = entry
            changed = True
        if not entry.get("hasTrustDialogAccepted"):
            entry["hasTrustDialogAccepted"] = True
            changed = True
    if changed:
        config_path.write_text(json.dumps(data, indent=2) + "\n")


def _pin_auto_memory(claude_dir: Path) -> None:
    """Turn auto-memory on and point the lead's slate at the session, in settings.local.json.

    Consultant slates are placed by the ``memory: project`` line on each agent
    card; the lead has no card, so its slate loads only through
    ``autoMemoryDirectory``. Pinning both keys in the session's local settings
    keeps a user's own Claude config (bound into the container) from switching
    the learned tier off, and — unlike user-level settings — never redirects
    the memory of the user's other Claude Code sessions.
    """
    path = claude_dir / "settings.local.json"
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    wanted = {"autoMemoryEnabled": True, "autoMemoryDirectory": LEAD_MEMORY_DIR}
    if any(data.get(k) != v for k, v in wanted.items()):
        data.update(wanted)
        path.write_text(json.dumps(data, indent=2) + "\n")


def _prepare_output_root(output_dir: Path) -> None:
    """Make ``/output`` a deterministic Claude Code project root.

    The consultant cards declare their slates at
    ``/output/.claude/agent-memory/<name>/MEMORY.md``, which Claude Code
    resolves against the project root — so ``git init`` pins the root to
    ``/output`` regardless of where an agent ``cd``s, and the ``.claude``
    mountpoint is pre-created so the nested bind attaches.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if not (output_dir / ".git").exists():
        try:
            subprocess.run(["git", "init", "-q", str(output_dir)], check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            raise LaunchError(
                f"could not git-init the session's output dir {output_dir}: {e}",
                hint="Install git on the host; the session's project root needs it.",
            ) from e
    (output_dir / ".claude").mkdir(exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    load_config_env()
    scrub_api_keys()

    session_dir = resolve_path(os.environ.get("SFA_SESSION_DIR"))
    if session_dir is None or not (session_dir / ".claude").is_dir():
        die(
            "no session to start (SFA_SESSION_DIR is unset, or has no .claude/).",
            hint="Start sessions with ./sfitteragents.sh.",
        )
    session_dir = session_dir.resolve()
    output_dir = session_dir / "output"
    run_dir = session_dir / "run"
    wiki_dir = session_dir / "agent_wikis"
    workspace_dir = session_dir / "workspace"
    docs_dir = _session_tree(session_dir, "docs")
    prompts_dir = _session_tree(session_dir, "prompts")
    cluster_runs = sessions.cluster_runs_dir(session_dir)
    claude_config_dir = sessions.claude_config_dir()
    instance_prefix = sessions.instance_prefix(session_dir.name)
    internals = REPO_ROOT / "internals"

    apptainer_bin = apptainer.locate()
    apptainer.ensure_env_dirs()
    image = _resolve_image()
    ensure_image(image, hint="Build it first: ./image/create_image.sh (or set APPTAINER_IMAGE).")
    sched_binds, sched_envs, sched_detected = scheduler.host_passthrough()

    # Writable overlay. Default: a fresh directory overlay on local disk,
    # removed on exit — every piece of durable state is bound from the host, so
    # the overlay only catches incidental writes. APPTAINER_OVERLAY overrides.
    overlay = resolve_path(os.environ.get("APPTAINER_OVERLAY"))
    if overlay is None:
        overlay = _new_overlay()
        atexit.register(_rm_writable_tree, overlay)
        print(f"sfitteragents: per-session overlay {overlay} (removed on exit)", flush=True)
    if overlay.suffix == ".img":
        if not overlay.is_file():
            die(
                f"overlay image not found at {overlay}.",
                hint="Create one with `apptainer overlay create --sparse --size 10240 <path>`, "
                     "or leave APPTAINER_OVERLAY empty for a per-session directory overlay.",
            )
    else:
        # Directory overlay: kernel overlayfs needs both layers to exist.
        (overlay / "upper").mkdir(parents=True, exist_ok=True)
        (overlay / "work").mkdir(parents=True, exist_ok=True)

    print(f"sfitteragents: image {image}", flush=True)

    run_dir.mkdir(parents=True, exist_ok=True)
    with session_lock(run_dir / ".lock"):
        stamp = make_stamp()
        workdir = make_workdir(run_dir / "workdirs", stamp=stamp)
        (workdir / "home").mkdir()
        session_uuid = make_session_uuid()
        (workdir / "logs" / "session_uuid").write_text(session_uuid)
        session_id_args = (
            [] if sessions.argv_pins_conversation(argv) else ["--session-id", session_uuid]
        )

        claude_config_dir.mkdir(parents=True, exist_ok=True)
        _seed_trusted_projects(claude_config_dir)
        _pin_auto_memory(session_dir / ".claude")
        _prepare_output_root(output_dir)
        wiki_dir.mkdir(exist_ok=True)
        workspace_dir.mkdir(exist_ok=True)
        cluster_runs.mkdir(parents=True, exist_ok=True)
        host_claude = claude_binary.detect_host_claude()

        instance_name: str | None = None
        cleaned = [False]

        def _do_cleanup() -> None:
            if cleaned[0] or instance_name is None:
                return
            cleaned[0] = True
            try:
                apptainer.stop_instance(apptainer_bin, instance_name, force=True)
                # Backstop when -F was swallowed: SIGKILL the recorded daemon
                # and drop its state dir so the next launch can reuse the name.
                apptainer.force_kill_instance_state(instance_name)
            except Exception as exc:
                print(f"WARN: instance cleanup raised {exc!r}", file=sys.stderr)

        # Registered after the overlay removal, so atexit's LIFO order stops
        # the instance before its overlay is deleted.
        atexit.register(_do_cleanup)

        if sched_detected:
            print(
                f"sfitteragents: {', '.join(sched_detected)} detected — the container's "
                "clients submit to this host's controller.",
                flush=True,
            )

        try:
            apptainer.stop_instances(apptainer_bin, instance_prefix)
            apptainer.cleanup_orphan_instance_state(instance_prefix)
            mount_points = [*_MOUNT_POINTS] + (["/internals"] if internals.is_dir() else [])
            apptainer.prep_overlay_dirs(apptainer_bin, image, overlay, mount_points)

            instance_name = f"{instance_prefix}-{stamp}"
            # In the cluster scratch, so a compute node reaches it even when the
            # repository is not on shared storage.
            (cluster_runs / ".sfitteragents").mkdir(exist_ok=True)
            cluster_exec = cluster_jobs.write_cluster_exec(
                script_path=cluster_runs / ".sfitteragents" / "cluster-exec",
                apptainer_bin=apptainer_bin,
                image=image,
                cluster_runs_path=cluster_runs,
                internals_path=internals,
            )

            binds: list[apptainer.Bind] = [
                (str(workspace_dir), "/workspace", None),
                # A private $HOME per launch, so MG5's ~/.mg5 and other tools'
                # per-user state never touch the host home. HOME itself is set
                # in the exec wrapper below: apptainer refuses it via --env.
                (str(workdir / "home"), "/session-home", None),
                (str(claude_config_dir), "/opt/.config/.claude", None),
                (str(output_dir), "/output", None),
                # After /output, so the parent bind is in place.
                (str(session_dir / ".claude"), "/output/.claude", None),
                (str(wiki_dir), "/agent_wikis", None),
                (str(docs_dir), "/sfitter_docs", "ro"),
                # Same absolute path inside and outside: job scripts written in
                # the container mean the same thing on a compute node.
                (str(cluster_runs), str(cluster_runs), None),
                (str(cluster_exec), "/usr/local/bin/cluster-exec", "ro"),
                *sched_binds,
            ]
            if host_claude is not None:
                binds.append((str(host_claude.install_dir), "/opt/claude", "ro"))
            if internals.is_dir():
                # Site-specific facts (e.g. cluster_info.md), git-ignored.
                binds.append((str(internals), "/internals", "ro"))

            envs = {
                "TERM": os.environ.get("TERM", "xterm-256color"),
                "LANG": os.environ.get("LANG", "C.UTF-8"),
                "CLAUDE_CONFIG_DIR": "/opt/.config/.claude",
                "CLUSTER_EXEC": str(cluster_exec),
                "CLUSTER_RUNS": str(cluster_runs),
                **sched_envs,
            }
            apptainer_log = workdir / "logs" / "apptainer.log"
            result = apptainer.start_instance(
                apptainer_bin, instance_name, image,
                overlay=overlay, binds=binds, envs=envs, log_path=apptainer_log,
                # Everything the session needs is bound explicitly above; the
                # host home (with its credentials and shell config) stays out.
                no_mount=("home", "cwd"),
            )
            if result.returncode != 0:
                die(f"failed to start Apptainer instance '{instance_name}'. See {apptainer_log}")
            (workdir / "logs" / "instance_name.txt").write_text(f"{instance_name}\n")
            print(f"Apptainer instance: {instance_name}", flush=True)

            if host_claude is not None:
                claude_bin = host_claude.container_bin_path
            else:
                claude_bin = claude_binary.resolve_in_container(apptainer_bin, instance_name)
                if not claude_bin:
                    print("Claude Code not found on host. Installing inside the container...")
                    claude_bin = claude_binary.install_in_container(apptainer_bin, instance_name)

            exec_envs = {
                **envs,
                **{k: v for k, v in os.environ.items() if k.startswith("CLAUDE_CODE_")},
            }
            system_prompt = "\n\n".join(
                (prompts_dir / name).read_text() for name in SYSTEM_PROMPT_FILES
            )
            # The image's Python environment (MadGraph, SFitter, numpy, torch)
            # is activated for the session, as cluster-exec does for jobs: the
            # system python lacks MadGraph's dependencies.
            claude_argv = [
                "bash", "-c",
                "export HOME=/session-home; . /opt/envs/MAD/bin/activate 2>/dev/null || true; "
                'export PATH="/root/.local/bin:${PATH}"; exec "$@"', "_",
                claude_bin,
                "--append-system-prompt", system_prompt,
                *session_id_args,
                *argv,
            ]
            cmd = [str(apptainer_bin), "exec", "--cleanenv"]
            for k, v in exec_envs.items():
                cmd += ["--env", f"{k}={v}"]
            cmd += ["--pwd", "/output", f"instance://{instance_name}", *claude_argv]

            # Final guard: nothing auth-related may reach the claude process.
            # --cleanenv strips the host env; this catches a programming error.
            for k in exec_envs:
                if k.endswith("_API_KEY") or k.endswith("_AUTH_TOKEN"):
                    die(f"refusing to exec claude: its environment contains {k!r}")
            assert_no_api_keys()

            subprocess.run(cmd)
        finally:
            _do_cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
