"""Shape strata, the viewed-groups registry and stratified sampling (SYNTHETIC records)."""

import json
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row

from localitylens.evaluation.dev_sample import load_registry, register, sample_strata, text_shape
from localitylens.ingest.specimens import text_key, to_record


@pytest.mark.parametrize(
    ("text", "shape"),
    [("Testa Peak.", "bare"), ("Pitkin.", "bare"), ("Gunnison Canon.", "bare"),
     ("2 mi NE of Testa.", "offset"), ("ca 5 air mi SSW of Testa.", "offset"),
     ("Nine miles north of Testa.", "offset"), ("½ mile S of Testa Rd.", "offset"),
     ("20-21 air mi NE of Testa.", "offset"), ("3.4 road mi on Forest 101.", "offset"),
     ("S slope of Mt. Testa, near the old road.", "other"), ("Hwy 34 at Testa Creek.", "other"),
     ("Testa Peak, elev. 9800 ft.", "offset")],
)  # fmt: skip
def test_text_shape(text: str, shape: str) -> None:
    assert text_shape(text) == shape


def test_registry_keeps_the_first_sample_for_a_group(tmp_path: Path) -> None:
    path = tmp_path / "viewed.json"
    register(path, "audit-50", ["g1", "g2"])
    register(path, "dev-1", ["g2", "g3"])
    assert load_registry(path) == {"g1": "audit-50", "g2": "audit-50", "g3": "dev-1"}
    assert json.loads(path.read_text())["counts"] == {"audit-50": 2, "dev-1": 1}


TEXTS = [
    "Alpha Peak.", "Beta Lake.", "Gamma Creek.", "Delta Hill.",
    "2 mi N of Alpha.", "3 mi S of Beta.", "4 km E of Gamma.",
    "N slope of Alpha Peak, by the old road.", "Along Beta Creek below the falls.",
]  # fmt: skip
RECORDS = [to_record(row(i, t)) for i, t in enumerate(TEXTS, start=1)]


def test_quotas_exclusion_and_determinism() -> None:
    viewed = {RECORDS[0].group_key, RECORDS[4].group_key}
    quotas = {"bare": 2, "offset": 2, "other": 1}
    items, total, groups, skipped = sample_strata(RECORDS, quotas, "s", viewed, "D")
    assert (total, groups, skipped) == (9, 9, 2)
    keys = {i.record.group_key for i in items}
    assert not keys & viewed
    shapes = [text_shape(i.record.locality) for i in items]
    assert shapes.count("bare") == 2
    assert shapes.count("offset") == 2
    assert shapes.count("other") == 1
    assert [i.audit_id for i in items] == ["D01", "D02", "D03", "D04", "D05"]
    again = sample_strata(list(reversed(RECORDS)), quotas, "s", viewed, "D")[0]
    assert [i.record.gbif_id for i in again] == [i.record.gbif_id for i in items]


def test_a_quota_larger_than_the_pool_is_refused() -> None:
    with pytest.raises(ValueError, match="offset"):
        sample_strata(RECORDS, {"offset": 4}, "s", {RECORDS[4].group_key}, "D")


@pytest.mark.parametrize(
    ("text", "shape"),
    [("Testa Mesa, 15 mi. east of Osgood.", "place_offset"),
     ("S. slope of Testa Mt., 16 miles N of Osgood.", "place_offset"),
     ("Testa Ck.; ca 3 air mi SW from Osgood", "place_offset"),
     ("Colorado: Testa Co.: Fenn Creek, ca. 2 mi NE of Osgood", "place_offset"),
     ("Testa Gulch, 9 km W of Osgood", "place_offset"),
     ("2 mi NE of Testa.", "offset"),
     ("Testa Peak, elev. 9800 ft.", "offset"),
     ("Testa Peak, 9800 ft.", "offset"),
     ("Hwy 12, 3 mi N of Osgood", "offset"),  # the clause before holds a digit
     ("3 mi N of Osgood, Testa Mesa", "offset"),  # the place comes after
     ("Testa Peak.", "bare"), ("Hwy 34 at Testa Creek.", "other")],
)  # fmt: skip
def test_shape_version_2_carves_place_offset_out_of_offset(text: str, shape: str) -> None:
    assert text_shape(text, "2") == shape
    assert text_shape(text) == ("offset" if shape == "place_offset" else shape)


def test_an_unknown_version_is_refused() -> None:
    with pytest.raises(ValueError, match="shape version"):
        text_shape("Testa Peak.", "3")
    with pytest.raises(ValueError, match="exclusion version"):
        sample_strata(RECORDS, {"bare": 1}, "s", set(), "D", exclusion_version="3")


def test_exclusion_version_2_also_drops_repeated_wording_under_another_county() -> None:
    viewed = to_record(row(1, "Testa Pass.", county="Marlow"))
    repeat = to_record(row(2, "Testa  pass", county=""))  # same name key, other county
    other = to_record(row(3, "Fenn Pass."))
    assert viewed.group_key != repeat.group_key
    assert text_key(viewed.locality) == text_key(repeat.locality)
    records = [viewed, repeat, other]
    v1 = sample_strata(records, {"bare": 2}, "s", {viewed.group_key}, "E")
    assert {i.record.gbif_id for i in v1[0]} == {"2", "3"}
    assert v1[3] == 1
    v2 = sample_strata(records, {"bare": 1}, "s", {viewed.group_key}, "E", exclusion_version="2")
    assert [i.record.gbif_id for i in v2[0]] == ["3"]
    assert v2[3] == 2
    with pytest.raises(ValueError, match="only 1"):
        sample_strata(records, {"bare": 2}, "s", {viewed.group_key}, "E", exclusion_version="2")
