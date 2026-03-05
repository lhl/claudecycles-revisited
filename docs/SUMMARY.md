# Summary

## Proven

- For every odd `m >= 5`, [proofs/partial_theorem.md](/home/lhl/github/lhl/claudescycles-revisited/proofs/partial_theorem.md) gives an explicit decomposition of `G_m` into three directed Hamiltonian cycles.
- The construction is implemented in [claudescycles/constructions.py](/home/lhl/github/lhl/claudescycles-revisited/claudescycles/constructions.py).
- The decomposition verifier is implemented in [claudescycles/verify.py](/home/lhl/github/lhl/claudescycles-revisited/claudescycles/verify.py).

## Computational Evidence

- Exact CP-SAT artifacts were generated and verified for `m = 3, 4, 6, 8, 10, 12, 14`.
- The odd construction was validated for every odd `m` in `5..31`.
- The return-map formulas used in the proof were checked computationally for every odd `m` in `5..31`.

## Not Proved

- No general theorem for even `m` is proved here.
- The case `m = 3` is supported by a verified solver witness, not by the odd-family proof.
- No general pattern has yet been extracted from the even solver artifacts.

## Key Artifacts

- Solver outputs: `artifacts/solutions/cpsat_m*.json`
- Odd construction validation: `artifacts/validation/odd_m_validation.json`
- Odd return-map checks: `artifacts/validation/odd_return_map_checks.json`
- Proof: [proofs/partial_theorem.md](/home/lhl/github/lhl/claudescycles-revisited/proofs/partial_theorem.md)

## Next Experiments

- Normalize and compare the even solver artifacts to search for a reusable family.
- Try proof strategies that replace the `+2` return-map shift in `C_2`, which is the first obstruction in even modulus.
- Either fold `m = 3` into a symbolic family or prove that the present row-based family cannot do so.
