# Odd-m Construction (m >= 5)

This document proves a concrete arc decomposition of `G_m` (as defined in `PROBLEM.md`)
into three directed Hamiltonian cycles for every **odd** `m >= 5`.

Notes:
- `m=2` is impossible (given in the problem statement).
- `m=3` is a small exceptional case for this particular construction; an explicit
  verified decomposition is stored under `artifacts/solutions/cpsat_m3.json`.
- Even `m` are not covered here.

## Notation

Work in `Z_m = {0,1,...,m-1}` with arithmetic modulo `m`.

Vertices of `G_m` are triples `(i,j,k) in Z_m^3` with outgoing arcs:
- `i`-arc: `(i,j,k) -> (i+1, j, k)` (direction `0`)
- `j`-arc: `(i,j,k) -> (i, j+1, k)` (direction `1`)
- `k`-arc: `(i,j,k) -> (i, j, k+1)` (direction `2`)

A directed Hamiltonian cycle is a directed cycle visiting all `m^3` vertices exactly once.

## Coordinate Change

Define a bijection `T : Z_m^3 -> Z_m^3` by:

```text
u = i
v = i + j
w = i + j + k
```

The inverse is:

```text
i = u
j = v - u
k = w - v
```

Under `T`, the three outgoing arcs become:

```text
dir 0 (i-arc): (u,v,w) -> (u+1, v+1, w+1)
dir 1 (j-arc): (u,v,w) -> (u,   v+1, w+1)
dir 2 (k-arc): (u,v,w) -> (u,   v,   w+1)
```

In particular, **every move increments `w` by `+1`**.

## Construction Definition

Fix an odd `m >= 5`.

### Choosing the parameter A

Choose an integer `A` with `0 <= A <= m-2` such that:

```text
gcd(m, 2A+1) = 1
gcd(m, 2A+3) = 1
```

Lemma "Existence of A" below proves this is always possible for odd `m >= 5`.

Define the row-set:

```text
R = {2, 3, ..., A+1}  (possibly empty if A=0)
```

### Directions as a function of (v,w)

For each vertex `(u,v,w)` (equivalently `(i,j,k)`), define the outgoing direction of
each cycle `C0, C1, C2` by the following table. The rules depend only on `v` and `w`.

We use the shorthand:
- `v0` means `v = 0`
- `v!=0` means `v != 0`

Case 1: `w = 0`

```text
C0: dir 2
If v=0:   C2: dir 0,  C1: dir 1
If v!=0:  C2: dir 1,  C1: dir 0
```

Case 2: `w = 1`

```text
C1: dir 2
If v=0:   C2: dir 0,  C0: dir 1
If v!=0:  C2: dir 1,  C0: dir 0
```

Case 3: `w in {2,...,m-1}`

```text
C2: dir 2

If w in R:
  If v=0:   C0: dir 1,  C1: dir 0
  If v!=0:  C0: dir 0,  C1: dir 1

If w not in R:
  If v=0:   C0: dir 0,  C1: dir 1
  If v!=0:  C0: dir 1,  C1: dir 0
```

This completely defines three successor functions on `Z_m^3`, hence three directed cycles.

## Arc Partition (Arc-disjointness + Full Coverage)

At every `(v,w)`, the triple of directions assigned to `(C0,C1,C2)` is a permutation of
`{0,1,2}` by inspection of the cases above. Since the outgoing arcs from any vertex are
exactly the three arcs of directions `{0,1,2}`, this implies:

- The three cycles are arc-disjoint.
- Their union is the entire arc set of `G_m`.

Thus it remains to prove that **each** `C0,C1,C2` is a single Hamiltonian cycle.

## Two Lemmas About Skew-Product Dynamics

Because our directions depend only on `(v,w)` (not `u`), each cycle has the form:

```text
(u,v,w) -> (u + a(v,w), v + b(v,w), w + 1)
```

