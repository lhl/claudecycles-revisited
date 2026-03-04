# Claude’s Cycles: Odd-`m` construction and proof

## Problem

For an integer `m > 2`, let `G_m` be the directed graph on vertices `Z_m^3`, i.e. triples `(i,j,k)` with `0 <= i,j,k < m`, with exactly three outgoing arcs from each vertex:

- `(i,j,k) -> (i+1, j, k)`
- `(i,j,k) -> (i, j+1, k)`
- `(i,j,k) -> (i, j, k+1)`

where all additions are modulo `m`.

Goal: partition the `3m^3` arcs into three arc-disjoint directed cycles, each a Hamiltonian cycle of length `m^3`.

## Construction (odd `m`)

Define `s(i,j,k) := (i + j + k) mod m`.

At each vertex `(i,j,k)`, define a permutation `d(i,j,k) = (d0,d1,d2)` of `{0,1,2}` by:

- If `s=0`:
  - if `j = m-1`, set `d = (0,1,2)`
  - else set `d = (2,1,0)`
- Else if `s=m-1`:
  - if `i > 0`, set `d = (1,2,0)`
  - else set `d = (2,1,0)`
- Else (i.e., `0 < s < m-1`):
  - if `i = m-1`, set `d = (2,0,1)`
  - else set `d = (1,0,2)`

Cycle `c ∈ {0,1,2}` uses the unique outgoing arc that “bumps” coordinate `d_c`:

- `d_c = 0` means `(i,j,k) -> (i+1,j,k)`
- `d_c = 1` means `(i,j,k) -> (i,j+1,k)`
- `d_c = 2` means `(i,j,k) -> (i,j,k+1)`

This construction is implemented in `claudescycles/claude.py`.

## Theorem

**Theorem (odd-`m` decomposition).** If `m` is odd and `m > 2`, the construction above decomposes the arcs of `G_m` into three arc-disjoint directed Hamiltonian cycles, each of length `m^3`.

### Lemma 1 (Arc partition is automatic)

For every vertex `(i,j,k)`, `d(i,j,k)` is a permutation of `{0,1,2}` by construction. Therefore:

- Each of the three cycles has outdegree `1` at every vertex.
- The three cycles are arc-disjoint (no vertex assigns the same outgoing arc to two cycles).
- The union of the cycles contains all arcs of `G_m` (at every vertex, the 3 outgoing arcs are used exactly once).

Thus, it remains only to prove that each cycle is Hamiltonian (a single directed cycle visiting all vertices).

### Lemma 2 (Layering by `s`)

Along any arc of `G_m`, exactly one of `i,j,k` increases by `1` (mod `m`), hence `s(i,j,k)` increases by `1` (mod `m`) at every step.

Consequences:

- In any directed cycle, the sequence of `s` values is periodic with period `m`.
- Vertices with the same `s` value are encountered exactly `m` steps apart along the cycle.

This “layering” structure is a key invariant used below.

## Cycle 0 is Hamiltonian when `m` is odd

Let `C0` be the cycle for `c=0`. Unwinding the definition of `d`, the bump rule for `C0` is:

- If `s=0`: bump `i` iff `j=m-1`; otherwise bump `k`.
- If `0 < s < m-1`: bump `k` iff `i=m-1`; otherwise bump `j`.
- If `s=m-1`: bump `j` iff `i>0`; otherwise bump `k`.

We prove that `C0` has length `m^3` by describing its evolution in “blocks” where the first coordinate `i` is fixed.

### Lemma 3 (`i` changes only at one recognizable event)

In `C0`, the coordinate `i` is bumped only in the case `s=0` and `j=m-1`. Therefore `i` is constant except at vertices of the form

`(i, m-1, 1-i)`, because `s=0` forces `k ≡ -i-j ≡ 1-i (mod m)` when `j=m-1`.

At such a vertex, the rule bumps `i`, so the cycle moves from the `i`-block to the `(i+1)`-block.

### Lemma 4 (The `i=0` block visits all `m^2` vertices with `i=0`)

Assume `i=0` and we have not yet reached the exit vertex `(0,m-1,1)`. For `i=0` the rule simplifies to:

- if `s ∈ {1,2,...,m-2}`: bump `j`;
- if `s=m-1`: bump `k`;
- if `s=0` and `j != m-1`: bump `k`.

Consider what happens over one full “`s`-period” of `m` steps. By Lemma 2, we encounter `s=0` and `s=m-1` exactly once each in those `m` steps; all other `m-2` steps have `1 <= s <= m-2`.

Therefore, over any `m` consecutive steps within the `i=0` block:

- `j` is bumped exactly `m-2` times;
- `k` is bumped exactly `2` times;
- `i` is never bumped.

Modulo `m`, that net effect is `(j,k) -> (j-2, k+2)`.

