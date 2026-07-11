# BQPD-Cpp - Create a thread-safe C++ version of Roger Fletchers robust QP solver

## Background

BQPD is a `fortran77` solver for quadratic programs of the form

$$ \min_x g^T x + \frac{1}{2} x^T G x, ~~ AL \leq A^T x \leq AU, xL \leq z \leq xU $$

where $g, xL, xU \in R^n$ are constant vectorss, $A \in R^{n \times m}, G \in R^{n\times n}$ are matrices, and $AL, AU \in R^m$ are constant bound vectors.

The solver uses `common` blocks to pass information, which means it is **not threat-safe**. Despite the fact that it is written in `fortran77`, the solver uses *object-oriented-like* ideas to allow any combinations of dense/sparse matrix representation/factorization (see `sparseA.f` and `denseA.f` for example).

**References:**
* R. Fletcher. [Resolving degeneracy in quadratic programming](https://link.springer.com/article/10.1007/BF02023102). Ann Oper Res 46, 307–334 (1993).
* R. Fletcher. [Stable reduced Hessian updates for indefinite quadratic programming](https://link.springer.com/article/10.1007/s101070050113). Math. Program. 87, 251–264 (2000).
* Fortran77 source code for `BQPD` is here [src/](src)

## Goal

Develop a thread-safe `c++` implemenatation of `bqpd` and test it on the examples (`avgasa.s` and `avgasa.d`). As **stretch goal** consider addding BQPD-Cpp to [UNO, our unified nonlinear optimizer](https://github.com/cvanaret/Uno)

## Outline

1. Add the references to the new git repo where you will start youir work as background.
2. Create a `CLAUDE.md` file, and edit it.
3. Add a `plans/` directory.
4. Learn about coding conventions: What parts are double precision, what parts are integers (the code is written in a way to allow a simple switch to single precision by editing only a few lines of code).
5. Make sure you preserve these conding conventions.
6. The subroutines `denseA.f` and `sparseA.f` implement two different representations of the matrix A (and also g).
7. The subroutines `denseL.f` and `sparseF.f` implement dense/sparse factorizations (and work with both As!).
8. The subroutine `gdotx.f` implements a solver-agnostic call-back for Hessian-vector factors $G x$.
9. The goal is to preserve this flexibility, and not let `claude` simplify things.
10. What are copyright issues with code translated by `claude`?
11. Will the new BQPD-CPP work with UNO (and reprduce thhe same resuklts)?

*Sven and others will be working on this project soon.* 