where:
- `a(v,w) in {0,1}` indicates whether the chosen direction is `dir 0` (only then does `u` increase),
- `b(v,w) in {0,1}` indicates whether the chosen direction is in `{dir 0, dir 1}` (then `v` increases),
  and for `dir 2` we have `b(v,w)=0`.

### Lemma 1 (Base cycle on (v,w))

Let `b : Z_m -> Z_m` be any function (in this construction it will be `{0,1}`-valued and depend only on `w`).
Define the map `F` on `Z_m^2` by:

```text
F(v,w) = (v + b(w), w + 1).
```

Let `B = sum_{t=0}^{m-1} b(t)` (computed in integers).

Then every orbit of `F` has length `m^2 / gcd(m, B)`. In particular, if `gcd(m,B)=1`,
then `F` is a single directed cycle of length `m^2` (Hamiltonian on `Z_m^2`).

Proof:
- After exactly `m` steps, `w` returns to its starting value, and `v` has increased by `B` modulo `m`.
- Therefore after `t*m` steps, `v` has increased by `t*B`.
- The smallest `t>0` with `t*B == 0 (mod m)` is `t = m / gcd(m,B)`.
- Hence the period is `m * (m / gcd(m,B)) = m^2 / gcd(m,B)`.

Since `Z_m^2` has exactly `m^2` states, if the period is `m^2` the map is one cycle. QED.

### Lemma 2 (Lift to (u,v,w))

Assume the `(v,w)`-projection of a cycle is Hamiltonian of length `m^2` (so it visits each `(v,w)` exactly once).
Let `a(v,w) in Z_m` be any function (in this construction `a in {0,1}`).

Consider the lifted map on `Z_m^3`:

```text
G(u,v,w) = (u + a(v,w), v + b(w), w + 1)
```

Let:

```text
Delta = sum_{(v,w) in Z_m^2} a(v,w)   (integer sum).
```

Then the orbit length in `Z_m^3` is:

```text
m^2 * (m / gcd(m, Delta)).
```

In particular, if `gcd(m,Delta)=1` then the orbit length is `m^3`, i.e. the cycle is Hamiltonian on `Z_m^3`.

Proof:
- By assumption, after `m^2` steps the state `(v,w)` returns to its start, and during those `m^2` steps it visits
  each `(v,w)` exactly once.
- Therefore in that period, `u` increases by exactly `Delta (mod m)`.
- Repeating the base period `t` times increases `u` by `t*Delta`. The smallest `t>0` with `t*Delta == 0 (mod m)`
  is `t = m / gcd(m,Delta)`.
- Multiply by the base period length `m^2` to obtain the orbit length. QED.

## Hamiltonicity of Each Cycle

We now compute `b(w)` and `Delta` for each cycle `C0,C1,C2`.

### Cycle C0

From the construction:
- On row `w=0`, `C0` uses `dir 2`, so `b0(0)=0`.
- On every row `w!=0`, `C0` uses `dir 0` or `dir 1`, so `b0(w)=1`.

Thus `B0 = sum_w b0(w) = m-1` and `gcd(m,B0)=gcd(m,m-1)=1`. By Lemma 1, the `(v,w)` dynamics is a single
cycle of length `m^2`.

For `a0(v,w)`, note that `a0=1` exactly where `C0` uses `dir 0` (i-arc).
Counting over all `(v,w)`:
- Row `w=0`: `a0=0` everywhere (since `dir 2`).
- Row `w=1`: `C0` uses `dir 0` for `v!=0` and `dir 1` for `v=0`, so contributes `m-1` ones.
- Rows `w in R` (there are `A` such rows): `C0` uses `dir 0` for `v!=0`, contributes `A*(m-1)` ones.
- Remaining rows `w in {2,...,m-1} \\ R` (there are `m-2-A` such rows): `C0` uses `dir 0` only at `v=0`,
  contributing `m-2-A` ones.

Therefore:

```text
Delta0 = (m-1) + A*(m-1) + (m-2-A) = m^2 - (2A+3).
```