Now restrict attention to the vertices with `s=0`. When `i=0` and `s=0`, we have `j+k ≡ 0 (mod m)`, so such vertices are exactly `(0, m-k, k)` for `k ∈ Z_m`.

Each time the walk returns to `s=0` (which happens every `m` steps), the value of `k` increases by `2` modulo `m`. Because `m` is odd, `2` is invertible in `Z_m`, hence the sequence `k, k+2, k+4, ...` hits every residue class. In particular, we eventually reach `k=1`, i.e. the unique exit vertex `(0,m-1,1)`.

Between successive visits to `s=0`, we traverse all intermediate `s` layers in order and bump `j` on each of those layers. Since `k` stays fixed during those `m-2` middle-layer steps, the corresponding values of `j` are all distinct modulo `m`. Hence, for each fixed `k`, we visit all vertices `(0,j,k)` exactly once before the next `s=0` time.

Because `k` takes every value in `Z_m` before the exit, the `i=0` block visits all `m^2` vertices with first coordinate `0`, and then exits to `i=1`.

### Lemma 5 (Blocks `1 <= i <= m-2` each visit all `m^2` vertices with that `i`)

Fix an `i` with `1 <= i <= m-2` and consider the walk until it reaches the exit vertex `(i, m-1, 1-i)`.

For such `i`, the rule is:

- if `s=0` and `j != m-1`: bump `k`;
- otherwise: bump `j`.

Now look at the walk sampled every `m` steps, i.e. at the times when `s=0` (Lemma 2). Suppose we are at an `s=0` vertex with `j != m-1`. The next step bumps `k`, so `j` stays fixed while `s` becomes `1`. Then for the next `m-1` steps (covering `s=1,2,...,m-1`), the rule bumps `j` on *every* step (because `s != 0` and `i` is neither `0` nor `m-1`), hence `j` takes the values

`j, j+1, j+2, ..., j+(m-1)`

modulo `m`, i.e. all `m` residues, while `k` stays fixed during those `m-1` steps.

At the end of that `m`-step segment we are back at `s=0` and:

- `j` has increased by `m-1`, i.e. `j -> j-1 (mod m)`;
- `k` has increased by `1` (from the single `k` bump);
- `i` is unchanged.

Therefore, the successive `s=0` vertices in this `i`-block are exactly

`(i, j_0, -i-j_0), (i, j_0-1, -i-j_0+1), (i, j_0-2, -i-j_0+2), ...,`

until we reach the unique `s=0` vertex with `j=m-1`, namely `(i, m-1, 1-i)`, where the rule bumps `i` and the block ends.

Because this hits each `j` value exactly once on `s=0`, and because each such `s=0` hit generates `m` distinct vertices with that fixed `i` and fixed `k` while `j` runs through all residues, the block contains exactly `m * m = m^2` distinct vertices, i.e. all vertices with first coordinate `i`.

### Lemma 6 (The final `i=m-1` block closes the cycle)

When `i=m-1`, the bump rule is:

- if `0 < s < m-1`: bump `k`;
- if `s=m-1`: bump `j`;
- if `s=0`: bump `k` unless `j=m-1`, in which case bump `i` (wrapping to `0`).

In particular, after the previous block ends we enter this block at the vertex `(m-1, m-1, 3)` (all arithmetic mod `m`), and from then on `k` is bumped on every layer except the single layer `s=m-1`, where `j` is bumped.

Sampling again at `s=0` (every `m` steps), the `s=0` vertices encountered in this final block are

`(m-1, 0, 1), (m-1, 1, 0), (m-1, 2, m-1), ..., (m-1, m-1, 2)`,

which are exactly the `m` solutions to `j+k ≡ 1 (mod m)` with `i=m-1`. At the last one, `(m-1,m-1,2)`, we have `s=0` and `j=m-1`, hence the rule bumps `i` and wraps back to `i=0`, returning to the start of the `i=0` block.

Together with Lemmas 3–6, `C0` visits all `m * m^2 = m^3` vertices exactly once and returns to its start, hence is Hamiltonian.

## Cycle 1 is Hamiltonian when `m` is odd

Let `C1` be the cycle for `c=1`. Its bump rule simplifies to:

- if `s=0`: bump `j`;
- if `0 < s < m-1`: bump `i`;
- if `s=m-1`: bump `k` iff `i>0`, else bump `j`.

As in Lemma 2, `s` increases by `1` on every step, so returns to `0` exactly every `m` steps. Consider therefore the map `Φ1` on the `s=0` layer that advances by exactly `m` steps along `C1`. We compute `Φ1` explicitly.

Let `(i,j,k)` satisfy `s=0`. The first step (at `s=0`) bumps `j`, giving `(i, j+1, k)` at `s=1`. Then for the next `m-2` steps (layers `s=1..m-2`), we bump `i` each time, arriving at `(i-2, j+1, k)` at layer `s=m-1` (because `m-2 ≡ -2 (mod m)`).

Finally, at `s=m-1` we bump:

