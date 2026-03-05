from __future__ import annotations

import pytest

from claudescycles.constructions import _choose_a_odd_m, construct_decomposition_odd_m
from claudescycles.verify import verify_decomposition


@pytest.mark.parametrize("m", [5, 7, 9, 11, 15])
def test_odd_construction_verifies(m: int) -> None:
    decomp = construct_decomposition_odd_m(m)
    report = verify_decomposition(m, decomp.dirs)
    assert report.ok, report.error


def test_choose_a_rejects_m3() -> None:
    with pytest.raises(ValueError):
        _choose_a_odd_m(3)
