from __future__ import annotations

from claudescycles.constructions import construct_decomposition_odd_m
from claudescycles.gm import n_vertices
from claudescycles.verify import verify_decomposition


def test_verify_accepts_odd_construction_m5() -> None:
    decomp = construct_decomposition_odd_m(5)
    report = verify_decomposition(5, decomp.dirs)
    assert report.ok, report.error


def test_verify_rejects_non_partition() -> None:
    m = 3
    n = n_vertices(m)
    dirs = [bytearray([0] * n), bytearray([1] * n), bytearray([1] * n)]
    report = verify_decomposition(m, dirs)
    assert not report.ok
    assert not report.arc_partition_ok


def test_verify_rejects_non_hamilton_cycle() -> None:
    m = 3
    n = n_vertices(m)
    dirs = [bytearray([0] * n), bytearray([1] * n), bytearray([2] * n)]
    report = verify_decomposition(m, dirs)
    assert not report.ok
    assert report.arc_partition_ok
    assert any(not check.ok for check in report.cycle_checks)

