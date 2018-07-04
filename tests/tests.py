#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import argparse
import sys
import os
import itertools

try: # Python2
    from urllib import urlretrieve
except ImportError: #Python3
    from urllib.request import urlretrieve
import subprocess

test_dir = os.path.dirname(os.path.realpath(__file__))
script_dir = "{0}/../src/".format(test_dir)
sys.path.append(script_dir)

import subsample


def test_homogenous_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing a homogenous input grid will produce a homogenous
    output.

    The test will fail if the output grid is not homogenously filled with
    values of 1.0 or the output grid is not of the expected shape.

    Parameters
    ----------

    input_gridsize, output_gridsize : int, optional
        1D size of the input/output grids.  Default : 128 and 64.

        ..note::
            `output_gridsize` must be an integer multiple (and smaller) than
            `input_gridsize`.  If not, a `RuntimeError` will be raised by
            `subsample.subsample_grid`.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid contains values that are not within the range
        0.99999 to 1.00001.
        Raised if the output grid is not of the shape (`output_gridsize`,
        `output_gridsize`, `output_gridsize`).
    """

    input_grid = np.ones((input_gridsize, input_gridsize, input_gridsize))
    output_grid = subsample.subsample_grid(input_grid, output_gridsize)    

    w = np.where((output_grid <= 0.99999) & (output_grid >= 1.00001))[0]

    if len(w) > 0:
        print("We tested a homogenous input grid with every cell containing a "
              "value of 1.0. We expected the output grid to contain values of "
              "1.0 as well.")
        print("However cells {0} had values {1}".format(w, output_grid[w]))
        raise RuntimeError

    if not output_grid.shape == (output_gridsize, 
                                 output_gridsize,
                                 output_gridsize):
        print("The output grid shape was expected to be ({0}, {0}, {0})" \
              .format(output_gridsize))
        print("However the shape was {0}".format(output_grid.shape))
        raise RuntimeError
        

def test_multiple_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing an input grid where every input_gridsize/output_gridsize
    cell is filled will a value of (input_gridsize/output_gridsize)^3 produces
    a grid that is homogenously filled with values of 1.0. 

    The test will fail if the output grid is not homogenously filled with
    values of 1.0 or the output grid is not of the expected shape.

    Parameters
    ----------

    input_gridsize, output_gridsize : int, optional
        1D size of the input/output grids.  Default : 128 and 64.

        ..note::
            `output_gridsize` must be an integer multiple (and smaller) than
            `input_gridsize`.  If not, a `RuntimeError` will be raised by
            `subsample.subsample_grid`.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid contains values that are not within the range
        0.99999 to 1.00001.
        Raised if the output grid is not of the shape (`output_gridsize`,
        `output_gridsize`, `output_gridsize`).
    """

    conversion = int(input_gridsize / output_gridsize)
    
    input_grid = np.zeros((input_gridsize, input_gridsize, input_gridsize))

    for (i, j, k) in itertools.product(range(output_gridsize),
                                       range(output_gridsize),
                                       range(output_gridsize)):
        input_grid[i*conversion, j*conversion, k*conversion] = conversion**3 

    output_grid = subsample.subsample_grid(input_grid, output_gridsize)

    w = np.where((output_grid <= 0.99999) & (output_grid >= 1.00001))[0]

    if len(w) > 0:
        print("We tested an input grid with every {0} cell containing a value "
              "of {1}. We expected the output grid to contain values of 1.0 " 
              "as well.".format(conversion, conversion**3)) 
        print("However cells {0} had values {1}".format(w, output_grid[w]))
        raise RuntimeError

    if not output_grid.shape == (output_gridsize, 
                                 output_gridsize,
                                 output_gridsize):
        print("The output grid shape was expected to be ({0}, {0}, {0})" \
              .format(output_gridsize))
        print("However the shape was {0}".format(output_grid.shape))
        raise RuntimeError


def run_tests():
    """
    Wrapper to run all the tests.

    Parameters
    ----------

    None.

    Returns
    ----------

    None.
    """

    print("=================================")
    print("Running tests")
    print("=================================")
    print("")

    print("Testing a homogenous grid input")
    test_homogenous_input()

    print("")
    print("Testing an input where every input_gridsize/output_gridsize cell " 
          "has a value of (input_gridsize/output_gridsize)^3.")
    test_multiple_input()

    print("")
    print("=================================")
    print("All tests passed!")
    print("=================================")


if __name__ == '__main__':

    run_tests()
