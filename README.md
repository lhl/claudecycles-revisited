# claudescycles-revisited

Search, verification, and proof tooling for decomposing the directed graph `G_m` from [PROBLEM.md](PROBLEM.md) into three arc-disjoint directed Hamiltonian cycles.

## Problem

For `m > 2`, the graph `G_m` has vertex set `Z_m^3`.
Each vertex `(i,j,k)` has three outgoing arcs:

- `(i,j,k) -> (i+1,j,k)`
- `(i,j,k) -> (i,j+1,k)`
- `(i,j,k) -> (i,j,k+1)`

all modulo `m`.

The goal is to partition all `3m^3` arcs into three directed cycles, each of length `m^3`.

## Current Status

### Proved

- There is an explicit construction for every odd `m >= 5`.
- A partial proof is written in [proofs/partial_theorem.md](proofs/partial_theorem.md).
- The proof shows:
  - each of the three cycles is Hamiltonian,
  - the cycles are arc-disjoint,
  - their union covers every arc of `G_m`.

### Computationally Verified

- Exact CP-SAT solver artifacts were generated and verified for:
  - `m = 3, 4, 6, 8, 10, 12, 14`
- The explicit odd construction was validated for:
  - every odd `m` in `5..31`
- The return-map identities used in the odd-`m` proof were checked for:
  - every odd `m` in `5..31`

### Not Yet Proved

- No general theorem for even `m` is proved in this repo.
- `m = 3` is covered by a verified solver witness, not by the explicit odd-family proof.
- No general even-family pattern has yet been extracted from the solver outputs.

## Main Components

- `claudescycles/gm.py`
  - graph indexing and successor/predecessor helpers
- `claudescycles/verify.py`
  - deterministic verifier for:
    - Hamiltonicity of each cycle,
    - arc-disjointness,
    - full arc coverage
- `claudescycles/constructions.py`
  - explicit odd-`m` construction
- `scripts/search_cp_sat.py`
  - exact OR-Tools CP-SAT search for small `m`
- `scripts/gen_construction_odd.py`
  - materialize the explicit odd-`m` construction as JSON
- `scripts/validate_construction_odd.py`
  - validate the odd family over a range of odd `m`
- `scripts/check_return_maps_odd.py`
  - check the return-map formulas used in the proof
- `proofs/partial_theorem.md`
  - theorem/lemma proof writeup and unresolved extensions
- `artifacts/`
  - machine-readable solution and validation outputs

## Artifact Layout

- `artifacts/solutions/cpsat_m*.json`
  - exact solver witnesses
- `artifacts/solutions/odd_m/m5.json`
  - sample generated odd-family witness
- `artifacts/validation/cpsat_m*.verify.json`
  - verifier reports for solver witnesses
- `artifacts/validation/odd_m_validation.json`
  - odd-family validation summary
- `artifacts/validation/odd_return_map_checks.json`
  - proof-supporting return-map checks

## Reproducibility

### Run tests

```bash
uv run pytest -q
```

### Verify an artifact

```bash
python scripts/verify_decomp.py artifacts/solutions/cpsat_m14.json
python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m14.json
```

### Search small cases exactly

```bash
python scripts/search_cp_sat.py 3 --time-limit 60 --out artifacts/solutions/cpsat_m3.json
python scripts/search_cp_sat.py 4 --time-limit 60 --out artifacts/solutions/cpsat_m4.json
```

### Generate the odd construction

```bash
python scripts/gen_construction_odd.py 5 --out artifacts/solutions/odd_m/m5.json
```

### Validate the odd family

```bash
python scripts/validate_construction_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_m_validation.json
```

### Check the proof formulas

```bash
python scripts/check_return_maps_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_return_map_checks.json
```

## Proof Summary

The proof for odd `m >= 5` uses the linear coordinate change

`(u,v,w) = (i, i+j, i+j+k)`,

so every arc increases `w` by `1`.
This converts each candidate cycle into an `m`-step return map on the slice `w = 0`.
The proof then shows:

- the three cycles partition the outgoing arcs at each vertex,
- each return map is a single cycle on the `m^2` points with `w = 0`,
- therefore each lifted orbit has length `m^3`.

The obstruction to extending the same proof directly to even `m` is also explicit in the proof:
for one cycle, the return map shifts `v` by `+2`, and `2` is not invertible modulo even `m`.

## Future Directions

- Normalize the even solver artifacts and search for a reusable construction family.
- Develop an even-`m` proof strategy that avoids the noninvertible `+2` return-map shift.
- Either absorb `m = 3` into a symbolic family or prove that the current row-based family cannot do so.
- Push the exact search frontier beyond `m = 14` once a better even-case hypothesis is available.

## Snapshot

At the end of this work:

- the verifier is deterministic and reusable,
- the odd-`m` family is implemented and proved for all odd `m >= 5`,
- solver witnesses exist for selected small odd and even values,
- the open part of the problem is now concentrated on a general even-`m` construction/proof.
