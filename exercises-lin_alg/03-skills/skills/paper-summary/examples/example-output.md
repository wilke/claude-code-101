# On the implementation of an interior-point filter line-search algorithm for large-scale nonlinear programming

**Authors:** Andreas Wächter, Lorenz T. Biegler
**Year:** 2006
**Venue:** Mathematical Programming, Series A
**BibTeX key:** wachter-biegler-2006
**DOI / arXiv ID:** 10.1007/s10107-004-0559-y
**Verified via:** semantic-scholar (DOI confirmed; arXiv preprint not found)

## Contribution

Describes the algorithm and software design behind IPOPT, an interior-point method for nonlinear programs that uses a filter mechanism (rather than a merit function) for globalization, plus inertia correction in the linear-system solve to reach second-order points reliably on nonconvex problems.

## Main result

Local and global convergence of the proposed primal-dual interior-point filter line-search algorithm under standard regularity conditions: linear independence constraint qualification, sufficient second-order conditions, and bounded multipliers. *(See §4 for the precise statement; assumptions A1–A4 quoted below.)*

## Assumptions

- "(A1) The functions f, g, h are twice continuously differentiable on an open set containing the iterates."
- "(A2) The iterates lie in a bounded set."
- "(A3) The matrix [∇g; ∇h_active] has full row rank at the limit point."
- "(A4) Strict complementarity holds at the limit point."

## Method / proof sketch

Primal-dual barrier formulation; Newton step on the perturbed KKT system; inertia detection on the augmented matrix to determine whether to add regularization; filter envelope in (constraint violation, objective) space replaces the merit function; second-order corrections to mitigate the Maratos effect.

## Limitations

The paper notes that the global convergence proof requires assumptions stronger than those needed in practice (a common situation for IPM convergence proofs). The implementation accepts much wider problem classes than the theory covers — e.g., problems where strict complementarity fails — but with weaker guarantees.

## Fit to our problem

We use this algorithm as our default NLP solver (decision in LOGBOOK.md, 2026-03-12). The filter line search section §4.2 is the source for our `filter.py` implementation in plans/2026-04-08-filter-linesearch.md. Inertia correction strategy in §3.4 is what we're building on for the inertia-corrected IPM project.

## Pull-quotes

- "The filter algorithm uses two criteria: the constraint violation θ(x) and the objective function f(x)." (p. 30)
- "If the inertia of the iteration matrix [...] is not (n, m, 0), the regularization parameter δ is increased until the correct inertia is achieved." (p. 38)
- "Strict complementarity (A4) is required for the local convergence analysis but is rarely necessary in practice." (p. 42)

## BibTeX

```bibtex
@article{wachter-biegler-2006,
  author  = {W{\"a}chter, Andreas and Biegler, Lorenz T.},
  title   = {On the implementation of an interior-point filter line-search algorithm for large-scale nonlinear programming},
  journal = {Mathematical Programming},
  volume  = {106},
  number  = {1},
  pages   = {25--57},
  year    = {2006},
  doi     = {10.1007/s10107-004-0559-y},
}
```
