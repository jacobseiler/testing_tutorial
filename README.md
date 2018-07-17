[![Build Status](https://travis-ci.org/jacobseiler/testing_tutorial.svg?branch=master)](https://travis-ci.org/jacobseiler/testing_tutorial)

# testing_tutorial

This repository aims to highlight the importance of testing code and provides instructions on setting up automated Travis testing.

# Why Test?

An important question that you should ask yourself is 

> How do I know my code is running correctly? 

Whilst the answer to this question may often be **My code compiles and executes without raising an error** the reality is more subtle than this.  

> How can I be certain that my code, which could be potentially thousands of lines long, runs in an identical manner after **every** commit?

As you may have guessed, the answer is to create a suite of tests wherein you enter known input and check the output is **exactly** what you expect.

# Using This Repo

## Setting Things Up

To fully understand the advantages and breadth of testing, we will want to make our own changes to this repo.  To do so, we must create our own [fork](https://help.github.com/articles/fork-a-repo/).  

Once you have created a fork on your own profile, you'll want to set this repository (i.e., `https://github.com/jacobseiler/testing_tutorial`) as an `upstream` repository of your fork.  This will allow your version of `testing_tutorial` to stay updated and synced with my version of `testing_tutorial`.  This step is covered in-depth in the [fork tutorial](https://help.github.com/articles/fork-a-repo/#keep-your-fork-synced).

Once you have your fork created, cloned onto your local machine and `https://github.com/jacobseiler/testing_tutorial` set as an `upstream` repository, you're good to go! 

## Running the Tests 

This repository contains a small snippet of code (in the `src` directory) that we wish to test.  This snippet performs downsampling in which an input cubic grid (say size `128x128x128`) is downsampled to a smaller grid (say size `64x64x64`) whilst maintaining identical averages over each region.

The code is checked by the `tests.py` file in the `tests` directory.  This file performs two checks:
* Given a grid that contains all values of `1.0`, the output grid should contain all values of `1.0`. This is because the averages within it region is conversed.
* If the input grid is (e.g.,) `128x128x128` and the output grid is requested to be (e.g.,) `64x64x64`, we check that given a grid where every 8th cell contains a value of `8.0`, the output grid should contain all values of `1.0`.  This is because we average over `(128/64)^3=8` cells. 

These checks are run by invoking `python tests.py`.

# Automating Tests

Great, we've now ensured that our code produces the expected output for a specific set on of inputs.  However we want to ensure that any changes we make to the codebase does not break our pipeline.  Whilst we could run the tests every time we make a change, this can become cumbersome.  Furthermore, if we want other people to contribute to our code, we need to ensure that their contributions pass the tests we've outlined.

To achieve this automation we use a practice called **continuous integration (CI)** in which any time commits are pushed to a repository - or pull requests are made - the tests are automatically run.  A swathe of CI services exist but in this tutorial we will focus on [**Travis**](https://travis-ci.com/). 

## Travis

The [Travis documentation page](https://docs.travis-ci.com/user/getting-started/) contains the essentials for getting started and will do a much better job than me of telling you exactly what to do. 

The biggest step is adding the `.travis.yml` file to the repo. This file tells
Travis exactly what to do when building your repo and specifies what Operating
System, compiler etc to use. 

The `.travis.yml` file can be split up into a few major sections. 

### include

This section describes the OS, compilers etc that you want to test your code
on.   Focus on the specifications you want to support.  For example, this
repository code works for both Python2 and Python3. 

### install

In this Section you will install all your modules and requirements you need to
execute your code.  Of particular importance is the file `requirements.txt`
which lists all the Python packages that will need to be installed via `pip`.

### script

The code the build needs to execute!  For this repo all the testing flow is
kept internal to `tests.py` so all we need to execute is this file.

---

Once Travis has been activated and linked to your Github, a `.travis.yml` is
located in your repository, Travis will execute every time you push to this
repo.  The settings under the `notifcations` section in the `.travis.yml` file
will dictate how you are notified of the outcome of your build.

Whenever you make a pull request to a repo that contains CI, the tests will be
run *on your branch* and also *on the expected merged branch*.  The outcome of
the tests will be listed on the pull request, this way the repo maintainer can
request updates before they accept the pull.
