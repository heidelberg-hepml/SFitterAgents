---
name: cluster-submission
description: Use when about to launch compute-intensive work — MadGraph event generation expected to exceed a few minutes wall time, high-statistics or NLO runs, parameter sweeps, GPU work, anything that needs significant CPU/RAM. Covers when to submit vs run locally, partition selection, the in-container submission infrastructure (`$CLUSTER_RUNS`, `$CLUSTER_EXEC`), job-script composition, status checking, and lead-side delegation discipline. Skip for quick syntax checks, single-event probes, file inspections.
---

# Cluster submission for compute-intensive work

Compute-heavy work MUST be submitted to the cluster, never run locally on the launch node. Local execution on a shared interactive node is for quick checks; long or resource-heavy work belongs on the cluster.

## When to submit

Any of these holds:

- Expected wall time exceeds a few minutes.
- Needs significant CPU (more than a couple of cores), memory beyond a few GB, or any GPU.
- High-statistics or NLO event generation, a parameter sweep, or anything with a known long runtime.
- Benefits from a dedicated walltime budget that interactive use cannot guarantee.

## When to run locally

- Quick syntax / sanity checks.
- Small interactive probes whose output you read live.
- Submission overhead would dominate the actual work.

## What compute is available — read `/internals/cluster_info.md`

If it exists, that file is the authoritative catalog of this deployment's clusters, partitions with CPU / RAM / GPU specs and walltime limits, submit-host hostnames, auth / network quirks, and etiquette. Treat it as ground truth.

If absent, probe `sinfo` / `sbatch` for what is available, and say in your output you are operating without site facts.

## Choose a partition

Pick the smallest partition whose limits satisfy your job's needs. Among candidates that fit, prefer:

- Idle or mixed nodes over fully busy ones.
- A walltime limit comfortably larger than your estimate but not vastly so (short walltime limits typically start sooner).
- Features (GPU, large memory) that match actual requirements; do not request features you do not use.

When the choice is non-obvious, ask the user before submitting.

## Submission infrastructure

The SLURM clients (`sbatch` / `squeue` / `sinfo` / `scancel`) work directly from this container — the launcher binds the host's SLURM configuration and auth socket. Two more pieces of plumbing make submission feel native:

**`$CLUSTER_RUNS`** — shared scratch bind-mounted at the **same absolute host path** inside the container as on the host. Compute nodes see this path natively via shared filesystem. **Use `$CLUSTER_RUNS/<jobname>/` for all inputs and outputs of every cluster job.** In-container-only paths (`/workspace`, `/output`, `/internals`) are not visible to compute nodes; never reference them from a job-script body.

**`$CLUSTER_EXEC`** — compute-node wrapper that runs commands inside `apptainer exec` against the same image + the `$CLUSTER_RUNS` bind, so the image's tools (`mg5_aMC`, `sfitter`, the Python environment) are available on the compute node. Two contexts:

| Where you are | Use |
|---|---|
| Inside this container (interactive, debugging) — *only where the host apptainer + image are bound in; see below* | `cluster-exec <command>` |
| Inside a job-script body (executed on the compute node) | `$CLUSTER_EXEC <command>` |

`cluster-exec` only exists in this container — never put it in a job-script body. Use `$CLUSTER_EXEC` (expanded absolute path).

**Interactive `cluster-exec` does not work in this container — don't mistake that for a fault.** The wrapper runs `apptainer exec <host-apptainer> … <image>`, so it needs the *host* apptainer binary and the image visible **inside** the lead container. The launcher deliberately does not nest the image, so a local `cluster-exec` fails with "apptainer not found" / the image path "does not exist." **That is expected, not a broken setup, and nothing to fix** — the image-exec step resolves only on the compute node. So never "test" the chain with a local `cluster-exec`; validate it end-to-end by submitting a small `sbatch` diagnostic job and reading its output.

`$CLUSTER_EXEC` and `$CLUSTER_RUNS` are NOT auto-forwarded by the scheduler. Both must be **expanded at job-script-write time** via an *unquoted* heredoc (`<<EOF`, not `<<'EOF'`) so absolute host paths are baked into the saved script.

