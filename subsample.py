#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import argparse
import os
from scipy import ndimage
import itertools


def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input or output grid specified a ValueError will
    be raised.

    The only accepted arguments for `precision` is "float" or "double"; any
    other input (including no input at all) will raise a ValueError. 

    If the size of the input grid is less than the size of the output grid a
    ValueError will be raised. This is a subsampler.

    If the size of the output grid is not a multiple of the input grid a
    ValueError will be raised.

    Parameters
    ----------

    None.

    Returns
    ----------

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package.
        Dictionary is keyed by the argument name (e.g., args['fname_in']).
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--fname_in", dest="fname_in",
                        help="Path to the input grid file. Required.")
    parser.add_argument("-o", "--fname_out", dest="fname_out",
                        help="Path to the output grid file. Required.")
    parser.add_argument("-p", "--precision", dest="precision",
                        help="Precision for the grids. Accepted values are "
                             "'float' and 'double'. Required.")
    parser.add_argument("-s", "--gridsize_in", dest="gridsize_in",
                        help="Size of the grid (i.e., number of cells per "
                             "dimension) of input grid. Required.",
                        type = int)

    parser.add_argument("-d", "--gridsize_out", dest="gridsize_out",
                        help="Size of the grid (i.e., number of cells per "
                             "dimension) of output grid. Required.",
                        type=int)

    args = parser.parse_args()

    # We require an input file and an output one.
    if args.fname_in is None or args.fname_out is None:
        print("Both an input and output filepath is required.")
        parser.print_help()
        raise ValueError 

    # Check a valid precision was entered.
    if args.precision == "float" or args.precision == "double":
        pass
    else: 
        print("The only accepted precision options are 'float' or 'double' "
              "(don't use apostrophes).") 
        parser.print_help()
        raise ValueError 

    # Check there was two gridsizes specified.
    if args.gridsize_in is None or args.gridsize_out is None:
        print("Both an input and ouput gridsize is required.")
        parser.print_help()
        raise ValueError 

    # Then check the gridsizes are valid.
    if args.gridsize_in < args.gridsize_out:
        print("This is a subsampler, the output grid must have a smaller "
              "gridsize than the input grid.")
        raise ValueError 

    if args.gridsize_in % args.gridsize_out != 0:
        print("The size of the output grid must be a multiple of the input "
              "grid.")
        raise ValueError

    # Print some useful startup info. #
    print("")
    print("======================================")
    print("Input grid: {0}".format(args.fname_in))
    print("Output grid: {0}".format(args.fname_out))
    print("Input gridsize: {0}".format(args.gridsize_in))
    print("Output gridsize: {0}".format(args.gridsize_out))
    print("Precision: {0}".format(args.precision))
    print("======================================")
    print("")

    return vars(args)


def read_grid(filepath, gridsize, precision):
    """
    Reads in a cartesian binary grid. 

    The read grid can be in either int, float or double precision.  If a
    different datatype is specified a ValueError will be raised. 

    If the size of the input grid does not match the expect value (i.e., the
    precision * cube(gridsize)) a RuntimeError will be raised.

    Note: This function only handles 3D Cartesian grids with the same number of
    cells in each dimension.

    Parameters
    ----------

    filepath: String. Required.
        Location of the grid to be read.

    gridsize: int. Required.
        Number of cells along one dimension of the grid to be read in.  

    precision: String. Required.
        Dictates what the precision of the input grid is.  Only reading of
        ints, floats or doubles is currently supported.  Any other datatype
        will raise a ValueError. 

    Returns
    ----------

    grid: A 3D array with shape (gridsize, gridsize, gridsize).
        The read binary grid. 
    """

    # Parse the input precision.
    if precision == "int":
        byte_size = 4
        precision_dtype = np.int32
    elif precision == "float":
        byte_size = 4
        precision_dtype = np.float32
    elif precision == "double":
        byte_size = 8
        precision_dtype = np.float64
    else:
        print("The input precision type for reading the grid was {0}" \
              .format(precision))
        print("Currently I only support reading of ints, floats or doubles.")
        raise ValueError
   
    # Check the size of the input grid to ensure it's correct. 
    filesize = os.stat(filepath).st_size
    if(pow(gridsize, 3.0) * byte_size != filesize):
        print("The size of the input grid is {0} bytes whereas we expected it "
              "to be {1} (for a grid of size {2}^3 with {3} precision)" \
               .format(filesize, pow(gridsize, 3.0) * byte_size, gridsize,
                       precision) )
        raise RuntimeError 
  
    # Everything's good, open the file and reshape the 1D grid. 
    fd = open(filepath, 'rb')
    grid = np.fromfile(fd, count = gridsize**3, dtype = precision_dtype)

    grid.shape = (gridsize, gridsize, gridsize)
    fd.close()

    return grid


def subsample_grid(input_grid, output_gridsize):
    """
    Takes an input grid and subsamples it to a smaller grid size.

    If we were moving from 256^3 grid to a 128^3 grid, then my definition of
    'subsampling' is to split the 256^3 into discrete (non-overlapping) regions
    of 2x2x2 cubes and then take their average.  The average of each 2x2x2 cube
    would then give each new element of the 128^3 grid. 

    Parameters
    ----------

    input_grid : `~numpy.ndarray`
        The 3D data array we will be subsampling from.

    output_gridsize : int
        The size of the grid we're subsampling to.  Must be an integer multiple
        of the `input_grid` shape. 

    Returns
    ----------

    output_grid : `~numpy.ndarray`
        The subsampled grid.


    Errors 
    ----------

    RuntimeError 
        Raised if the dimensions of the input grid are not equal.
        Raised if the requested dimensions of the output grid is not an integer
        multiple of the `input_grid` shape. 

    """

    input_gridsize = input_grid.shape[0]

    if not input_grid.shape == (input_gridsize,
                                input_gridsize, 
                                input_gridsize):
        print("The dimensions of the input grid must be cubic (i.e., all "
              "equal). The shape of the input grid is "
              "{0}.".format(input_grid.shape)) 
        raise RuntimeError

    if not output_gridsize % input_gridsize == 0:
        print("The input grid has gridsize {0} and the requested output grid "
              "has gridsize {1}. These must be an integer multiple of each "
              "other.".format(input_gridsize, output_gridsize))
        raise RuntimeError 

    conversion = int(input_gridsize / output_gridsize) 

    footprint = np.ones((conversion, conversion, conversion))

    # First generate a grid that contains the sliding sum of the original
    # density.
    new_density = ndimage.convolve(input_grid, footprint, mode='wrap')  

    # Now since we want our new cells to be the discrete average (i.e., no
    # overlaps), we will only use every ``conversion`` cells.

    print("Convolution done, now reading the correct cells and normalizing.")
    final_new_density = np.zeros((output_gridsize, output_gridsize,
                                  output_gridsize))

    for (i, j, k) in itertools.product(range(output_gridsize),
                                       range(output_gridsize),
                                       range(output_gridsize)): 
        final_new_density[i, j, k] = new_density[i * conversion, 
                                                 j * conversion, 
                                                 k * conversion] \
                                                / pow(conversion,3.0)
   
    return final_new_density
 
   
if __name__ == '__main__':

    args = parse_inputs()

    input_grid = read_grid(args["fname_in"], args["gridsize_in"],
                           args["precision"])
 
    print("Input grid read, now convolving with the footprint.")
    output_grid = subsample_grid(input_grid, args["gridsize_in"], 
                                 args["gridsize_out"])

    final_new_density.tofile(args["fname_out"])
    print("Subsampled grid saved to {0}".format(args["fname_out"]))
