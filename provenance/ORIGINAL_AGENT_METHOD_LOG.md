# Method and proof boundary

## Admission gate and literature

The starting adversarial audit is PASS. The starting witness SHA256 is
42c0568630f153d117cf4bd97c4289c2164c02762e47192bdd5fe8549879755d.
The initial bound for this run is exactly 103/105.

A fresh quick public search on 2026-09-15 found no credible higher public lower
bound for the same polynomial formulation. The confirmed external reference is
[Charles--Boston 2018](https://link.springer.com/article/10.1007/s10898-018-0659-5),
0.9808348 admissible. The authors are Zachary Charles and Nigel Boston.
This search does not establish priority or global optimality.

## Search adjacency and breadth

The quasi equations, in t=s², are

`(t²+alpha*t+1)X(t)+(t-1)Y(t)-Z(t)=0`,

where `alpha=2-4d²`, `X=product(t+A_i)^j_i`,
`Y=gain*product(t+B_i)^k_i`, and `Z=t^h*product(t+C_i)^ell_i`.
For x degree 2D, h=D+1-sum(ell); the coefficient system has D+1 equations.
The square-system condition is `2+len(j)+len(k)+len(ell)=D+1`.
All nodes also satisfy `sum(k)<D`, ensuring the highest coefficient cancels
identically. This invariant holds on both adjacency operators from the seed;
the reusable validator explicitly rejects other cases rather than silently
dropping a nonzero leading coefficient equation.

Finite adjacency operators are defined explicitly in `frontier_search.py`:

1. Growth: add one new frequency to one family; increase one existing
   multiplicity in each of the other two families. This increases degree x by 2.
   Every such edge from each retained parent is tried. New-frequency seeds use
   the geometric mean of the two selected old frequencies.
2. Balanced split/merge: split a multiplicity into two positive parts in one
   family and merge any pair in a different family. This preserves degree and
   the square-system count. Equal and near-equal splits are included.
3. Starting at degree 42, growth also treats the origin as a Z frequency:
   increase h by one, add an A/B frequency, and grow an exponent in B/A.
   Lateral moves split off one origin factor into a positive Z frequency while
   merging A/B; conversely absorb a positive Z factor into the origin while
   splitting A/B. Earlier layers 24--40 kept h=7 and did not try these moves.

At each degree, all growth neighbors from the retained parents are explored.
Then all balanced split/merge neighbors of the top three numerical growth
solutions are explored. Each distinct warm start gets two attempts, including a
deterministic randomized perturbation (seed 20260916). Labels are canonicalized
by multiplicities; distinct initial frequency assignments are kept as restarts.
This is a local multi-branch frontier, not exhaustive enumeration of every
possible multiplicity partition or every algebraic root.

An additional finite coverage pass (`complete_adjacency.py`) checks every
retained certified node's full same-degree neighbor set, and supplies numerical
attempts for missing configuration keys. The final pass must cover the last
completed degree before the final audit accepts the stopping report. Coverage
means attempted configurations, not proofs that failed configurations have no
solution. Supplemental attempts are included in final per-degree totals.

At most three interval-isolated distinct configurations are retained as parents
for the next degree, selected best first. Other numerical results are untrusted
attempt logs and are not admitted to the formal quasi leaderboard. Every
numerical attempt records its residual, scaled Jacobian condition, seed origin,
configuration, result and elapsed time. A failed solve is not an infeasibility
proof. Failed numerical iterates may contain nonfinite JSON tokens; those logs
are diagnostic only and are never inputs to the certificate verifier.

## Exact interval isolation

`certification.py` evaluates the coefficient system and its analytic Jacobian
as a factored arithmetic circuit. This avoids an exponentially large expansion
into multivariate monomials. `review_circuit.py` compares both coefficient
equations and Jacobian entries against an independent exact SymPy expansion on
the degree-22 seed and a degree-24 configuration.

For each retained candidate, the proof file contains dyadic center c, radius r,
and rational preconditioner C. All interval operations use integer floor/ceiling
rounding. The verifier checks

`rho = ||I-C J(box)||_infinity < 1`,

`||C F(c)||_infinity + rho*r < r`.

Consequently `T(z)=z-CF(z)` is a contraction mapping the box strictly into
itself. Since `I-CJ(c)` has norm below one, C and J(c) are nonsingular. At the
unique fixed point, F=0. Factor parameters are positive throughout the box, and
the d interval follows from exact rational squared inequalities. The rational
polynomial system and unique isolated real root specify real algebraic values.

The numerical inverse only proposes C; its accuracy is not trusted. The exact
norm inequalities certify it. Higher-precision retries alone are not described
as a second independent interval method.

At degree 64, unscaled high-precision Newton failed on an origin-growth
candidate at both 120 and 220 decimal digits. A separate scaled-variable and
row-scaled high-precision Newton calculation recovered it, and an integer-only
interval certificate then proved the root. Its strict rational witness raised
the incumbent again. From degree 66 onward, scaled Newton is tried first;
unscaled Newton at higher precision remains a fallback. This is an improvement
to candidate refinement, not a replacement for exact interval acceptance.

From the degree-68 partial-layer resume onward, the high-precision proposal Jacobian reuses each family
product and obtains its derivatives by synthetic division by the corresponding
linear factor. Division direction limits roundoff amplification. This branch
is used only for MP candidate calculations; the Dyadic integer interval proof
still evaluates the original factorized derivative circuit. Exact rational
division examples, 140-digit comparisons against the reference circuit, and
an exact containment proof identifying the same degree-64 algebraic root
validated the change (`fast_mp_review.json`, `fast_mp_algebraic_root_identity.json`).

## Strict rational witnesses

For an isolated d and rational e<d, put

`lambda=sqrt(((1-d)/(1+d))/((1-e)/(1+e)))`,
`a=1+lambda`, `b=1-lambda`, `N=as+b`, `D=bs+a`,
`L=a²+b²-2dab`.

Then `N²-D²=4lambda(s²-1)` and
`N²-2dND+D²=L(s²-2es+1)`.
The transformed finite polynomials have only strictly Hurwitz linear/quadratic
factors, since 0<lambda<1 and all frequency parameters are positive.

The x,y coefficients are rationalized; p is then defined afresh by exact integer
arithmetic at e. No perturbation margin, floating root, or numerical residual
is trusted for final acceptance.

More explicitly, the isolated coefficient identity yields the original quasi
polynomials `x_d(s)=(s²+2ds+1)X(s²)`, `y_d(s)=Y(s²)`, and `p_d(s)=Z(s²)`.
For n=degree x_d, the strict algebraic polynomials before rounding are
`x_e=L D(s)^n x_d(N(s)/D(s))`,
`y_e=4lambda D(s)^n y_d(N(s)/D(s))`, and
`p_e=D(s)^(n+2) p_d(N(s)/D(s))`.
The two displayed transformation identities prove the original BCP identity.
For any old root u with Re(u)<=0, its new root is
`s=(a*u-b)/(a-b*u)` and its real-part numerator is
`(a²+b²)Re(u)-ab(1+|u|²)<0`.
Any additional denominator factors have their zero at `-a/b<0`.
Thus the construction really perturbs into the strict left half-plane.
Final rational acceptance remains independent of this derivation.

`verify_record.py` independently reads the rational arrays and verifies:

- nonzero polynomials and actual degree x >= degree y;
- original identity by a rational coefficient stencil and again in QQ[s];
- all exact Hurwitz determinants positive;
- independent Fraction Routh first-column entries positive;
- pairwise exact gcd degrees and leading coefficients.

Routh rows use positive integer rescaling, with rational scales reconstructing
the classical first column exactly. Coprimality may be proved by a finite-field
gcd with both leading degrees preserved, over an explicitly trial-division
verified prime; otherwise a full QQ gcd is used. The optional local GMP backend
uses only exact mpz/mpq operations. Its entire degree-32 output was compared
with the stdlib output and agreed exactly. `BCP_STDLIB_ONLY=1` selects the
stdlib implementation. Numerical jobs use six worker processes; isolation and
rational witness acceptance remains ordered. From degree 66 onward, the three
polynomial stability checks inside one witness run in separate local processes.
Each receives the immutable coefficient snapshot via stdin, never reopening the
witness path; the parent performs both identity checks and gcd checks on that
same snapshot. The entire degree-60 proof output agreed with the serial version.
`BCP_SERIAL_CERTIFICATES=1` selects serial checking. These changes do not weaken
acceptance.

Coefficient precision initially used the full degree. From degree 58 onward,
the initial proposal instead uses the largest limiting root multiplicity,
including the origin and the extra denominator roots; full-degree and doubled
full-degree precision are automatic fallbacks. This heuristic has no proof
status. Every shorter coefficient array still undergoes all exact checks.
The degree-54 test certified the same rational target using 584 coefficient
digits instead of 1012. The exact-division performance experiment produced
identical evidence but no material speed gain, so ordinary quotient/remainder
checking was retained.

Its saved evidence includes all determinants, all Routh first-column entries,
exact minima, and witness SHA256. The proper controller is c=y/x; the original
BCP definition permits degree equality. The witness has degree p=degree x+2,
with positive leading coefficient, so there is no leading cancellation.

Only successful acceptance of an explicit Q[s] witness can update the incumbent.
Per-degree searches use two increasingly close rational targets (8 and 16
decimal places); the final best configuration receives a further adaptive
precision pass after the search layers have met a stopping condition.
The final pass attempts 24,32,48,64,96,128 decimal places, strengthening the
isolating box as needed. A measured 60-second target per final certificate
controls practical output precision; a passing point is kept even if it takes
longer. This does not trigger route saturation, impose a total search budget,
or claim that the reported rational is the nearest possible one.

Before delivery, five adversarial checker cases are exercised: a one-integer
identity error, a wrong target, a zero leading coefficient, an unstable cubic
with all positive coefficients, and stable x/y whose identity-defined p is
unstable. All must be rejected. These are supplemental checks, not substitutes
for the exact algebraic criteria.

## Stopping audit

Any automatic stopping label is independently checked from layer certificates
before delivery. In particular, absence of an isolated root is NOT treated as
evidence of a small quasi improvement. The tiny-improvement criterion requires
isolated roots in three successive layers and uses rigorous interval endpoints.
If that condition is unavailable, four successive degrees without a certified
improvement must be completed. No fixed maximum degree is imposed.

From the second partial resume of degree 68, a single high-precision Newton
proposal is limited to 2000 residual evaluations. Exhaustion marks only that
proposal inconclusive; the alternate precision/method and other configurations
remain eligible. It is not evidence of nonexistence, a total resource budget,
or a saturation criterion. Partial-layer resumes reuse saved exact certificates
and completed numerical logs. Improvement counters compare against the previous
completed degrees, including any record already saved in the partial layer.

From degree 70, high-precision residual calls skip construction of the unused
Jacobian. The full derivative circuit remains the default for exact interval
verification. Degree 22, 64, and 68 residual outputs agreed exactly in both
multiprecision and outward-rounded dyadic arithmetic; their existing interval
certificates were replayed successfully (residual_only_review.json).

For the next complete layer after degree 70, mpmath may use the already vetted
local GMP backend. Its residual/Jacobian outputs, refined roots, and integer
interval proof outputs agreed with the Python backend on degrees 22/64/68
(mpmath_backend_review.json). This accelerates candidate generation only;
interval proofs still use Python integer outward rounding. Set MPMATH_NOGMPY=1
to force mpmath's Python backend; BCP_STDLIB_ONLY=1 also avoids the local vendor
path when starting the verifier or producer in a fresh Python process.

At degree 72, direct high-precision parent-growth starts rescued n0085_d72
whose floating-root refinements had failed. Its first direct start passed
180-digit refinement and the exact dyadic contraction verifier. The independently
executed rescue and integrated start selector agreed exactly
(parent_growth_fallback_review.json). From degree 74, a failed primary isolation
tries up to three direct growth starts from retained parents, ordered by scaled
distance to the numerical candidate, at 180/280 digits. These starts have no
proof status: every result must still pass interval isolation and independent
rational witness acceptance. Additional rescued parents are all retained at
checkpoint promotions. Main frontier state saves now use an atomic file replace.
