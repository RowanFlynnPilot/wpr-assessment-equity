"""Tests for the join contract: ID normalization, the multi-parcel acreage
fingerprint, and the loud join-rate gate."""

import pytest

from analysis.join import acreage_plausible, join, normalize_parcel_id


def test_normalize_strips_dashes_tabs_spaces():
    assert normalize_parcel_id("004-3006-032-0999") == "00430060320999"
    assert normalize_parcel_id("\t168-2807-071-0989") == "16828070710989"
    assert normalize_parcel_id(" 291-2907-353-0030 ") == "29129073530030"
    assert normalize_parcel_id("") == ""
    assert normalize_parcel_id(None) == ""


def _sale(pid="004-3006-032-0999", acres=0.3, price=200_000):
    return {"Parcel Number": pid, "_acres": acres, "_price": price}


def _parcel(propclass="1", assdacres="0.30"):
    return {"PROPCLASS": propclass, "ASSDACRES": assdacres,
            "CNTASSDVALUE": "180000", "PLACENAME": "CITY OF WAUSAU"}


def test_acreage_fingerprint():
    assert acreage_plausible(0.3, "0.30")            # exact
    assert acreage_plausible(0.0, "0.30")            # RETR blank -> cannot fire
    assert acreage_plausible(40.0, "")               # parcel blank -> cannot fire
    assert not acreage_plausible(40.0, "0.30")       # multi-parcel sale, one id
    assert not acreage_plausible(65.0, "5.00")       # the genuine June case
    assert acreage_plausible(1.0, "0.13")            # "1 acre" default on a city
                                                     # lot: entry noise, passes


def test_join_excludes_mixed_class():
    index = {"00430060320999": _parcel(propclass="1,4")}
    matches, excl = join([_sale()], index)
    assert matches == []
    assert excl["parcel not pure class 1"] == 1


def test_join_rate_gate_fails_loudly():
    index = {}  # nothing matches
    with pytest.raises(RuntimeError, match="join rate"):
        join([_sale() for _ in range(20)], index)


def test_join_happy_path():
    index = {"00430060320999": _parcel()}
    matches, excl = join([_sale()], index)
    assert len(matches) == 1
    assert sum(excl.values()) == 0
