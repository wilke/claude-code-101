# Capstone Project: diffBLAS activity contexts

## Purpose

To enable on-the-fly adaptation of a library providing differentiated BLAS routines to be used in different automatic differentiation activity contexts.

## Background

- **Key Reference:** Laurent Hascoët, Matt Menickelly, Sri Hari Krishna Narayanan, Jared O’Neal, Nicolas Schunck, Stefan M. Wild. "HFBTHO-AD: Differentiation of a nuclear energy density functional code". Computer Physics Communications, Volume 320, 2026. [doi:10.1016/j.cpc.2025.109955](https://doi.org/10.1016/j.cpc.2025.109955).
- **Related Work:**
  - [diffBLAS](https://github.com/Reference-LAPACK/diffblas)
  - Jonasson, Kristjan and Sigurdsson, Sven and Yngvason, Hordur Freyr and Ragnarsson, Petur Orri and Melsted, Pall. "Algorithm 1005: Fortran Subroutines for Reverse Mode Algorithmic Differentiation of BLAS Matrix Operations". ACM Trans. Math. Softw., Volume 46. [doi:10.1145/3382191](https://doi.org/10.1145/3382191). 2020.
  - [Tapenade](https://tapenade.gitlabpages.inria.fr/userdoc/build/html/tapenade/tutorial.html)

## Problem Statement

`diffblas` is a library that provides (algorithmically) differentiated BLAS routines from their reference implementation in [LAPACK](https://github.com/Reference-LAPACK/lapack) using the automatic differentiation tool [Tapenade](https://gitlab.inria.fr/tapenade/tapenade) in four modes: forward (`_d`), vector forward (`_dv`), reverse (`_b`), and vector reverse (`_bv`).
The compiled `libdiffblas` can be linked into applications that need derivatives of BLAS operations for optimization, sensitivity analysis etc.

For a routine like `DGEMM` diffblas contains `DGEMM_D`. 

```
      SUBROUTINE DGEMM_D(transa, transb, m, n, k, alpha, alphad, a, ad, 
     +                   lda, b, bd, ldb, beta, betad, c, cd, ldc)
```

Here the variables `alpha`, `a`, `b`, `beta`, and `c` are considered to be active and have variables `alphad`, `ad`, `bd`, `betad`, and `cd` respectively associated with them to hold derivative values. 

The problem is that `DGEMM_D` may be called from contexts where only a proper subset of these variables is active, and therefore the provided `DGEMM_D` is not appropriate for correctness and/or performance reasons.


The charge is to generate an approach that can create versions of `DGEMM_D` as needed given an activity pattern.

## Suggested Approaches

### Approach 1: Preprocessor directives 
A preprocessor macro that wraps each statement or declaration such as `_keep_if_active_(010010, stmt)` which, based on a preprocessor-defined activity variable at that moment, either evaluates just to `stmt` or to an empty line. Approach 1 does not require heavy compiler infrastructure.

### Approach 2: Type analysis of an abstract syntax tree
Design a tool that parses the code (for `DGEMM_D`) into an intermediate representation and uses the provided activity descriptor to manage declarations and prune statements in the code. This approach assumes compiler infrastructure.


### Algorithmic Choices 

1. You may find that neither approach is appropriate on its own
2. A different approach or a combination may work

## Outline of Tasks

1. Build and run the basic tests for `diffBLAS`
2. Create an activity context test where the existing approach will fail
3. Explore options to parse and manipulate the Fortran source
4. Create a transformation pass that accepts the activity pattern and appropriately modifies the code.


## Possible Publication Outlets

* [International Conference on Computational Science](https://www.iccs-meeting.org/iccs2026/) ... a venue with workshops that fit AD related publications

*Good Luck!*

