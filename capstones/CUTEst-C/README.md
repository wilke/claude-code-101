# CUTEst-C: Create a clean no-dependency C implementation of CUTEst

## Background

CUTEst is the Constrained and Unconstrained Testing Environment with safe threads (CUTEst) for optimization software, see <https://github.com/ralna/CUTEst>. It is the most comprehensive and widely used library of optimization test problems. Problems are specified in SIF format, that are decoded into Fortran code, using the `SIFDecode`.

## Objective

For automatic differentiation (AD) and/or mixed-precision research, it would be very helpful to have a clean, no-dependency C implementation of the CUTEst test problems. the goal of this project is to create a new version of `SIFDecode` that can generate C code from a SIF file.

Installation instructions are here: <https://github.com/ralna/CUTEst/wiki>

## Extensions

There are a number of possible extension or stretch goals:
1. Develop a similar no-dependency Julia implementation (to replace the [CUTEst.jl package](https://github.com/JuliaSmoothOptimizers/CUTEst.jl) that simply calls the internal fortran binaries.
2. Compare the *simplistic* AD of the SIF files (based on group-partial-separability) with modern AD tools using the C interface.

*project proposed by Paul Hovland* 

