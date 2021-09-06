blec: alpha blending calculator
===============================

<!-- cut -->
[![Version](https://img.shields.io/pypi/v/blec.svg)](https://pypi.org/project/blec/)
<!-- end -->
This is a tool to calculate a resulting color of the alpha blending process.
A gamma correction is enabled and the default transfer function is the one defined in sRGB.

Usage
-----
Just enumerate colors from the bottom to the top. Let's blend 75% black on pure white

    blec white black:0.75
    blec fff 000000bf
    blec ffffffff [0,0,0,191]
    blec ffffff:1 [0,0,0]:0.75

Every call above does the same thing

Installation
------------

    pip3 install blec

