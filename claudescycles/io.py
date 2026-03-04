from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class Decomposition:
    m: int
    # dirs[c][idx] in {0,1,2} for cycle c at vertex index idx.
    dirs: List[bytearray]
    meta: dict


def _parse_dirs_field(m: int, value) -> bytearray:
    n = m * m * m

    if isinstance(value, str):
        # Compact representation: string of digits (e.g. "012201...") length n.
        b = value.encode("ascii")
        if len(b) != n:
            raise ValueError(f"dirs string length {len(b)} != m^3={n}")
        out = bytearray(len(b))
        for i, ch in enumerate(b):
            if ch < 48 or ch > 50:  # '0'..'2'
                raise ValueError(f"dirs[{i}] not in '0'..'2': {chr(ch)!r}")
            out[i] = ch - 48
        return out

    if isinstance(value, list):
        if len(value) != n:
            raise ValueError(f"dirs list length {len(value)} != m^3={n}")
        out = bytearray(n)
        for i, d in enumerate(value):
            if not isinstance(d, int):
                raise TypeError(f"dirs[{i}] must be int; got {type(d).__name__}")
            if d not in (0, 1, 2):
                raise ValueError(f"dirs[{i}] not in {{0,1,2}}: {d}")
            out[i] = d
        return out

    raise TypeError(f"unsupported dirs type: {type(value).__name__}")


def load_decomposition(path: str | Path) -> Decomposition:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("top-level JSON must be an object")

    if "m" not in data:
        raise KeyError("missing required field 'm'")
    m = data["m"]
    if not isinstance(m, int):
        raise TypeError(f"'m' must be int; got {type(m).__name__}")

    meta = dict(data.get("meta", {}))

    if "dirs" in data:
        dirs_raw = data["dirs"]
        if not isinstance(dirs_raw, list) or len(dirs_raw) != 3:
            raise TypeError("'dirs' must be a list of 3 elements")
        dirs = [_parse_dirs_field(m, v) for v in dirs_raw]
        return Decomposition(m=m, dirs=dirs, meta=meta)

    if "cycles" in data:
        cycles = data["cycles"]
        if not isinstance(cycles, list) or len(cycles) != 3:
            raise TypeError("'cycles' must be a list of 3 objects")
        dirs: List[bytearray] = []
        for idx, c in enumerate(cycles):
            if not isinstance(c, dict):
                raise TypeError(f"cycles[{idx}] must be an object")
            if "dirs" not in c:
                raise KeyError(f"cycles[{idx}] missing 'dirs'")
            dirs.append(_parse_dirs_field(m, c["dirs"]))
        return Decomposition(m=m, dirs=dirs, meta=meta)

    raise KeyError("expected either top-level 'dirs' or 'cycles' with per-cycle 'dirs'")


def save_decomposition(path: str | Path, decomp: Decomposition) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    m = decomp.m
    n = m * m * m
    if len(decomp.dirs) != 3:
        raise ValueError("decomposition must have exactly 3 cycles")
    dirs_strs = []
    for c in range(3):
        arr = decomp.dirs[c]
        if len(arr) != n:
            raise ValueError(f"cycle {c}: dirs length {len(arr)} != {n}")
        dirs_strs.append("".join(str(int(x)) for x in arr))

    data = {
        "m": m,
        "vertex_order": "lex(i,j,k) => idx = i*m^2 + j*m + k",
        "dirs": dirs_strs,
        "meta": decomp.meta or {},
    }
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

