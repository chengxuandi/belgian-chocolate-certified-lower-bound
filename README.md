# Certified Lower Bound for the Belgian Chocolate Problem

This repository provides an explicit finite certificate showing that

```text
δ = 1969263222086617/2000000000000000
  = 0.9846316110433085
```

is admissible for the Generalized Belgian Chocolate Problem in the original polynomial formulation. It contains explicit real Hurwitz polynomials `x(s)`, `y(s)` and `p(s)` satisfying

```text
a_δ(s) = s² - 2δs + 1
b(s)   = s² - 1
p(s)   = a_δ(s)x(s) + b(s)y(s)
deg x >= deg y.
```

The certificate has actual degrees `deg x = 72`, `deg y = 72`, and `deg p = 74`. Therefore `δ* >= δ`.

This repository **does not claim to solve the full Belgian Chocolate Problem** or determine `δ*`. The previous published lower bound used for comparison is Charles–Boston (2018): `0.9808348`. The exact improvement over that value is `0.0037968110433085`.

To the best of the literature search conducted for this project, no published admissible value exceeding this bound was found. This is a bounded literature-search statement, not a world-record or global-optimality claim.

## Fast verification

Clone the repository and run the two independent standard-library checkers:

```bash
git clone https://github.com/chengxuandi/belgian-chocolate-certified-lower-bound.git
cd belgian-chocolate-certified-lower-bound
python verify_final_witness.py
python audit_final_witness.py
```

Expected key output is:

```text
IDENTITY = PASS
DEGREE = PASS
X_HURWITZ = PASS
Y_HURWITZ = PASS
P_HURWITZ = PASS
FINAL = PASS
```

No numerical root finding is required for the final proof. `verify_final_witness.py` uses exact rational reconstruction and integer-preserving Hurwitz-matrix elimination. `audit_final_witness.py` independently reconstructs the identity and uses an exact Routh table; it does not import the primary verifier.

## Files

- [Chinese result note](RESULT_NOTE_CN.md)
- [Formal Chinese PDF](FINAL_RESULT_CN.pdf)
- [Complete exact witness](WITNESS_FINAL.txt)
- [Primary exact verifier](verify_final_witness.py)
- [Independent Routh audit](audit_final_witness.py)
- [Verification guide](VERIFICATION_GUIDE_CN.md)
- [Search-method appendix](SEARCH_METHOD_APPENDIX_CN.md)
- [References and literature boundary](REFERENCES.md)
- [SHA-256 manifest](SHA256SUMS.txt)

The complete integer arrays in `WITNESS_FINAL.txt` are ordered by ascending powers of `s`; the file is self-contained and does not require any generator or search code.

## Discovery versus proof

Numerical optimization, quasi-admissible algebraic configurations, interval isolation and rationalization were discovery machinery. Correctness of the reported lower bound depends only on the explicit rational witness and the two exact verifiers. Search logs and source material are archived under `supplementary/` and are not required to establish admissibility.

## Relationship to the earlier formalization project

A separate earlier repository investigated computability and formalization aspects:

https://github.com/chengxuandi/belgian-chocolate-problem-lean-proof-20260910210030-init

That repository should not be interpreted as a complete solution of the BCP. The two projects are logically independent: the earlier repository preserves Lean and threshold-structure investigations; this repository provides one explicit certified admissible lower bound.

## License and citation

The files in this repository are released under the MIT License. See `LICENSE`.
The comparison source is Charles and Boston, *Exploiting algebraic structure in global optimization and the Belgian chocolate problem*, Journal of Global Optimization 72 (2018), 241–254, DOI [10.1007/s10898-018-0659-5](https://doi.org/10.1007/s10898-018-0659-5).
