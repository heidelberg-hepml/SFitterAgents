from __future__ import annotations

import fcntl
import os
from contextlib import contextmanager
from pathlib import Path

from .errors import LaunchError


def is_locked(lock_path: Path) -> bool:
    """True when a launch currently holds *lock_path*.

    Opened read-write: on NFS, flock() is emulated with POSIX record locks and
    taking LOCK_EX on a read-only descriptor fails. No O_CREAT, so probing never
    creates the lock file.
    """
    try:
        fd = os.open(str(lock_path), os.O_RDWR)
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    except OSError:
        return False
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


@contextmanager
def session_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            os.close(fd)
            # One launch per session: a session owns its output/, memory and
            # wiki, and two containers writing them at once would corrupt
            # both. Different sessions have different locks and run
            # concurrently.
            raise LaunchError(
                f"this session is already running (lock: {lock_path})",
                hint="Wait for it to exit, or start or fork another session with "
                     "./sfitteragents.sh — different sessions run concurrently.",
            ) from e
        os.ftruncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode())
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(fd)
        except OSError:
            pass
