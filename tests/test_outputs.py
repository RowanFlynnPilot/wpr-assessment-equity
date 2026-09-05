"""Contract tests on the committed output/ feeds — what the widget will serve.

Runs in CI before every deploy, so a push that lists a year in index.json
without its feed file, ships a feed the widget can't read, or leaks a
parcel number / address / name into the public feeds fails BEFORE Pages
publishes it.
"""

import json
import os
import re
from pathlib import Path

import pytest

OUTPUT = Path(__file__).resolve().parent.parent / "output"
FEEDS = sorted(OUTPUT.glob("findings-*.json"))
REQUIRED = ["schema", "study_year", "county", "reference", "sample",
            "municipalities", "pooled", "deciles"]

# Anything that looks like a Marathon parcel number, or a per-property field,
# has no business in an aggregate-only feed.
PARCEL_ID = re.compile(r"\b\d{3}-\d{4}-\d{3}-\d{4}\b|\b\d{14}\b")
FORBIDDEN_KEYS = {"address", "grantor", "grantee", "parcel", "parcelid",
                  "parcel_number", "owner", "name_of", "document_number"}


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k.lower()
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


def test_index_lists_only_years_whose_feed_exists():
    index = json.loads((OUTPUT / "index.json").read_text(encoding="utf-8"))
    assert index["years"], "index.json lists no years"
    assert index["latest"] == max(index["years"])
    for y in index["years"]:
        assert (OUTPUT / f"findings-{y}.json").exists(), f"index lists {y} but findings-{y}.json is absent"


@pytest.mark.skipif(not os.environ.get("CI"),
                    reason="locally, output/ may hold not-yet-published years")
def test_every_feed_file_is_indexed():
    index = json.loads((OUTPUT / "index.json").read_text(encoding="utf-8"))
    on_disk = {int(p.stem.split("-")[1]) for p in FEEDS}
    assert on_disk == set(index["years"]), f"feeds on disk {sorted(on_disk)} != index {index['years']}"


@pytest.mark.parametrize("feed", FEEDS, ids=[p.name for p in FEEDS])
def test_feed_has_widget_contract(feed):
    f = json.loads(feed.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in f]
    assert not missing, f"{feed.name} missing {missing}"
    assert f["schema"] >= 2
    assert f["study_year"] == int(feed.stem.split("-")[1])
    assert len(f["deciles"]) >= 2
    assert f["pooled"]["n"] == f["sample"]["final_n"]


@pytest.mark.parametrize("path", sorted(OUTPUT.glob("*.json")), ids=lambda p: p.name)
def test_public_feeds_are_aggregate_only(path):
    text = path.read_text(encoding="utf-8")
    assert not PARCEL_ID.search(text), f"{path.name} contains a parcel-number-shaped value"
    keys = set(_walk_keys(json.loads(text)))
    leaked = {k for k in keys if any(bad in k for bad in FORBIDDEN_KEYS)}
    assert not leaked, f"{path.name} carries per-property keys: {sorted(leaked)}"
