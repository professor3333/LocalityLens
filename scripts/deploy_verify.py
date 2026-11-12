"""Deploy verification against a running stack (the CI/CD spec's deploy check).

    uv run python scripts/deploy_verify.py import  --url http://127.0.0.1:8000 --out evidence.json
    (restart the review service and the worker)
    uv run python scripts/deploy_verify.py restart --url http://127.0.0.1:8000 --out evidence.json

`import` uploads deploy/sample.csv through POST /api/imports (hybrid), waits for the worker,
checks /readyz and the reported versions against release/manifest.json, approves one record
(and retries the same decision, which must not duplicate it), and exports. `restart` checks
that the saved decision and the export survive a restart. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

SAMPLE = Path("deploy/sample.csv")
APPROVE = "gbif:2573441754"  # rules path; held by selection-2, approval answers the question
LLM_RECORD = "gbif:2573332102"  # the rules reach no candidate: hybrid-1 calls the model
KEY = "deploy-verify-1"


def _call(url: str, method: str = "GET", body: bytes | None = None,
          headers: dict[str, str] | None = None) -> tuple[int, Any]:  # fmt: skip
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        raw, status = e.read(), e.code
    except OSError as e:  # not listening yet, or reset while the service starts
        return 0, f"{type(e).__name__}: {e}"
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw.decode("utf-8", "replace")


def _json(url: str, payload: dict[str, Any]) -> tuple[int, Any]:
    return _call(url, "POST", json.dumps(payload).encode(),
                 {"Content-Type": "application/json"})  # fmt: skip


def _multipart(url: str, path: Path, fields: dict[str, str]) -> tuple[int, Any]:
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]  # fmt: skip
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        "Content-Type: text/csv\r\n\r\n".encode()
        + path.read_bytes()
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return _call(url, "POST", b"".join(parts),
                 {"Content-Type": f"multipart/form-data; boundary={boundary}"})  # fmt: skip


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def __call__(self, name: str, ok: bool, detail: Any = "") -> bool:
        self.items.append({"check": name, "passed": bool(ok), "detail": detail})
        print(f"  {'ok ' if ok else 'BAD'}  {name}  {detail}", flush=True)
        return ok


def _versions(c: Checks, base: str) -> None:
    manifest = json.loads(Path("release/manifest.json").read_text(encoding="utf-8"))
    status, ready = _call(f"{base}/readyz")
    c("/readyz ready", status == 200 and ready.get("ready") is True,
      ready.get("problems") if isinstance(ready, dict) else ready)  # fmt: skip
    rel = ready.get("release", {}) if isinstance(ready, dict) else {}
    want = {
        "release": manifest["release"],
        "model": manifest["model"]["id"],
        "upstream_revision": manifest["model"]["upstream_revision"],
        "gguf_sha256": manifest["model"]["gguf_sha256"],
        "llama_cpp": manifest["server"]["llama_cpp_build"],
        "prompt": manifest["prompt"]["version"],
        "selection_version": manifest["selection_version"],
        "uncertainty_policy": manifest["uncertainty_policy"],
        "gazetteer_snapshot": manifest["gazetteer_snapshot"],
    }
    got = {
        "release": rel.get("release"),
        "model": rel.get("model", {}).get("id"),
        "upstream_revision": rel.get("model", {}).get("upstream_revision"),
        "gguf_sha256": rel.get("model", {}).get("gguf_sha256"),
        "llama_cpp": rel.get("llama_cpp", {}).get("build"),
        "prompt": rel.get("prompt", {}).get("version"),
        "selection_version": rel.get("selection_version"),
        "uncertainty_policy": rel.get("uncertainty_policy"),
        "gazetteer_snapshot": rel.get("gazetteer_snapshot"),
    }
    c("reported versions match release/manifest.json", got == want,
      {k: got[k] for k in got if got[k] != want[k]} or "all match")  # fmt: skip


def run_import(base: str, timeout_s: float) -> dict[str, Any]:
    c = Checks()
    status, body = _multipart(f"{base}/api/imports", SAMPLE, {"system": "hybrid"})
    if not c("import accepted", status == 201 and body.get("accepted") == 2,
             f"HTTP {status}, accepted {body.get('accepted') if isinstance(body, dict) else body}"):  # fmt: skip
        return {"checks": c.items}
    batch = body["batch_id"]
    started = time.monotonic()
    while True:
        _, b = _call(f"{base}/api/batches/{batch}")
        if isinstance(b, dict) and b.get("open") == 0:
            break
        if time.monotonic() - started > timeout_s:
            c("worker finished the batch", False, f"timeout after {timeout_s:.0f} s: {b}")
            return {"checks": c.items}
        time.sleep(5)
    seconds = round(time.monotonic() - started, 1)
    c(
        "worker finished the batch",
        b.get("jobs", {}).get("done") == 2,
        f"{b.get('jobs')}, {seconds} s",
    )
    _versions(c, base)
    _, held = _call(f"{base}/api/records/{APPROVE}")
    _, llm = _call(f"{base}/api/records/{LLM_RECORD}")
    questions = (held.get("proposal") or {}).get("region", {}) or {}
    c("selection-2 holds the Paonia region with its question",
      held.get("record", {}).get("status") == "needs_information"
      and any("(selection-2)" in q for q in questions.get("questions", [])),
      held.get("record", {}).get("status"))  # fmt: skip
    c("hybrid-1 used the LLM for the record the rules cannot reach",
      (llm.get("proposal") or {}).get("extractor_version", "").startswith("llm-"),
      (llm.get("proposal") or {}).get("extractor_version"))  # fmt: skip
    decision = {"action": "approve", "reviewer": "deploy-check", "key": KEY,
                "rationale": "deploy verification: the offset from Paonia is the reference"}  # fmt: skip
    s1, d1 = _json(f"{base}/api/records/{APPROVE}/decisions", decision)
    s2, d2 = _json(f"{base}/api/records/{APPROVE}/decisions", decision)
    c("approve stored", s1 == 201 and d1.get("status") == "approved", f"HTTP {s1}")
    c("retried decision is not duplicated",
      s2 == 200 and d2.get("decision_id") == d1.get("decision_id"), f"HTTP {s2}")  # fmt: skip
    _, after = _call(f"{base}/api/records/{APPROVE}")
    c(
        "one decision on record",
        len(after.get("decisions", [])) == 1,
        len(after.get("decisions", [])),
    )
    se, ex = _json(f"{base}/api/exports", {})
    c("export: 1 approved, 1 unresolved",
      se == 200 and ex.get("approved") == 1 and ex.get("unresolved") == 1, ex)  # fmt: skip
    st, csv_text = _call(f"{base}/export/occurrences.csv")
    c(
        "export CSV holds the approved record",
        st == 200 and "2573441754" in str(csv_text),
        f"HTTP {st}",
    )
    return {"checks": c.items, "batch": batch, "batch_seconds": seconds,
            "decision_id": d1.get("decision_id")}  # fmt: skip


def run_restart(base: str, previous: dict[str, Any]) -> dict[str, Any]:
    c = Checks()
    for _ in range(60):
        status, _ = _call(f"{base}/readyz")
        if status == 200:
            break
        time.sleep(2)
    _versions(c, base)
    _, rec = _call(f"{base}/api/records/{APPROVE}")
    ds = rec.get("decisions", [])
    c("decision survives the restart",
      rec.get("record", {}).get("status") == "approved" and len(ds) == 1
      and ds[0]["decision_id"] == previous.get("decision_id"), len(ds))  # fmt: skip
    st, csv_text = _call(f"{base}/export/occurrences.csv")
    c("export survives the restart", st == 200 and "2573441754" in str(csv_text), f"HTTP {st}")
    return {"checks": c.items}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("phase", choices=["import", "restart"])
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=float, default=1800.0, help="seconds to wait for the worker")
    args = ap.parse_args()
    out = Path(args.out)
    evidence: dict[str, Any] = json.loads(out.read_text()) if out.is_file() else {}
    if args.phase == "import":
        evidence["import"] = run_import(args.url.rstrip("/"), args.timeout)
    else:
        evidence["restart"] = run_restart(args.url.rstrip("/"), evidence.get("import", {}))
    out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    ok = all(i["passed"] for i in evidence[args.phase]["checks"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