So `gcd(m,Delta0) = gcd(m, 2A+3)`. By our choice of `A`, this gcd is `1`, and Lemma 2 implies `C0` is a
Hamiltonian cycle of length `m^3`.

### Cycle C1

Similarly:
- `C1` uses `dir 2` exactly on row `w=1`, so `b1(1)=0` and `b1(w)=1` for `w!=1`.
So `B1 = m-1` and the base `(v,w)` dynamics is a single cycle.

Now compute `Delta1` (number of `(v,w)` where `C1` uses `dir 0`):
- Row `w=1`: `a1=0` everywhere (since `dir 2`).
- Row `w=0`: `C1` uses `dir 0` for `v!=0` and `dir 1` for `v=0`, contributes `m-1` ones.
- Rows `w in R`: `C1` uses `dir 0` only at `v=0`, contributes `A` ones.
- Rows `w in {2,...,m-1} \\ R`: `C1` uses `dir 0` for `v!=0`, contributes `(m-2-A)*(m-1)` ones.

Therefore:

```text
Delta1 = (m-1) + A + (m-2-A)*(m-1) = m^2 - (2A+1).
```

So `gcd(m,Delta1) = gcd(m, 2A+1) = 1` by choice of `A`. By Lemma 2, `C1` is Hamiltonian of length `m^3`.

### Cycle C2

For `C2`:
- It uses `dir 2` on every row `w>=2`, i.e. on `m-2` rows, and uses `dir 0/1` only on rows `w=0,1`.
Thus `b2(w)=1` iff `w in {0,1}`, else `0`. So `B2 = 2`.

Because `m` is odd, `gcd(m,2)=1`, so by Lemma 1 the base dynamics on `(v,w)` is a single cycle of length `m^2`.

For `Delta2`, `C2` uses `dir 0` only at `v=0` on each of rows `w=0` and `w=1`, and never uses `dir 0` elsewhere.
So `Delta2 = 2`, and again `gcd(m,2)=1`.

By Lemma 2, `C2` is Hamiltonian of length `m^3`.

## Conclusion

For every odd `m >= 5`, the construction above:
- assigns each arc of `G_m` to exactly one of `C0,C1,C2`, and
- makes each `Ck` a directed Hamiltonian cycle.

Therefore `G_m` admits a decomposition into three directed Hamiltonian cycles for all odd `m >= 5`.

## Lemma (Existence of A for odd m >= 5)

Claim: For every odd `m >= 5`, there exists `A` with `0 <= A <= m-2` such that both `2A+1` and `2A+3` are
coprime to `m`.

Proof sketch (constructive via CRT):
- Let `p` range over the distinct odd primes dividing `m`.
- For a fixed prime `p`, the constraints "p does not divide 2A+1" and "p does not divide 2A+3" forbid at most
  two residue classes of `A (mod p)`:
  `A == (-1)/2 (mod p)` and `A == (-3)/2 (mod p)` (division by 2 is valid since `p` is odd).
  Hence there exists at least one allowed residue class mod `p`.
- For each prime `p|m`, choose any allowed residue `r_p (mod p)`; for `p>=5`, also choose `r_p != -1 (mod p)`.
  (This is always possible because at most three residues are forbidden and `p>=5`.)
- By the Chinese Remainder Theorem on the squarefree kernel `q = product_{p|m} p`, there exists `A0 (mod q)` with
  `A0 == r_p (mod p)` for all `p|m`. This ensures `gcd(m,2A0+1)=gcd(m,2A0+3)=1`.
- If `m>q`, there are multiple integers `A` in `[0,m-1]` congruent to `A0 (mod q)`, and none equals `m-1`
  because `m-1 == -1 (mod q)` while `A0 != -1 (mod q)` (due to the choice at some `p>=5` if present).
- If `m=q` (squarefree), then the same `A0 != -1 (mod m)` guarantee gives `A0 <= m-2`.
- The only excluded case is `m=3`, where the only possible residue mod 3 is `A == 2 == m-1`.

This provides existence for all odd `m >= 5`. QED.

