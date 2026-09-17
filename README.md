# SFitterAgents

[![arXiv](https://img.shields.io/badge/arXiv-2607.22813-b31b1b.svg)](https://arxiv.org/abs/2607.22813)

This repository contains **SFitter**, a tool for turning experimental measurements into constraints on
effective (SMEFT) operators, and **SFitterAgents**, a multi-agent system that automates the
reinterpretation: from a published measurement to a validated, fit-ready SFitter datacard — and, on
request, the fit itself.

- 📄 Paper: [arXiv:2607.22813](https://arxiv.org/abs/2607.22813)
- 🧮 The fitting code: [`sfitter/`](sfitter)
- 🤖 The agent system: [`sfitteragents/`](sfitteragents)
- 🧩 Built on [MadAgents](https://github.com/MadGraphTeam/MadAgents)

---

## What can I do with SFitterAgents?

Point it at a measurement — an arXiv paper, a HEPData record — and ask for its reinterpretation. The
lead agent routes every sub-question to a specialised agent, has the results checked by adversarial
reviewers, and walks the pipeline:

1. **Measurement extraction** (`/sf-extract`) — measured values, bin edges and per-bin, per-source
   uncertainties, into a reviewed extraction report.
2. **SM-prediction template** (`/sf-sm-template`) — the Standard-Model baseline at the right perturbative
   order (NNLO k-factors applied), with its theory-uncertainty budget.
3. **EFT parameterization** (`/sf-parameterize`) — SMEFTatNLO Wilson-coefficient scans with MadGraph, and
   the κ₁/κ₂ and interference terms extracted from them.
4. **Datacard assembly** (`/sf-datacard`) — the SFitter JSON observation + prediction entry, validated
   until it loads with SFitter's `ReadDataCard`.

`/sf-reinterpret` runs all four stages. After that, `/sf-fit` runs the standard SFitter fit and reads off
the intervals, and `/sf-diagnostics` offers optional physics cross-checks. Every stage keeps a
provenance record under `output/documentation/` as the work happens.

The SFitter layer sits **on top of** the MadGraph layer of [MadAgents](https://github.com/MadGraphTeam/MadAgents):
the predictions come from real MadGraph runs, set up and checked by the MadAgents consultants. Heavy
MadGraph runs and fits are submitted to a SLURM cluster (see [Cluster submission](#cluster-submission)).

---

## Repository layout

| Path | What it is |
| --- | --- |
| [`sfitter/`](sfitter) | The SFitter fitting code: the `sfitter` Python package and CLI, example datacards (`data/`), run cards (`params/`). |
| [`sfitteragents/`](sfitteragents) | The agent system: `.claude/` (61 agents, 18 skills, rules), `docs/` (the documentation library the agents cite), `prompts/` (the lead's system prompt). |
| `sfitteragents.sh` | Starts the agent — a menu to run, continue or remove a session. |
| `cleanup_sfitteragents.sh` | Stops a session a dead terminal left running. |
| [`image/`](image) | The Apptainer image: MadGraph 3.7 (NLO stack) + SMEFTatNLO + SFitter + CUDA PyTorch. |
| `src/launcher/` | The launcher behind the two scripts. |
| [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | Third-party components and their licenses. |

**The agents.** 15 `sf-` agents own the reinterpretation: measurement extraction, uncertainty naming and
decomposition, the SM order correction, scale / PDF / parametric theory uncertainties, scan design and
sanitisation, κ extraction, the SMEFTatNLO → SFitter convention translation, the datacard ID encoding,
a methodology advisor, and two reviewers (the reinterpretation reviewer and the datacard schema gate).
The 46 `ma-` agents are MadAgents' MadGraph consultants, reviewers, auditors and runtime probe.

---

## Quick start

You need a **Linux host** (or a Linux VM), **[Apptainer](https://apptainer.org/)**, `git`, `rsync` and
`python3` (≥ 3.10), and the **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)**,
installed and authenticated (a Claude subscription or API credits). Building the image needs internet
access and several GB of disk (the extracted sandbox alone is about 8 GB).

For a real reinterpretation you also need a **SLURM cluster**: the agents submit every MadGraph scan and
SFitter fit there, so launch from a submit host whose storage the compute nodes share, with GPU nodes
for the fits (see [Cluster submission](#cluster-submission)).

```bash
git clone https://github.com/heidelberg-hepml/SFitterAgents && cd SFitterAgents
cp config.env.example config.env    # set APPTAINER_DIR
./image/create_image.sh             # MadGraph + SFitter + CUDA PyTorch (tens of minutes)
./sfitteragents.sh
```

Then describe the task, for example `/sf-reinterpret <arXiv ID or HEPData record>`, and name the
operators you are interested in.

> **Permissions.** The shipped agent system pre-approves no tools, so a plain session asks before each
> tool call — and a reinterpretation makes a great many. Skipping those checks is a real decision:
> the container runs as your user and can write to the session, its cluster scratch, the mounted Claude
> config directory, and submit cluster jobs. If you make it, make it per launch:
> `./sfitteragents.sh --dangerously-skip-permissions`.

---

## Sessions

`./sfitteragents.sh` asks what to do:

- **Run the agent (new session)** — fork a new session from the **shipped agent system** (a clean, cold
  start) or from an **earlier session**, whose learned memory and wiki then carry over. A fork copies
  its source's whole agent system — agents, skills, rules, docs and prompts — not only its memory.
- **Continue a session** — re-enter a session in place and resume its conversation.
- **Remove a session** — delete it (after a typed confirmation).

Any argument is forwarded to `claude` (`--model`, `--dangerously-skip-permissions`, …).

A session is a self-contained directory under `sessions/`:

```
sessions/<stamp>__<label>/
  output/        deliverables and the documentation record — the session's project root
  .claude/       the agent system, with the memory slates of the lead and the agents
  agent_wikis/   the long-form wiki the slates index
  docs/          the documentation library (read-only in the container)
  prompts/       the lead's system prompt
  workspace/     scratch (/workspace in the container), kept across launches
  cluster_runs/  scratch for cluster jobs
  run/           logs, the session lock, one working directory per launch
  session.json   label, lineage, conversation id
```

The agents learn in two tiers: a short **memory** slate per agent, always loaded, and a **wiki** of
longer pages read on demand. A new session copies both from its source, so it extends its own copy and
the source stays unchanged — a session that went wrong is a dead branch; fork the last good one. Each
session has its own lock, overlay and container instance, so several sessions run concurrently from
one clone.

**Updating.** After `git pull`, rebuild the image if `image/` or `sfitter/` changed. Existing sessions,
and sessions forked from them, keep the agent system they were created with; start a new session from
the shipped agent system to use the updated one.

---

## Skills

You can invoke any of these by name, and the lead reaches for them on its own when a task calls for one.

| Skill | What it does |
| --- | --- |
| **`/sf-reinterpret`** | The whole pipeline, from a measurement to a validated datacard |
| **`/sf-extract`** | Extracts a measurement into a reviewed extraction report |
| **`/sf-sm-template`** | Builds the SM-prediction template with its theory uncertainties |
| **`/sf-parameterize`** | Runs the Wilson-coefficient scans and extracts the κ parameterization |
| **`/sf-datacard`** | Assembles and validates the SFitter datacard entry |
| **`/sf-fit`** | Runs the standard SFitter fit and reads off the intervals |
| **`/sf-diagnostics`** | Optional cross-checks on a fit, when you ask for them |
| **`/sf-document`** | Records a stage's provenance under `output/documentation/` |
| **`/sf-deep-verify`** | A heavy verification cascade on a deliverable, when you ask for one |
| **`/cluster-submission`** | How compute-heavy work is submitted to the cluster |
| **`/mg-setup`**, **`/mg-probe`**, **`/mg-deep-verify`**, **`/mg-study`** | MadGraph setup, runtime probing, deep verification, warm-up study |
| **`/ma-wiki-write`**, **`/ma-wiki-lint`**, **`/ma-reflect`**, **`/ma-doctor`** | Memory and wiki upkeep, hardening against past mistakes, auditing the agent system itself |

---

## Using SFitter on its own

SFitter is an ordinary Python package; the agents are not needed to run a fit. `sfitter/` is the
package as released, with its own [`README.md`](sfitter/README.md). From the root of this repository:

```bash
cd sfitter
pip install --editable . pyyaml
mkdir -p output                          # each run is written to output/<yyyymmdd_hhmmss>_<run_name>/
sfitter run params/top_fit.yaml --verbose
```

SFitter uses a GPU when one is available. In the image, the package source is at `/opt/sfitter`
(`$SFITTER_INSTALL`) and the `sfitter` CLI is in the `/opt/envs/MAD` environment; the `/sf-fit` skill
runs fits from a copy in the cluster scratch, where their output persists.

---

## Cluster submission

MadGraph scans and SFitter fits are **submitted to the cluster**, never run on the interactive node —
the `/cluster-submission` skill is the playbook the agents follow. On a SLURM submit host the launcher
binds the host's SLURM configuration and auth socket, so `sbatch` / `squeue` work inside the container,
and it provides two helpers:

- `$CLUSTER_RUNS` — the session's cluster scratch, mounted at the same path inside the container as on
  the host. Compute nodes must see it too, so it has to be on shared storage: by default it is inside
  the session (fine when the repository is on shared storage); otherwise set `CLUSTER_RUNS_BASE`.
- `$CLUSTER_EXEC` — a wrapper, kept in that scratch, that runs a job's command inside the same image on
  the compute node, with the node's GPU available. It calls the host's `apptainer` and the image by
  absolute path, so compute nodes must reach both at the same paths: if the repository is not on
  shared storage, put the image there too and point `APPTAINER_IMAGE` at it.

MadGraph event generation is CPU-only; SFitter fits want a GPU. Describe your cluster for the agents
in `internals/cluster_info.md` (git-ignored, mounted at `/internals` when present): partitions and their
CPU / RAM / GPU limits, walltimes, and any etiquette. Without it the agents probe `sinfo` themselves and
say so.

The image's SLURM clients are version 24.11 (Debian trixie). A SLURM controller accepts clients only from
its own and a few earlier releases, so on a cluster running an older SLURM, submissions from inside the
container fail; build the image on a base whose `slurm-client` matches your controller.

---

## Configuration

`config.env` (repository root, git-ignored) is read by the launcher and the image build; start from
`config.env.example`. Relative paths resolve against the repository root. For the launcher the
precedence is **caller env > `config.env` > defaults**, so any value can be overridden for one launch:
`APPTAINER_IMAGE=/shared/sfitteragents.sif ./sfitteragents.sh`. The image build sources `config.env`
over the caller's environment, so there its values win (use `--sandbox-only` on the command line).

- `APPTAINER_DIR` — directory containing the `apptainer` binary (empty: `PATH`).
- `CLAUDE_CONFIG_DIR` — the Claude Code config directory mounted into the container: it holds the login
  and the conversation transcripts. Empty (recommended): `claude_config/` in this repository, where you
  log in once. Pointing it at your own `~/.claude` reuses that login, but also brings your personal
  settings, hooks and agents into the sessions, and lets the agents modify them.
- `APPTAINER_IMAGE` — the image to run (empty: `image/sfitteragents_sandbox/` if built, else
  `image/sfitteragents.sif`).
- `APPTAINER_OVERLAY`, `OVERLAY_BASE` — the writable overlay. By default each launch gets a fresh
  directory overlay in `OVERLAY_BASE` (default: the system temp dir, e.g. `/tmp`), private to you and
  removed on exit; it must be on a local filesystem that supports overlayfs.
- `BIND_SLURM` — empty or `auto` binds SLURM when the host is a submit host; `0` never; `1` requires it.
- `CLUSTER_RUNS_BASE` — where cluster scratch lives, if not inside the session.
- `SFITTER_SRC`, `IMAGE_SANDBOX_ONLY` — image build options, see below.

No API keys: Claude Code authenticates itself through that directory, and the launcher strips
`*_API_KEY` / `*_AUTH_TOKEN` variables and `CLAUDE_CODE_OAUTH_TOKEN` from the container environment.

---

## Build the image

```bash
./image/create_image.sh                  # image/sfitteragents.sif + image/sfitteragents_sandbox/
./image/create_image.sh --sandbox-only   # only the sandbox directory
```

The image is Debian trixie with MadGraph 3.7.0 (FastJet, LHAPDF6, Pythia8, ninja, collier), the
SMEFTatNLO model, SFitter from `sfitter/` (or `SFITTER_SRC`), CUDA PyTorch, and the SLURM clients.
The launcher prefers the **sandbox directory**: on a host without `squashfuse`, apptainer cannot mount a
`.sif` and would extract the whole image (~8 GB) on every launch. The `.sif` is the portable artifact
to share.

The build is **unprivileged** — `apptainer build --fakeroot`, no sudo and no `/etc/subuid` mapping
needed. Without a subuid mapping apptainer runs the build in a root-mapped namespace under its bundled
`faked`, which needs glibc ≥ 2.38; the trixie base provides it. If your site disallows fakeroot, build
the `.sif` elsewhere and point `APPTAINER_IMAGE` at it.

A shared image bundles third-party software under its own licenses; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## Install Apptainer

Apptainer can usually be installed and run **without sudo**, which matters on HPC clusters:

- [Installation guide](https://apptainer.org/docs/admin/main/installation.html)
- [Unprivileged install from pre-built binaries](https://apptainer.org/docs/admin/main/installation.html#install-unprivileged-from-pre-built-binaries)
- Windows / macOS need a Linux VM (WSL2 on Windows, Lima on macOS).

If installation is not possible in your environment, ask your cluster administrator.

---

## Stop / cleanup

A launch stops its container instance on exit. For a wedged launch or a dead terminal:

```bash
./cleanup_sfitteragents.sh          # lists running sessions and asks which to stop
./cleanup_sfitteragents.sh --all
```

It stops instances only; sessions are removed from the `./sfitteragents.sh` menu.

---

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `apptainer not found` | Install Apptainer, or set `APPTAINER_DIR` in `config.env`. |
| `Container image not found` | Build it: `./image/create_image.sh`, or set `APPTAINER_IMAGE`. |
| `this session is already running` | One launch per session. Continue it later, or fork it into a new session. |
| The instance fails to start with an overlay error | `OVERLAY_BASE` is on a network filesystem; point it at local disk (e.g. `/tmp` or `/dev/shm`). |
| `sbatch` in the session cannot reach the controller | The launch host is not a SLURM submit host, or `BIND_SLURM=0`. `BIND_SLURM=1` turns a missing SLURM into a launch error. |
| `sbatch` in the session reports a protocol or version error | The cluster's SLURM is older than the image's 24.11 clients; see [Cluster submission](#cluster-submission). |
| Cluster jobs fail with "No such file or directory" | Compute nodes cannot see the image, the `apptainer` binary or the cluster scratch at the paths the launch host uses; see [Cluster submission](#cluster-submission). |
| The session asks you to log in | The mounted Claude config has no login yet. Log in once; it is kept in `claude_config/` (or in `CLAUDE_CONFIG_DIR`). |
| The build fails | It uses `apptainer build --fakeroot`; if your site disallows fakeroot, build elsewhere and share the `.sif`. |

---

## Citation

If you use SFitterAgents in your research, please cite:

```bibtex
@article{Diefenbacher:2026azr,
    author = "Diefenbacher, Sascha and Plehn, Tilman and Schiller, Daniel and Schmal, Nikita",
    title = "{Agentic Re-Casting using Agentic Re-Simulations}",
    eprint = "2607.22813",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    month = "7",
    year = "2026"
}
```

SFitterAgents is built on MadAgents:

```bibtex
@article{Plehn:2026gxv,
    author = "Plehn, Tilman and Schiller, Daniel and Schmal, Nikita",
    title = "{MadAgents}",
    eprint = "2601.21015",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    month = "1",
    year = "2026"
}
```

Please also cite the SFitter implementation shipped here, and the SMEFT@NLO model and MadGraph5_aMC@NLO
that produce the predictions:

```bibtex
@article{Heimel:2024drk,
    author = "Heimel, Theo and Plehn, Tilman and Schmal, Nikita",
    title = "{Profile Likelihoods on ML-Steroids}",
    eprint = "2411.00942",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    month = "11",
    year = "2024"
}

@article{Degrande:2020evl,
    author = "Degrande, C{\'e}line and Durieux, Gauthier and Maltoni, Fabio and Mimasu, Ken and Vryonidou, Eleni and Zhang, Cen",
    title = "{Automated one-loop computations in the standard model effective field theory}",
    eprint = "2008.11743",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    reportNumber = "CERN-TH-2020-140, CP3-20-42",
    doi = "10.1103/PhysRevD.103.096024",
    journal = "Phys. Rev. D",
    volume = "103",
    number = "9",
    pages = "096024",
    year = "2021"
}

@article{Alwall:2014hca,
    author = "Alwall, J. and Frederix, R. and Frixione, S. and Hirschi, V. and Maltoni, F. and Mattelaer, O. and Shao, H. -S. and Stelzer, T. and Torrielli, P. and Zaro, M.",
    title = "{The automated computation of tree-level and next-to-leading order differential cross sections, and their matching to parton shower simulations}",
    eprint = "1405.0301",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    reportNumber = "CERN-PH-TH-2014-064, CP3-14-18, LPN14-066, MCNET-14-09, ZU-TH-14-14",
    doi = "10.1007/JHEP07(2014)079",
    journal = "JHEP",
    volume = "07",
    pages = "079",
    year = "2014"
}
```

For the SFitter framework, see [arXiv:0709.3985](https://arxiv.org/abs/0709.3985),
[arXiv:2208.08454](https://arxiv.org/abs/2208.08454) and [arXiv:2312.12502](https://arxiv.org/abs/2312.12502).

---

## License

MIT, see [`LICENSE`](LICENSE). Third-party components — code adapted from nflows, the SMEFT@NLO model,
and the software the image build installs — are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
