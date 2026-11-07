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

## Verified on 2026-11-07

**Fresh clone** of `release/deploy` from GitHub into an empty folder, on the development machine
(Apple M1, 8 GB):
- `uv sync`, then the pinned GNIS snapshot fetched from the project's data release, with both
  checksums matching.
- `gazetteer build`, and `extents check`: 67 reviewed, 48 pending, 0 problems.
- Audit sample imported with rules: 36 need information, 11 ready, 3 unsupported, as in the
  README.
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

**Not verified:** a deployment on a Linux host. CI builds the image on Linux on every push, and
runs the pinned llama-server image with a tiny test model (see the README's testing section).
