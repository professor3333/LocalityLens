# Deployment, backup and rollback

LocalityLens runs on one machine: the review screen and JSON API, one worker, an optional
llama-server, and SQLite. Everything listens on 127.0.0.1. This page covers installing it,
what to back up, how to upgrade, and how to roll back. Every command below was run on
2026-11-07, as recorded at the end.

## What a deployment is made of

| Part | Where | How to get it back |
|---|---|---|
| Code, release manifest, prompts, policies, reviewed extents, samples | git (a commit or tag) | `git checkout <release>` |
| Python environment | `uv.lock` | `uv sync` |
| Model file (only for `llm` and `hybrid`) | `models/`, pinned by SHA-256 in the manifest | `localitylens model fetch` (verifies the hash) |
| GNIS snapshot and gazetteer index | `data/raw/gnis/`, `data/derived/` | `localitylens data fetch-gnis` (the manifest's pinned snapshot), then `gazetteer build` |
| **Review store**: records, proposals, curator decisions, jobs, traces | `data/review/review.sqlite` | **only from a backup** |
| Exports | `data/review/export/` | `localitylens review export` from the store |

The review store is the only state that cannot be rebuilt, so it is the only thing that needs
a backup. Each proposal in it records the release, extractor and snapshot that produced it,
so decisions keep their versions after an upgrade or a rollback.

## Install

Native (Python 3.12+ and [uv](https://github.com/astral-sh/uv)):

```bash
git clone https://github.com/professor3333/LocalityLens.git && cd LocalityLens
uv sync
uv run localitylens data fetch-gnis        # the pinned snapshot, checksummed
uv run localitylens gazetteer build
uv run localitylens extents check          # 67 reviewed, 48 pending, 0 problems
uv run localitylens review import --sample eval/audit/audit-50.json --system rules \
    --extents data/reviewed/extents.csv
uv run localitylens review serve --extents data/reviewed/extents.csv   # http://127.0.0.1:8000/
```

For `--system llm` or `hybrid`, also install llama.cpp, run `localitylens model fetch`, and
start llama-server as shown in the README. Docker Compose is described in the README
("Run it with Docker Compose"): the same commands run inside the `review` service.

**Check a deployment** with `/readyz`. It answers 200 only when the store opens and
`release/manifest.json` matches the code. It reports every pinned version: model and revision,
GGUF SHA-256, llama.cpp build, prompt, schema and policy versions, snapshots, store schema and
API version.

## Back up

```bash
uv run localitylens review backup --out data/backups/review-$(date -u +%Y%m%dT%H%M%SZ).sqlite
# Docker Compose:
docker compose run --rm review review backup --db /app/data/review/review.sqlite \
    --out /app/data/backups/review-<time>.sqlite
```

- **It is safe while the screen and worker are running.** SQLite's online backup copies a
  consistent snapshot without blocking writers; a write still in progress is not in the copy.
- **The copy is one file,** checked with `PRAGMA integrity_check`. The command prints its
  schema and its record, proposal and decision counts. It never overwrites a file.
- **Take one before every upgrade,** and keep it with the release it belongs to. `data/` is
  gitignored, so backups are never committed; copy them off the machine yourself.

## Upgrade

1. `review backup` (above). Note the file: it is the rollback point.
2. Stop the review screen and the worker (`docker compose stop`).
3. `git fetch && git checkout <new release>`, then `uv sync`.
4. If the new manifest pins a different model or GNIS snapshot: `model fetch`, `data fetch-gnis`,
   `gazetteer build`.
5. Start again and check `/readyz`: `ready` true, and the versions you expect.

Opening the store with newer code may upgrade its schema (for example `review-2` to
`review-3`). Older code refuses a newer schema, which is why rollback restores the backup
from step 1 instead of reusing the upgraded store.

## Roll back

1. Stop the review screen and the worker.
2. Restore the backup taken before the upgrade:
   ```bash
   uv run localitylens review restore --from data/backups/<before-upgrade>.sqlite --replace
   ```
   - The current store is moved aside to `review.sqlite.before-restore-<UTC time>`, never
     deleted.
   - The restore refuses a damaged file, a file that is not a review store, a store schema this
     release cannot read, and a store another process is writing to.
   - Decisions made after the backup are not in the restored store. They are still in the
     moved-aside file.
3. `git checkout <previous release>`, `uv sync`, and the model and GNIS steps if the previous
   manifest pins different ones.
4. Start and check `/readyz`: the previous release's versions, `ready` true.

## Releasing

A version tag (`git tag -a vX.Y.Z` on `main`, then `git push origin vX.Y.Z`) starts
[`.github/workflows/release.yml`](../.github/workflows/release.yml):
1. **Evaluate:** 12 jobs, six dev and validation samples × two quants. Each job fetches the
   pinned GNIS snapshot and the pinned model (SHA-256 checked), and starts the pinned llama.cpp
   image (`model check` must pass). It then reruns the systems from scratch: rules, the LLM,
   hybrid-1 and the scores, with and without selection-2. The Q8_0 reference quant runs the LLM
   alone. No held-out test is touched.
2. **Check:** the gates in [`release/regression.json`](../release/regression.json), with the
   evidence as an artifact and a summary on the run page.
3. **Deploy check:** the Compose stack (with llama-server) starts on the Linux runner, and
   `scripts/deploy_verify.py` takes `deploy/sample.csv` from import to export, then checks the
   saved decision after a restart (below).
4. **Image:** only if every gate and the deploy check pass, the image is built and pushed to
   `ghcr.io/professor3333/localitylens:<tag>`, and its digest is kept as an artifact.

The digest can't go into the tagged manifest, because the tag fixes that file before the image
exists. Copy it into the GitHub release notes instead. A manual run (`workflow_dispatch`)
evaluates without pushing (`-f evaluate=false` runs only the deploy check). The first
evaluation took 48 minutes, and the deploy check takes about 3 minutes.

**Known red gate:** quantization parity fails for Q4_K_M (2.3 points against a 1-point limit;
[parity](../eval/reports/quantization-parity.md)). The owner kept the quant, so the check stays
red, and no image is pushed, until the quant or the spec changes.

## Verified on 2026-11-10 (v0.1.2)

- **What changed:** v0.1.2 changes no store schema (still `review-3`). Proposals already in a
  store keep the release they were made with. New `review import` and `review work` runs apply
  the manifest's `selection-2` check.
- **Compose on a scratch clone of the release branch:** `/readyz` ready, release 0.1.2,
  `selection_version` selection-2, no problems.
- **The worker:** it processed the audit sample with rules (38 need information, 9 ready, 3
  unsupported, as on the host) and stopped cleanly on SIGTERM.

## Verified on 2026-11-07

**Fresh clone** of `release/deploy` from GitHub into an empty folder, on the development machine
(Apple M1, 8 GB):
- `uv sync`, then the pinned GNIS snapshot fetched from the project's data release, with both
  checksums matching.
- `gazetteer build`, and `extents check`: 67 reviewed, 48 pending, 0 problems.
- Audit sample imported with rules: 36 need information, 11 ready, 3 unsupported, as in the
  README at the time (v0.1.1, before the default selection check).
- One record approved, then `review export`: 1 approved row in the CSV and the GeoJSON, 39
  unresolved.
- `review backup`: 50 records, 50 proposals, 1 decision, integrity ok.

**Rollback rehearsal** on that clone:
- After the backup, one more decision (a reject) stood for work done after an upgrade.
- `review restore` without `--replace` was refused. With it, the store was moved aside and the
  backup restored: 1 decision, and the later reject is gone (0 rejected records).
- The previous release was checked out (`4861442`) and `uv sync` run. Its `review serve`
  answered `/readyz` ready, store schema `review-3`, release `0.1.0-dev`, `rules-6`,
  `gnis-co-2026-09-29`. The approved record's page loaded.

**Docker Compose** on the same clone:
- `docker compose build` and `up -d`, with the review screen on port 8766.
- `review backup` inside the `review` service while both services were up: integrity ok.
- `docker compose stop`, then `review restore --replace` in the container, then `up -d`:
  `/readyz` ready, `review-3`.
- During that backup the worker had no jobs. Copying during an in-progress write is covered by
  a unit test.

**Rollback across a store-schema change**, on the same clone, with v0.1.0's `review backup` and
`review restore`:
- An older release (`2e03e8c`, store schema `review-2`) imported the audit sample (36 / 11 / 3)
  and approved one record.
- `review backup` copied that store without changing it: schema `review-2`, 1 decision.
- v0.1.0 opened the store, which upgraded it to `review-3`, and recorded a second decision.
- The older release then refused the upgraded store: `store schema review-3, expected review-2`.
- `review restore --replace` brought back the `review-2` backup. The older release opened it
  again: the approved record is there, and the later decision is not.

**The `llm` Compose profile** on the same machine (Docker Desktop, a 4 GB Linux VM, CPU only):
- llama-server loaded the pinned model in about a minute, at 2.8 GB of the VM's 3.9 GB. `model
  check` passed from the worker.
- One hybrid record took 540 s: prompt 37 tokens/s, generation 0.23 tokens/s, against p50 9.9 s
  for native llama-server with Metal on the same machine.
- That is longer than the worker's 300 s job lease, so the job was leased again. **On a machine
  like this one, run llama-server natively** and point the worker at it. On a larger Linux
  host, raise the lease with `LOCALITYLENS_LEASE` (seconds) if a call can take longer than 300 s.

**On a Linux host** (verified 2026-11-12 by the release workflow's deploy check, run
[43232254377](https://github.com/professor3333/LocalityLens/actions/runs/43232254377)):
- **Host:** a GitHub-hosted runner, AMD EPYC 7763, 4 vCPU, 15 GiB RAM, Ubuntu 26.04.1, Docker
  29.4.2.
- **Stack:** the full Compose stack, `llm` profile included, built from the repository with
  the pinned GNIS snapshot and model.
- **The sample** (`deploy/sample.csv`, two audit records) went through `POST /api/imports` with
  hybrid-1. The worker processed both in 70–115 s across two runs, one of them through the
  LLM, the first after a cold start.
- **Checks:** `/readyz` ready, and every reported version matched the manifest. selection-2
  held the Paonia region. The approval was stored, and its retry returned the same decision.
  The export held it.
- **After a restart** of the review service and the worker, the decision and the export were
  still there.
- **Model speed on this CPU** (release-workflow evaluation, native llama.cpp image, two runs):
  - **Q4_K_M:** p50 23.8–28.6 s and p95 41.2–44.6 s per LLM call.
  - **Memory:** not reliably measured. `docker stats` doesn't consistently count the
    memory-mapped model file: the two runs reported 2.2 and 3.2 GiB for Q4_K_M, and 5.4 and
    0.9 GiB for Q8_0, whose file alone is 4.5 GB.
  - **Model file:** 2.74 GB, and on the M1 llama-server adds 629 MB on top of it.

The check runs again on every version tag, and an image is pushed only if it passes.
