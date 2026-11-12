import json
import shutil
from pathlib import Path

import pytest

from localitylens.evaluation.release_check import check, parse_memory, summary_markdown
from localitylens.release import load_release

REPORTS = Path("eval/reports")
REGRESSION = json.loads(Path("release/regression.json").read_text(encoding="utf-8"))
IDS = {
    "q4": load_release(Path("release/manifest.json")).extractor_id,
    "q8": load_release(Path("release/manifest-q8.json")).extractor_id,
}


def _runs(tmp_path: Path) -> Path:
    """A fake fresh run made of the committed reports (the Q8 run copies the Q4 one)."""
    runs = tmp_path / "runs"
    for s in REGRESSION["samples"]:
        q4, q8 = runs / f"eval-q4-{s}", runs / f"eval-q8-{s}"
        q4.mkdir(parents=True)
        q8.mkdir(parents=True)
        for suffix in ("", "-sel2"):
            name = f"{s}-score-hybrid-1-extents-derived{suffix}.json"
            shutil.copy(REPORTS / name, q4 / name)
        llm = REPORTS / f"{s}-{IDS['q4']}-extents-derived.json"
        shutil.copy(llm, q4 / llm.name)
        shutil.copy(llm, q8 / f"{s}-{IDS['q8']}-extents-derived.json")
        shutil.copy(REPORTS / f"{s}-score-hybrid-1-extents-derived.json",
                    q8 / f"{s}-score-extents-derived.json")  # fmt: skip
    return runs


def test_the_committed_reports_pass_their_own_gates(tmp_path: Path) -> None:
    evidence = check(_runs(tmp_path), REPORTS, REGRESSION, IDS)
    assert evidence["passed"], summary_markdown(evidence)
    sel = next(g for g in evidence["gates"] if g["gate"] == "selection_2")
    assert sel["held_back_wrong"] >= 2 * sel["held_back_correct"]


def test_any_rules_difference_fails_and_a_small_model_drift_does_not(tmp_path: Path) -> None:
    runs = _runs(tmp_path)
    path = runs / "eval-q4-dev-1" / "dev-1-score-hybrid-1-extents-derived.json"
    score = json.loads(path.read_text(encoding="utf-8"))
    score["all"]["systems"]["llm"]["correct_proposal_candidates"]["hits"] -= 3
    path.write_text(json.dumps(score), encoding="utf-8")
    assert check(runs, REPORTS, REGRESSION, IDS)["passed"]  # 3 is within the tolerance
    score["all"]["systems"]["llm"]["correct_proposal_candidates"]["hits"] -= 1
    score["all"]["systems"]["rules"]["critical_exact_match"]["hits"] += 1
    path.write_text(json.dumps(score), encoding="utf-8")
    evidence = check(runs, REPORTS, REGRESSION, IDS)
    failed = {g["gate"] for g in evidence["gates"] if not g["passed"]}
    assert failed == {"rules_exact", "model_systems"}


def test_a_missing_report_is_an_error_not_a_pass(tmp_path: Path) -> None:
    runs = _runs(tmp_path)
    (runs / "eval-q8-dev-4" / "dev-4-score-extents-derived.json").unlink()
    with pytest.raises(FileNotFoundError, match="dev-4"):
        check(runs, REPORTS, REGRESSION, IDS)


def test_peak_memory_from_docker_stats_lines() -> None:
    text = "512MiB / 15.6GiB\n2.95GiB / 15.6GiB\n\n1.2GiB / 15.6GiB\n"
    assert parse_memory(text) == int(2.95 * 2**30)
    assert parse_memory("") is None


def test_the_reference_quant_differs_from_the_release_only_in_the_model_file() -> None:
    main = json.loads(Path("release/manifest.json").read_text(encoding="utf-8"))
    ref = json.loads(Path("release/manifest-q8.json").read_text(encoding="utf-8"))
    assert ref["release"] == main["release"] + "-ref-q8"
    for key in ("gguf_file", "quantization", "gguf_sha256", "gguf_size_bytes"):
        assert ref["model"].pop(key) != main["model"].pop(key)
    assert ref.pop("extractor_id") != main.pop("extractor_id")
    ref.pop("release")
    main.pop("release")
    assert ref == main  # same upstream and GGUF revisions, prompt, settings, rules, snapshots
