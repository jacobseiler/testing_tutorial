#!/usr/bin:env python

import numpy as np
import argparse


def parse_input():
    """
    Parses the command line input arguments.

    Parameters
    ----------

    None.

    Returns
    ----------

    args: Dictionary. Required.
        Dictionary of arguments from the ``argparse`` package.
        Dictionary is keyed by the argument name (e.g., args["seed"]).
    """

    # Taken from
    # https://stackoverflow.com/questions/24180527/argparse-required-arguments-listed-under-optional-arguments
    # Normally `argparse` lists all arguments as 'optional'.  However some of
    # my arguments are required so this hack makes `parser.print_help()`
    # properly show that they are.

    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument("-s", "--seed", dest="seed",
                          help="Seed for the RNG. Default: Random",
                          type=int)

    required.add_argument("-d", "--gen_data", dest="gen_data",
                          help="Generate random data for this run. If not "
                               "specified, then the option 'data_file' " 
                               "must be specified. Default: 1.", default=1,
                          type=int) 

    required.add_argument("-f", "--data_file", dest="data_file",
                          help="File that contains data for this run.  If " 
                               "this isn't specified, we will generate random "
                               "data.  Default: None.", default=None, type=str)

    args = parser.parse_args()
    args = vars(args)

    if (args["gen_data"] == 0) and \
        args["data_file"] is None: 
            print("The code runs using either pre-specified data (data_file = "
                  "'/path/to/file.txt') or generated random data (gen_data = 1). "
                  "Select one of these options.")
            parser.print_help()
            raise RuntimeError

    if args["gen_data"] == 1 and args["data_file"]: 
            print("The code runs using either pre-specified data (data_file = "
                  "'/path/to/file.txt') or generated random data (gen_data = 1). "
                  "Select ONLY ONE of these options.")
            parser.print_help()
            raise RuntimeError

    return args


def get_data(args):

    if args["data_file"]:
        data = np.loadtxt(args["data_file"])
        print("Read {0} entries from {1}".format(len(data), args["data_file"]))

        return data

    else:
        if args["seed"]:
            np.random.seed(args["seed"])

        data = np.random.rand(int(1e6))

        return data


def crunch_data(args, data):


if __name__ == '__main__':
    args = parse_input()

    data = get_data(args)
    crunch_data(args, data)

