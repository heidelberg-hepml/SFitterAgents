#!/usr/bin/env bash
# Build the SFitterAgents image: MadGraph (NLO stack) + the SFitter fitting tool
# (sfitter/ in this repository) + CUDA PyTorch.
#
#   ./image/create_image.sh                 image/sfitteragents.sif + image/sfitteragents_sandbox/
#   ./image/create_image.sh --sandbox-only  only the sandbox directory (no .sif, no mksquashfs)
#
# The launcher runs the sandbox DIRECTORY when it exists: on a host without
# squashfuse, apptainer cannot mount a .sif and would extract the whole image
# (~8 GB) into a temporary sandbox on every launch. The .sif is the portable,
# distributable artifact.
#
# UNPRIVILEGED BUILD: `apptainer build --fakeroot` needs no sudo and no
# /etc/subuid mapping. Without a subuid mapping apptainer falls back to a
# root-mapped user namespace and runs %post under its bundled `faked`, which
# fakes the chown/ownership operations a single-uid namespace rejects. `faked`
# needs GLIBC >= 2.38, which the Debian trixie base provides — and it is
# REQUIRED here: slurm-client pulls in munge, whose postinst chowns its dirs.
#
# The build is heavy (MadGraph + tools + CUDA torch: several GB, tens of
# minutes). Run it on a quiet node, or submit it as a batch job.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CONFIG_PATH="${REPO_ROOT}/config.env"
if [[ -f "$CONFIG_PATH" ]]; then
  set -a; # shellcheck disable=SC1090
  source "$CONFIG_PATH"; set +a
fi
# config.env's runtime overlay settings must not leak into the build: `apptainer
# build` runs %post in --writable mode, and an inherited overlay aborts it
# ("cannot use --overlay in conjunction with --writable").
unset APPTAINER_OVERLAY APPTAINER_OVERLAYIMAGE APPTAINER_WRITABLE

SANDBOX_ONLY="${IMAGE_SANDBOX_ONLY:-0}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sandbox-only) SANDBOX_ONLY=1; shift ;;
    -h|--help) sed -n '2,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ERROR: unknown option: $1" >&2; exit 2 ;;
  esac
done

# Create apptainer temp/cache dirs named by env but missing on this node.
[[ -n "${APPTAINER_CACHEDIR-}" ]] && mkdir -p "${APPTAINER_CACHEDIR}"
[[ -n "${APPTAINER_TMPDIR-}" ]] && mkdir -p "${APPTAINER_TMPDIR}"

# --- Locate apptainer (APPTAINER_DIR or PATH) ---
APPTAINER_BIN=""
if [[ -n "${APPTAINER_DIR-}" ]]; then
  APPTAINER_DIR="${APPTAINER_DIR/#\~/$HOME}"
  [[ "$APPTAINER_DIR" == /* ]] || APPTAINER_DIR="${REPO_ROOT}/${APPTAINER_DIR}"
fi
if [[ -n "${APPTAINER_DIR-}" && -x "${APPTAINER_DIR%/}/apptainer" ]]; then
  APPTAINER_BIN="${APPTAINER_DIR%/}/apptainer"
else
  APPTAINER_BIN="$(command -v apptainer || true)"
fi
[[ -n "$APPTAINER_BIN" ]] || { echo "ERROR: apptainer not found (set APPTAINER_DIR in config.env)." >&2; exit 1; }

IMAGES_DIR="${REPO_ROOT}/image"
SIF_PATH="${IMAGES_DIR}/sfitteragents.sif"
SANDBOX_DIR="${IMAGES_DIR}/sfitteragents_sandbox"
DEF_PATH="${IMAGES_DIR}/sfitteragents.def"
[[ -f "$DEF_PATH" ]] || { echo "ERROR: $DEF_PATH not found." >&2; exit 1; }

# --- Stage the SFitter source ---
# %files does not follow symlinks out of the build context, and a working copy
# may carry run output, so stage a clean copy at the path the .def references.
# SFITTER_SRC (config.env) points at another checkout; default: sfitter/ here.
SFITTER_SRC="${SFITTER_SRC:-${REPO_ROOT}/sfitter}"
SFITTER_SRC="${SFITTER_SRC/#\~/$HOME}"
[[ "$SFITTER_SRC" == /* ]] || SFITTER_SRC="${REPO_ROOT}/${SFITTER_SRC}"
[[ -f "${SFITTER_SRC%/}/setup.py" ]] || {
  echo "ERROR: no SFitter source at ${SFITTER_SRC} (expected setup.py)." >&2
  exit 1
}
STAGING_DIR="${IMAGES_DIR}/.build/sfitter"
rm -rf "${IMAGES_DIR}/.build"
mkdir -p "$STAGING_DIR"
echo "Staging SFitter source ${SFITTER_SRC} -> ${STAGING_DIR} ..."
rsync -a --exclude='.git' --exclude='output' --exclude='runfiles' --exclude='run_scripts' \
      --exclude='__pycache__' --exclude='*.egg-info' \
      "${SFITTER_SRC%/}/" "$STAGING_DIR/"

# --- Remove any stale sandbox ---
# Built under the fakeroot namespace, some of its dirs are read-only, and a plain
# `rm -rf` leaves a half-removed tree. Make it user-writable first.
if [[ -e "$SANDBOX_DIR" ]]; then
  echo "Found existing sandbox at $SANDBOX_DIR — removing it..."
  chmod -R u+rwX -- "$SANDBOX_DIR" 2>/dev/null || true
  rm -rf -- "$SANDBOX_DIR"
fi

if [[ "$SANDBOX_ONLY" == "1" ]]; then
  # Straight to the sandbox directory: skips mksquashfs, which is unnecessary
  # without squashfuse and can abort compressing a large rootfs.
  echo "Building sandbox directly (no .sif): $SANDBOX_DIR"
  ( cd "$REPO_ROOT"; "$APPTAINER_BIN" build --sandbox --fakeroot "$SANDBOX_DIR" "$DEF_PATH" )
else
  if [[ -e "$SIF_PATH" ]]; then
    echo "Found existing image at $SIF_PATH — removing it..."
    rm -f -- "$SIF_PATH"
  fi
  echo "Building image: $APPTAINER_BIN build --fakeroot $SIF_PATH $DEF_PATH"
  ( cd "$REPO_ROOT"; "$APPTAINER_BIN" build --fakeroot "$SIF_PATH" "$DEF_PATH" )
  echo "Done. Built: $SIF_PATH"
  # Extract the sandbox once. Keep the conversion scratch on the image's
  # disk-backed filesystem, never a RAM-backed /tmp.
  echo "Creating sandbox directory from the .sif: $SANDBOX_DIR"
  SANDBOX_TMP="${IMAGES_DIR}/.sandbox_tmp"
  rm -rf "$SANDBOX_TMP"; mkdir -p "$SANDBOX_TMP"
  ( cd "$REPO_ROOT"; APPTAINER_TMPDIR="$SANDBOX_TMP" "$APPTAINER_BIN" build --sandbox "$SANDBOX_DIR" "$SIF_PATH" )
  rm -rf "$SANDBOX_TMP"
fi

rm -rf "${IMAGES_DIR}/.build"
echo "Done. Sandbox: $SANDBOX_DIR"
echo "Start the agent with: ./sfitteragents.sh"