`$CLUSTER_EXEC` runs against the image alone. Jobs see everything the image ships but NOT runtime installs made in this session (pip mid-session, mods under `/opt/`). Place runtime state under `$CLUSTER_RUNS` first if a job needs it. The cluster-exec container gets a per-invocation `--writable-tmpfs` for incidental writes; redirect bulk output to `$CLUSTER_RUNS/<jobname>/` so artifacts survive.

Job-script body shape (unquoted heredoc):

```
cat > $CLUSTER_RUNS/<jobname>/job.sh <<EOF
#!/bin/bash
#<scheduler-directives go here, with file paths under $CLUSTER_RUNS/<jobname>/>
cd $CLUSTER_RUNS/<jobname>
exec > $CLUSTER_RUNS/<jobname>/out.log 2>&1   # write the log to shared storage yourself (see below)
$CLUSTER_EXEC <your-command-and-args>
echo \$? > $CLUSTER_RUNS/<jobname>/exit_status
EOF
```

`$CLUSTER_EXEC` and `$CLUSTER_RUNS` expand at write time → absolute host paths in the saved script. `\$?` (single backslash) escapes `$` so the heredoc writes literal `$?` into the saved script — that variable then expands inside the job's shell at runtime to capture the main command's exit status. Do **not** write `\\$?` — the heredoc consumes one backslash and expands `$?` against the writing shell (typically 0 from the prior `cat`), and your captured exit status is silently always zero.

**Job stdout/stderr — write it to shared storage yourself; don't rely on the scheduler to deliver it.** The job redirects its own output to `$CLUSTER_RUNS/<jobname>/out.log` (the `exec > … 2>&1` line above) and you read it from there, wherever the scheduler puts its own captured streams.

## Resource sizing (MadGraph / SMEFTatNLO)

Scheduler resource directives are yours to set per job — there is **no baked default**, so size them to the work, not to a placeholder. MadGraph (especially SMEFTatNLO / NLO and multi-process scans) needs real memory and process headroom:

- **Memory** — floor of `--mem=4G` for a MadGraph process directory. A 1 GB request is far too small: the job is killed mid-`launch` as a silent OOM, which surfaces as a truncated/empty result, *not* a physics error. Scale up for high-statistics or many-process scans.
- **Process limit** — MadGraph + apptainer spawn many short-lived processes and routinely hit the default per-user `nproc` cap (the fingerprint is `fork: retry: Resource temporarily unavailable`, not an OOM). Raise it on the first line of the job body:
  ```
  ulimit -u 8192 2>/dev/null || true
  ```
- **Cores** — `--cpus-per-task=2` is a sane default; raise it only if the run actually parallelizes.
- **Walltime** — size to estimate with margin (a SMEFTatNLO SM+linear+quadratic scan is comfortably under `--time=06:00:00`); shorter limits often start sooner.
- **Transient drops** — wrap each `mg5_aMC` call in a 2–3 attempt retry loop; compute nodes occasionally drop a run for non-physics reasons, and a clean retry beats a resubmit.

## After submission

Wait for the job to finish before treating its output as authoritative. Slow does not mean stuck — never substitute a low-statistics local run for the high-statistics cluster job you are still waiting on. Read exit status and any error log before declaring success or diagnosing failure.

## Lead orchestration

You do not submit jobs yourself; you ensure the workers you dispatch do submit when warranted.

**Hard rule: every time you delegate compute-heavy work** (long launches, high-statistics or NLO event generation, parameter sweeps, GPU work, anything matching "When to submit"), **the dispatch must explicitly direct the worker to submit via the cluster**. Concretely:

- Explicit instruction to submit ("Run this on the cluster: write a job script under `$CLUSTER_RUNS/<jobname>/`, submit with `sbatch`, wait for completion").
- Pointer to `/internals/cluster_info.md` for partition choice (or the partition name if you've already picked).
- Reminder to capture exit status and read outputs from `$CLUSTER_RUNS/<jobname>/`.

**If a worker returns output from a compute-heavy task without evidence of cluster submission** (no job ID, no `$CLUSTER_RUNS/<jobname>/` entry, no `exit_status`, no `out.log` under `$CLUSTER_RUNS/<jobname>/`) — push back and require them to redo it through the cluster.

For tasks that are clearly NOT compute-heavy (quick syntax checks, single-event probes, plot rendering, file inspections), local execution is correct — don't over-direct.
