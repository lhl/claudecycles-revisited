from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List


@dataclass(frozen=True)
class Decomposition:
    m: int
    dirs: List[bytearray]
    meta: dict[str, Any] = field(default_factory=dict)


def _parse_dirs_field(m: int, value: Any) -> bytearray:
    n = m * m * m

    if isinstance(value, str):
        raw = value.encode("ascii")
        if len(raw) != n:
            raise ValueError(f"dirs string length {len(raw)} != m^3={n}")
        bad = [chr(ch) for ch in raw if ch not in b"012"]
        if bad:
            raise ValueError(f"dirs string contains invalid digits: {sorted(set(bad))}")
        return bytearray(ch - ord("0") for ch in raw)

    if isinstance(value, (bytes, bytearray)):
        if len(value) != n:
            raise ValueError(f"dirs byte length {len(value)} != m^3={n}")
        if any(d not in (0, 1, 2) for d in value):
            raise ValueError("dirs byte array must contain only 0, 1, 2")
        return bytearray(value)

    if isinstance(value, list):
        if len(value) != n:
            raise ValueError(f"dirs list length {len(value)} != m^3={n}")
        out = bytearray(n)
        for idx, item in enumerate(value):
            if item not in (0, 1, 2):
                raise ValueError(f"dirs[{idx}] must be 0, 1, or 2; got {item!r}")
            out[idx] = int(item)
        return out

    raise TypeError(f"unsupported dirs encoding: {type(value).__name__}")


def load_decomposition(path: str | Path) -> Decomposition:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value must be an object")

    if "m" not in payload:
        raise ValueError("missing required field 'm'")
    if "dirs" not in payload:
        raise ValueError("missing required field 'dirs'")

    m = int(payload["m"])
    raw_dirs = payload["dirs"]
    if not isinstance(raw_dirs, list) or len(raw_dirs) != 3:
        raise ValueError("'dirs' must be a length-3 list")

    dirs = [_parse_dirs_field(m, value) for value in raw_dirs]
    meta = payload.get("meta", {})
    if not isinstance(meta, dict):
        raise ValueError("'meta' must be an object when present")

    return Decomposition(m=m, dirs=dirs, meta=meta)


def save_decomposition(path: str | Path, decomp: Decomposition) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "m": decomp.m,
        "dirs": ["".join(str(int(d)) for d in dc) for dc in decomp.dirs],
        "meta": decomp.meta,
    }
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

