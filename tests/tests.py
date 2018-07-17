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


def unit_tests(grid, expected_gridsize, expected_datatype=np.float64):
    """
    Tests some fundamental properties of the grids output by `subsample`.

    Parameters
    ----------

    grid : `~numpy.ndarray`
        The 3D downsampled array created by `subsample`. 
    
    expected_gridsize : int, optional
        The expected 1D size of output grid.  Default : 128 and 64.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid is not in the expected shape specified when
        `subample` was called.
        Raised if any values in the output grid are not `np.float64` types. 
    """

    # Check that the grid is cubic with the expected gridsize.
    if not grid.shape == (expected_gridsize, 
                          expected_gridsize,
                          expected_gridsize):
        print("The output grid shape was expected to be ({0}, {0}, {0})" \
              .format(expected_gridsize))
        print("However the shape was {0}".format(grid.shape))
        raise RuntimeError

    # Check that every element is of the expected datatype.
    for (i, j, k) in itertools.product(range(expected_gridsize),
                                       range(expected_gridsize),
                                       range(expected_gridsize)):
        if not type(grid[i,j,k]) == expected_datatype: 
            print("The input data format was a `{4}`.  The output " 
                  "data type should be identical however for element " 
                  "({0},{1},{2}) it was {3}".format(i,j,k,type(grid[i,j,k]),
                    expected_datatype)) 
            raise RuntimeError


def test_homogenous_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing a homogenous input grid will produce a homogenous
    output.

    The test will fail if the output grid is not homogenously filled with
    values of 1.0.

    We also run a suite of unit tests (see `unit_tests` function) that will
    return a RuntimeError if they're not passed.

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
    """

    input_grid = np.ones((input_gridsize, input_gridsize, input_gridsize),
                         dtype=np.float64)
    output_grid = subsample.subsample_grid(input_grid, output_gridsize)

    w = np.where((output_grid <= 0.99999) & (output_grid >= 1.00001))[0]

    if len(w) > 0:
        print("We tested a homogenous input grid with every cell containing a "
              "value of 1.0. We expected the output grid to contain values of "
              "1.0 as well.")
        print("However cells {0} had values {1}".format(w, output_grid[w]))
        raise RuntimeError

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)


def test_multiple_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing an input grid where every input_gridsize/output_gridsize
    cell is filled will a value of (input_gridsize/output_gridsize)^3 produces
    a grid that is homogenously filled with values of 1.0. 

    The test will fail if the output grid is not homogenously filled with
    values of 1.0. 

    We also run a suite of unit tests (see `unit_tests` function) that will
    return a RuntimeError if they're not passed.

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

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)



def test_random(save_output=False):
    """

    Parameters
    ----------

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
    """

    # These parameters have been hardcoded to match the specs of the known grid
    # we're testing against.
    # If you want to test different parameters, set `save_output` to True.
    input_gridsize=128
    output_gridsize=64
    seed=12

    np.random.seed(seed)

    input_grid = np.random.rand(input_gridsize,
                                input_gridsize,
                                input_gridsize)

    output_grid = subsample.subsample_grid(input_grid, output_gridsize)

    known_grid_name = "{0}/known_grid_in{1}_out{2}_seed{3}.npz" \
                      .format(test_dir, input_gridsize, output_gridsize, seed)
    if save_output: 
        np.savez(known_grid_name, output_grid)

    known_grid = (np.load(known_grid_name))["arr_0"]
    known_grid.shape = (output_gridsize, output_gridsize, output_gridsize)

    w = np.where(abs(known_grid - output_grid) > 1e-6)[0]

    if len(w) > 0:
        print("We compared an input grid with randomly generated data with "
              "random seed {0}.  Reading the known input grid ({1}), we had "
              "cells that contained different values.".format(seed,
              known_grid_name))
        print("These were cells {0} with difference {1}".format(w,
              known_grid-output_grid[w]))
        raise RuntimeError

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)


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
    print("Testing a randomly generated grid with known seed.")
    test_random()

    print("")
    print("=================================")
    print("All tests passed!")
    print("=================================")


if __name__ == '__main__':

    run_tests()

    innocuous_variable = 1
