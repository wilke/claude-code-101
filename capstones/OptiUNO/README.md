# OptiUNO - search for an optimal optimization solver 

UNO [Unifying Nonlinear Optimization](https://github.com/cvanaret/Uno) Uno breaks down these methods into a set of common building blocks that interact with one another, such as constraint reformulation, step computation, and globalization. These strategies can be combined at runtime in various ways, and there are at least 186 possible configurations, but only a small number of these have ever been tried. **Our goal is find an optimal configuration of UNO's strategies.**

## Background

UNO's goal is to provide a single executable that can be changed at run-time to be many Newton-like solvers: interior-point, SQP, with different globalization mechanisms (line-search vs. trust-region), and globalization strategies. No one has explored these different possibilities; instead, we have implemented existing methods as `presets`. It would be interesting to see whether there are combinations that had not been explored that work significantly better for certain classes of problems.


## Possible Project Outline

1. Install [UNO](https://github.com/cvanaret/Uno) in your workspace *(not here :-)*
2. Install [openEvolve](https://github.com/algorithmicsuperintelligence/openevolve).
3. Select a set of test problems, e.g. the Hock-Schittkowski set from [Bob Vanderbei](https://vanderbei.princeton.edu/ampl/nlmodels/index.html).
4. Explore the `run-time-options` that UNO offers: *these are your optimization variables*.
5. What is a good `performance metric`? Total CPU-time, variance in time, iterations ... *this is your objective*.
6. Set up `openEvolve` to find the `run-time-options` that optimize your `performance metric`.
7. If you have multiple performance metrics, how do you address this problem?
8. Beware that some combinations of `run-time-options` do not work at all. How do you catch this?
9. How do the optimal `run-time-options` depend on the problem class?

**Risk Mitigation**: If `openEvolve` fails to *optimize* the `run-time-options`, then we could resort to some form of complete enumeration.


## Possible Research Product

This is not a classical optimizaton paper, but still worth writing up. A possible outline:

1. Methodology (describe the project outline from above).
2. Findings, and interpretation. Are there gaps in the software design/methods?
3. How does this experiment (with UNO) generalize to other solvers?
4. Compare `openEvolve` to complete enumeration both in terms of time and optimal solution.
5. Conclusions and outlook.

*From an idea by Nick Gould, who asked Sven whether he had explored all configurations.*
