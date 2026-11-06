"""GEOLocate comparison on read samples (never the locked test). Plan: eval/reports/geolocate-plan.md.

    uv run python scripts/geolocate_compare.py query            # sends label text to GEOLocate
    uv run python scripts/geolocate_compare.py score eval/reports/geolocate-comparison.json

``query`` sends each record's original locality text, with country, state and the supplied county,
to the GEOLocate web service (glcwrap) one request at a time, and caches the raw responses in
eval/.cache/geolocate/ (not committed). ``score`` needs no network: it compares GEOLocate's top
result and our systems' points against the position each annotation defends.

* **Defensible position:** for every acceptable GNIS ID of an answerable record, the feature's
  GNIS primary point; for an annotated distance with unit and direction, the geodesic offset
  from it (nominal bearing). Other relations have no defensible point and are counted, not scored.
* **A system's point:** GEOLocate's highest-scoring result; for our systems, the top candidate's
  GNIS point, offset by the system's own reading when it has a distance, unit and direction.
* **Distances** are geodesics on GRS80. GEOLocate reports WGS84 and GNIS NAD83; the two differ by
  about 1-2 m in Colorado, far below the 1 km and 5 km thresholds, and are not transformed.
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Final

from pyproj import Geod

from localitylens.evaluation.annotations import Annotation, annotated_distance, check_worksheet
from localitylens.evaluation.audit import load_sample
from localitylens.evaluation.score import _category
from localitylens.gazetteer.index import Gazetteer
from localitylens.geo.directions import CompassPoint, nominal_bearing
from localitylens.geo.units import METRES_PER_UNIT, LengthUnit

ENDPOINT: Final = "https://www.geo-locate.org/webservices/geolocatesvcv2/glcwrap.aspx"
SETTINGS: Final = {"enableH2O": "false", "hwyX": "false", "doUncert": "true", "doPoly": "false",
                   "displacePoly": "false", "languageKey": "0", "fmt": "geojson"}  # fmt: skip
COMPARE_VERSION: Final = "geolocate-compare-1"
CACHE: Final = Path("eval/.cache/geolocate")
THRESHOLDS_M: Final = (1000.0, 5000.0)
SAMPLES: Final = {
    "audit-50": ("eval/audit/audit-50.json", "eval/audit/worksheet.csv", "owner"),
    "dev-1": ("eval/dev/dev-1/dev-1.json", "eval/dev/dev-1/worksheet.csv", "owner"),
    "validation": ("eval/benchmark/validation/validation.json",
                   "eval/benchmark/validation/worksheet.csv", "owner"),
    "dev-2": ("eval/dev/dev-2/dev-2.json", "eval/dev/dev-2/worksheet.csv", "Claude"),
    "dev-3": ("eval/dev/dev-3/dev-3.json", "eval/dev/dev-3/worksheet.csv", "Claude"),
    "dev-4": ("eval/dev/dev-4/dev-4.json", "eval/dev/dev-4/worksheet.csv", "Claude"),
}  # fmt: skip
OURS: Final = {"rules": "rules-6", "llm": "llm-x2g2-qwen3.5-4b-q4km", "hybrid": "hybrid-1"}
GRS80: Final = Geod(ellps="GRS80")


def _county(supplied: str) -> str:
    """The supplied county, or "" when it says nothing usable (as COUNTY_CONTEXT_VERSION 1)."""
    c = supplied.strip()
    if not c or c.casefold().startswith("unknown") or "/" in c or " or " in c.casefold():
        return ""
    return c


def _params(locality: str, county: str) -> dict[str, str]:
    p = {"country": "USA", "state": "Colorado", "locality": locality, **SETTINGS}
    if c := _county(county):
        p["county"] = c
    return p


def _key(params: dict[str, str]) -> str:
    body = json.dumps({"v": COMPARE_VERSION, "endpoint": ENDPOINT, **params}, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def query(pause_s: float = 1.0) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, (sample_path, _, _) in SAMPLES.items():
        items = load_sample(Path(sample_path)).items
        sent = cached = failed = 0
        for item in items:
            params = _params(item.record.locality, item.record.county)
            path = CACHE / f"{_key(params)}.json"
            if path.exists():
                cached += 1
                continue
            url = ENDPOINT + "?" + urllib.parse.urlencode(params)
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(url, timeout=90) as resp:  # fixed host
                        body = resp.read()
                    if not body.strip():  # HTTP 200, empty body: GEOLocate found nothing
                        body = json.dumps({"type": "FeatureCollection", "features": [],
                                           "empty_body": True}).encode()  # fmt: skip
                    json.loads(body)  # must parse; stored only as data
                    path.write_bytes(body)
                    sent += 1
                    break
                except (OSError, ValueError):
                    time.sleep(5 * 2**attempt)
            else:
                failed += 1
            time.sleep(pause_s)
        print(f"{name}: {len(items)} records, {sent} sent, {cached} cached, {failed} failed")


def _point(lat: float, lon: float) -> tuple[float, float]:
    return float(lat), float(lon)


def _offset(origin: tuple[float, float], direction: CompassPoint | None,
            unit: LengthUnit | None, value: float | None) -> tuple[float, float] | None:  # fmt: skip
    if direction is None or unit is None or value is None:
        return None
    lon, lat, _ = GRS80.fwd(origin[1], origin[0], nominal_bearing(direction),
                            value * METRES_PER_UNIT[unit])  # fmt: skip
    return float(lat), float(lon)


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return float(GRS80.inv(a[1], a[0], b[1], b[0])[2])


def _positions(a: Annotation, gaz: Gazetteer) -> list[tuple[float, float]] | None:
    """Defensible positions, or None when the annotation defends no point."""
    out = []
    offset = a.relation.value == "distance_and_direction"
    if a.relation.value not in ("named_feature", "distance_and_direction"):
        return None
    for fid in sorted(a.acceptable_ids):
        f = gaz.feature(fid)
        if f is None:
            continue
        p = _point(f.primary_point.latitude, f.primary_point.longitude)
        if offset:
            q = _offset(p, a.direction, a.unit, annotated_distance(a.distance))
            if q is None:
                return None
            p = q
        out.append(p)
    return out or None


def _geolocate_top(body: dict[str, Any]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_score = float("-inf")
    for feat in body.get("features") or []:
        try:
            lon, lat = feat["geometry"]["coordinates"][:2]
            props = feat.get("properties") or {}
            score = float(props.get("score") or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if score > best_score:
            best_score = score
            radius = props.get("uncertaintyRadiusMeters")
            best = {"point": _point(lat, lon), "score": score,
                    "radius_m": float(radius) if isinstance(radius, (int, float)) else None,
                    "precision": props.get("precision"),
                    "parse_pattern": props.get("parsePattern")}  # fmt: skip
    return best


def _our_point(r: dict[str, Any], gaz: Gazetteer) -> tuple[float, float] | None:
    top = r.get("top_candidate")
    interp = r.get("interpretation")
    if not top or not interp:
        return None
    f = gaz.feature(int(top["feature_id"]))
    if f is None:
        return None
    p = _point(f.primary_point.latitude, f.primary_point.longitude)
    rel = interp.get("relation")
    if rel == "named_feature":
        return p
    if rel == "distance_and_direction":
        d, u, h = interp.get("distance"), interp.get("unit"), interp.get("direction")
        if d is None or u is None or h is None:
            return None
        return _offset(p, CompassPoint(h), LengthUnit(u), float(d))
    return None


def _summary(errors: list[float | None], n: int) -> dict[str, Any]:
    have = [e for e in errors if e is not None]
    out: dict[str, Any] = {"records": n, "with_point": len(have)}
    for t in THRESHOLDS_M:
        out[f"within_{int(t)}_m"] = sum(1 for e in have if e <= t)
    out["median_error_m"] = round(statistics.median(have)) if have else None
    return out


def score(out_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"version": COMPARE_VERSION, "endpoint": ENDPOINT,
                              "settings": SETTINGS, "ours": OURS, "samples": {}, "pooled": {},
                              "records": []}  # fmt: skip
    pooled: dict[str, dict[str, list[Any]]] = {}
    with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
        for name, (sample_path, worksheet, annotator) in SAMPLES.items():
            sample = load_sample(Path(sample_path))
            by_id = {i.audit_id: i for i in sample.items}
            ann = check_worksheet(Path(worksheet), sample, gaz).annotations
            reports = {
                k: {r["audit_id"]: r for r in json.loads(
                    Path(f"eval/reports/{name}-{v}.json").read_text(encoding="utf-8"))["records"]}
                for k, v in OURS.items()
            }  # fmt: skip
            answerable = [a for a in ann if _category(a) == "answerable"]
            errs: dict[str, list[Any]] = {k: [] for k in ("geolocate", *OURS)}
            contained: list[float] = []  # GEOLocate radius when it contains the position
            not_contained = 0
            no_position = 0
            no_response = 0
            for a in answerable:
                pos = _positions(a, gaz)
                if pos is None:
                    no_position += 1
                    continue
                rec = by_id[a.audit_id].record
                path = CACHE / f"{_key(_params(rec.locality, rec.county))}.json"
                top = None
                if path.exists():
                    top = _geolocate_top(json.loads(path.read_text(encoding="utf-8")))
                else:
                    no_response += 1
                row: dict[str, Any] = {"sample": name, "audit_id": a.audit_id}
                g_err = min(_dist(top["point"], p) for p in pos) if top else None
                errs["geolocate"].append(g_err)
                row["geolocate"] = None if top is None else {
                    "error_m": round(g_err) if g_err is not None else None,
                    "radius_m": top["radius_m"], "score": top["score"],
                    "precision": top["precision"], "parse_pattern": top["parse_pattern"],
                }  # fmt: skip
                if top and g_err is not None and top["radius_m"] is not None:
                    if g_err <= top["radius_m"]:
                        contained.append(top["radius_m"])
                        row["geolocate"]["contains_position"] = True
                    else:
                        not_contained += 1
                        row["geolocate"]["contains_position"] = False
                for k in OURS:
                    p = _our_point(reports[k][a.audit_id], gaz)
                    e = min(_dist(p, q) for q in pos) if p else None
                    errs[k].append(e)
                    row[k] = {"error_m": round(e) if e is not None else None}
                result["records"].append(row)
            n = len(errs["geolocate"])
            result["samples"][name] = {
                "annotator": annotator, "answerable": len(answerable),
                "with_defensible_position": n, "no_defensible_position": no_position,
                "geolocate_no_response": no_response,
                **{k: _summary(v, n) for k, v in errs.items()},
                "geolocate_containment": {
                    "contains": len(contained), "does_not": not_contained,
                    "median_radius_when_contained_m":
                        round(statistics.median(contained)) if contained else None,
                },
            }  # fmt: skip
            pool = pooled.setdefault(annotator, {k: [] for k in ("geolocate", *OURS)})
            for k, v in errs.items():
                pool[k].extend(v)
            pool.setdefault("_contained", []).extend(contained)
            pool.setdefault("_not", []).append(not_contained)
    for annotator, pool in pooled.items():
        n = len(pool["geolocate"])
        result["pooled"][annotator] = {
            **{k: _summary(pool[k], n) for k in ("geolocate", *OURS)},
            "geolocate_containment": {
                "contains": len(pool["_contained"]), "does_not": sum(pool["_not"]),
                "median_radius_when_contained_m":
                    round(statistics.median(pool["_contained"])) if pool["_contained"] else None,
            },
        }  # fmt: skip
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    if sys.argv[1:2] == ["query"]:
        query()
    elif sys.argv[1:2] == ["score"] and len(sys.argv) == 3:
        r = score(Path(sys.argv[2]))
        for who, p in r["pooled"].items():
            print(who, json.dumps(p))
    else:
        sys.exit(__doc__)