- `k` if `i-2 != 0`, i.e. if `i != 2`;
- otherwise bump `j`.

Thus the `m`-step map on the `s=0` layer is:

- if `i != 2`: `Φ1(i,j,k) = (i-2, j+1, k+1)`;
- if `i = 2`: `Φ1(2,j,k) = (0, j+2, k)`.

Now assume `m` is odd, so `2` is invertible in `Z_m`. For each pair `(r,t) ∈ Z_m^2`, define a vertex

`v(r,t) := (-2t, r+t, t-r)` (all coordinates mod `m`).

Then `v(r,t)` always lies on the `s=0` layer because the coordinates sum to `0`. Moreover, the map `(r,t) -> v(r,t)` is a bijection from `Z_m^2` onto the `s=0` layer (invert using division by `2`).

Direct substitution into the cases above shows:

- if `t != m-1`, then `Φ1(v(r,t)) = v(r, t+1)`;
- if `t = m-1`, then `Φ1(v(r,t)) = v(r+1, 0)`.

Therefore, starting at `v(0,0) = (0,0,0)`, repeated application of `Φ1` cycles through all `m^2` vertices of the `s=0` layer exactly once before returning. Any return to the start of `C1` must happen at a time difference divisible by `m` (because `s` must match), hence cannot occur before `m * m^2 = m^3` steps. Since `G_m` has exactly `m^3` vertices, `C1` is a Hamiltonian cycle.

## Cycle 2 is Hamiltonian when `m` is odd

Let `C2` be the cycle for `c=2`. Its bump rule simplifies to:

- if `s=0`: bump `k` iff `j=m-1`, else bump `i`;
- if `0 < s < m-1`: bump `j` iff `i=m-1`, else bump `k`;
- if `s=m-1`: bump `i`.

Again consider the `m`-step map `Φ2` on the `s=0` layer.

Let `(i,j,k)` have `s=0`.

### Case A: `j != m-1`

At `s=0` we bump `i`, giving `(i+1, j, k)` at `s=1`.

For layers `s=1..m-2`, `i` stays constant, so the rule either bumps `k` on every such step (if `i+1 != m-1`) or bumps `j` on every such step (if `i+1 = m-1`, i.e. `i = m-2`).

- If `i != m-2`, then `k` is bumped `m-2` times, i.e. `k -> k-2`, and at `s=m-1` we bump `i` once more. Net effect:
  - `i -> i+2`
  - `j` unchanged
  - `k -> k-2`
- If `i = m-2`, then `j` is bumped `m-2` times, i.e. `j -> j-2`, and at `s=m-1` we bump `i` (wrapping to `0`). Net effect:
  - `i -> 0`
  - `j -> j-2`
  - `k` unchanged

So on `s=0` with `j != m-1`, the map `Φ2` is:

- if `i != m-2`: `Φ2(i,j,k) = (i+2, j, k-2)`;
- if `i = m-2`: `Φ2(m-2, j, k) = (0, j-2, k)`.

### Case B: `j = m-1`

At `s=0` we bump `k`, giving `(i, m-1, k+1)` at `s=1`.

If `i != m-1`, then layers `s=1..m-2` bump `k` throughout (since `i<m-1`), hence `k` changes by `m-2` and then `s=m-1` bumps `i`. Net effect:

- `i -> i+1`
- `j` unchanged (`m-1`)
- `k -> k-1`

If `i = m-1`, then layers `s=1..m-2` bump `j` throughout (since `i=m-1`), sending `j` from `m-1` to `m-3`, and then `s=m-1` bumps `i` to `0`. Net effect:

- `i -> 0`
- `j -> m-3`
- `k -> k+1`

### Orbit structure on `s=0` when `m` is odd

When `m` is odd, stepping by `+2` modulo `m` permutes `Z_m`. Starting at `(0,0,0)` and iterating `Φ2`:

- while `j != m-1`, the rule advances `i` by `+2` through all residues; when the orbit reaches the unique value `i=m-2`, it resets `i` to `0` and updates `j -> j-2`;
- the updates `j -> j-2` also permute `Z_m`, so eventually we reach `j=m-1`;
- on the `j=m-1` fiber, `Φ2` advances `i` by `+1` through all residues; when it reaches `i=m-1`, it exits to `j=m-3` (which is again `j-2`).

Thus every `j` value is reached, and for each fixed `j` the orbit visits all `m` values of `i` exactly once. Hence the `s=0` layer has a single `Φ2`-orbit of length `m^2`, implying (as in the cycle-1 proof) that `C2` returns to its start only after `m^3` steps. Therefore `C2` is Hamiltonian.

Combining the cycle-0, cycle-1, and cycle-2 sections with Lemma 1 proves the theorem.

## Even `m`

The construction above is *not* Hamiltonian for even `m` (it repeats early). See `artifacts/claude_scan_even_4_100.json` for verifier outputs on even `m` in `[4,100]`.
