"""/readyz and /api/version: every pinned version, 503 with reasons until ready; the container
bind exception; the watching worker stops on SIGTERM. SYNTHETIC store."""

import json
import os
import signal
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from localitylens.release import load_release
from localitylens.review.store import ReviewStore
from localitylens.web import app as web_app
from localitylens.web.app import ReviewConfig, create_app, serve

RELEASE = Path("release/manifest.json")


def _client(db: Path, release: Path = RELEASE) -> TestClient:
    return TestClient(create_app(ReviewConfig(db=db, release=release)))


def test_ready_reports_every_pinned_version(tmp_path: Path) -> None:
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    r = _client(db).get("/readyz")
    assert r.status_code == 200
    body = r.json()
    assert body["ready"] is True
    assert body["problems"] == []
    pinned = load_release(RELEASE)
    rel = body["release"]
    assert rel["model"]["gguf_sha256"] == pinned.model.gguf_sha256
    assert rel["model"]["upstream_revision"] == pinned.model.upstream_revision
    assert rel["llama_cpp"]["build"] == pinned.server.llama_cpp_build
    assert rel["prompt"]["version"] == pinned.prompt.version
    assert rel["gazetteer_snapshot"] == pinned.gazetteer_snapshot
    assert rel["uncertainty_policy"] == pinned.uncertainty_policy
    for key in ("store_schema", "jobs", "telemetry", "api"):
        assert body[key]


def test_not_ready_without_a_store_and_the_app_still_starts(tmp_path: Path) -> None:
    db = tmp_path / "missing.sqlite"
    r = _client(db).get("/readyz")
    assert r.status_code == 503
    assert any("does not exist" in p for p in r.json()["problems"])
    assert not db.exists()  # the probe never creates a store
    assert _client(db).get("/api/version").status_code == 200


def test_a_manifest_that_disagrees_with_the_code_is_not_ready(tmp_path: Path) -> None:
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    data["rules_version"] = "rules-0"
    stale = tmp_path / "manifest.json"
    stale.write_text(json.dumps(data), encoding="utf-8")
    r = _client(db, stale).get("/readyz")
    assert r.status_code == 503
    assert any("rules_version" in p for p in r.json()["problems"])
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert _client(db, broken).get("/readyz").status_code == 503
    assert _client(db, tmp_path / "absent.json").get("/readyz").status_code == 503


def test_an_unknown_selection_check_in_the_manifest_is_not_ready(tmp_path: Path) -> None:
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    assert data["selection_version"] == "selection-2"
    data["selection_version"] = "selection-9"
    stale = tmp_path / "manifest.json"
    stale.write_text(json.dumps(data), encoding="utf-8")
    r = _client(db, stale).get("/readyz")
    assert r.status_code == 503
    assert any("selection_version" in p for p in r.json()["problems"])
    assert _client(db).get("/api/version").json()["release"]["selection_version"] == "selection-2"


def test_the_container_may_bind_all_interfaces_and_nothing_else_may(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import uvicorn

    started: list[str] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, host, port, log_level: started.append(host))
    config = ReviewConfig(db=tmp_path / "r.sqlite")
    monkeypatch.delenv(web_app.CONTAINER_ENV, raising=False)
    with pytest.raises(ValueError, match="local only"):
        serve(config, host="0.0.0.0")
    monkeypatch.setenv(web_app.CONTAINER_ENV, "1")
    serve(config, host="0.0.0.0")
    with pytest.raises(ValueError, match="local only"):
        serve(config, host="192.168.1.20")  # even in the container, only 0.0.0.0
    serve(config, host="127.0.0.1")
    assert started == ["0.0.0.0", "127.0.0.1"]


def test_the_watching_worker_stops_on_sigterm(
    tmp_path: Path, gnis_snapshot: tuple[Path, object]
) -> None:
    from localitylens.cli import main
    from localitylens.data.manifest import write_manifest
    from localitylens.gazetteer.index import build_index

    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)  # type: ignore[arg-type]
    index = tmp_path / "g.sqlite"
    build_index(directory, manifest, index)  # type: ignore[arg-type]
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    timer = threading.Timer(0.5, lambda: os.kill(os.getpid(), signal.SIGTERM))
    timer.start()
    old_term, old_int = signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGINT)
    try:
        code = main(["review", "work", "--db", str(db), "--index", str(index), "--watch",
                     "--poll", "0.2"])  # fmt: skip
    finally:
        timer.cancel()
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)
    assert code == 0
