Users
=====
If you came here because you wanted to submit an issue, thanks for reading!
We depend on users like you to help us find bugs and suggest enhancements.

If you are planning on submitting an issue on the GitHub issue tracker, please
search first, to make sure the issue has not already been raised.  Other than
that, please feel free to submit an issue regarding any topic including

* Questions about using the software
* Bugs you've found
* Ideas for improvements

Developers
==========

## Workflow

To contribute code, edit, etc:

1. [Install Git](http://git-scm.com/book/en/Getting-Started-Installing-Git) (if
   you haven't already).

2. Install [Git LFS](https://git-lfs.github.com/) for managing large files.

3. Make a GitHub account.

4. Clone the repo:

        $ git clone https://github.com/voicesauce/opensauce-python.git
        $ cd opensauce-python

5. To run unit tests, run the Python standard testing library `unittest` as a
   module on the command line.

   To run all the tests:

        $ python -m unittest test

   To run tests in one test file (for example, the tests in `test_soundfile.py`):

        $ python -m unittest test.test_soundfile

   To run tests in one class of one test file (for example, `TestSoundFile`):

        $ python -m unittest test.test_soundfile.TestSoundFile

   To run a single test in one class of one test file (for example, `test_no_textgrid`):

        $ python -m unittest test.test_soundfile.TestSoundFile.test_no_textgrid

   Following the convention of `unittest`, all tests and test files begin with
   `test_`.

   To see all the available options for running `unittest`, display help:

        $ python -m unittest -h

   Note that in order for the tests that use resampled data to pass, you need
   SciPy version 1.0+.  The resampled test data was generated using SciPy 1.0,
   and previous versions of SciPy generate different resampled values.

6. Write code, edit code, test code.  Ideally, add tests to the set of
   unit tests in the tests directory to cover any new or changed code.
   New tests will be automatically picked up by the test runner if
   (a) any test class subclasses unittest.TestCase and (b) any
   test method name starts with the string 'test_'.

7. Automatically check the Python code you've written by using code checkers.
   To run code checkers on Python code (.py files), use one or more of these
   Python packages:

   * [pycodestyle](https://pypi.python.org/pypi/pycodestyle)
   * [pyflakes](https://pypi.python.org/pypi/pyflakes)
   * [pydocstyle](https://pypi.python.org/pypi/pydocstyle)
   * [pylint](https://www.pylint.org/)

   If you don't have these packages, you need to install them using pip.  Most
   of these packages (pycodestyle, pyflakes, pylint) are also available as
   Anaconda packages.  It's good to start with pycodestyle and pyflakes, which
   work well for basic checking.

   Some examples of how to run the code checkers for pycodestyle and pyflakes:

        $ pycodestyle /path/to/python_file
        $ pyflakes /path/to/python_file

8. To make sure you've written enough tests to cover the code you've written,
   run a coverage check.  You need to install the Python package `coverage`.
   This can be done using pip (`pip install coverage`), or if you are using
   Linux, there may be a system package for it (on Ubuntu, do `sudo apt-get
   install python-coverage` for Python 2 or `sudo apt-get install
   python3-coverage` for Python 3).

   Once you have the Python `coverage` package installed, run the test coverage
   script `run_coverage.sh` if you have a bash shell on your machine, or run
   the following commands:

        $ coverage run -m unittest test
        $ coverage report -m --include=opensauce/*

   This will show you a report of how many lines of code have been covered by
   the unit tests, and which lines have not been covered, for each Python
   module.  For example, you might get a report like this:

        Name                     Stmts   Miss  Cover   Missing
        ------------------------------------------------------
        opensauce/__init__.py        0      0   100%
        opensauce/__main__.py      273     44    84%   28, 62, 132-133, 160, 162-164, 198-199, 206-207, 219-220, 229, 248, 320-335, 359-364, 366, 369-372, 375, 377, 383-388, 639-644
        opensauce/helpers.py        24      0   100%
        opensauce/praat.py          95      5    95%   158, 180, 194, 310, 325
        opensauce/shrp.py          213     14    93%   51, 268, 281-282, 304-306, 318, 322, 333, 449, 457, 483, 487
        opensauce/snack.py         232    125    46%   109, 111, 115, 129-153, 165-212, 232, 260-261, 273, 367, 369, 373, 387-420, 432-483, 504, 526-528, 531-532, 545
        opensauce/soundfile.py      46      4    91%   79-81, 99
        opensauce/textgrid.py      229    115    50%   166-167, 170-173, 193-200, 219-220, 224, 227-230, 241-246, 261-277, 284-306, 349-350, 355, 365-371, 378-383, 400-403, 409-413, 415, 425, 433-439, 446, 453, 460, 463, 466, 470-478, 483-488, 673
        ------------------------------------------------------
        TOTAL                     1112    307    72%

   For instance, we see that for the module `soundfile.py`, 46 lines of code
   were covered by the tests, but 4 lines were not -- which results in 91%
   coverage.  Specifically, the lines numbered 79-81 and 99 were not covered
   by the tests.

   Running coverage requires the Python package coverage to be installed.  See
   the [coverage documentation](https://coverage.readthedocs.io/) for
   installation instructions.  Coverage is also available as a package on
   Anaconda.

9. To track added or changed files, use "git add":

        $ git add path/to/file

   Note that JSON files are managed by Git LFS.  If you add any other type of
   large file, you should use Git LFS to manage it, for example

        $ git lfs track "*.psd"

   if you wanted to add large .psd files.

10. Once you're ready to commit your changes, use "git commit":

        $ git commit

   An editing window will open for the commit message.  Please start it with a
   one line summary of the change, a blank line, and then a paragraph or two
   about the motivation for the change and what the changes are.

11. Push your changes to the cloud (it'll ask for your GitHub username and
    password):

        $ git push

   In order to sync your version of the repo with the master copy, use "git pull":

        $ git pull

   If something breaks or anything is confusing, post a question on the Issue tracker.

## How to do an algorithm conversion

1. In the algorithm's .m file, add a line to the end of the function
   for which the file is named like this:

        save -6 data.mat list-of-variables

   where list-of-variables is the complete list of variables used
   to call the function as well as all the variables it returns.
   (Check to make sure the arguments aren't modified in the body of
   the function; if they are you will have to make copies of the original
   values and save those as well.)

2. Call opensauce-octave such that your algorithm of interest
   gets called.  (XXX: need to flesh this out.)

3. Copy the data.mat file to test/data as <funcname>.mat, where funcname
   is the name of the primary function you are converting.

4. Create a test_funcname.py file, where funcname is the name the function
  will have after conversion (please follows PEP 8 naming conventions).
  See test_shrp.py as an example of how a test file is organized.

5. Add a test to your test_funcname.py file that loads the .mat file using
   the loadmat function from test.support, calls your function, and
   compares the output to the matlab output data from the .mat file.
   See test_shrp.py for examples.  Things to keep in mind:

    * matlab arrays are 1 origined, python's are 0 origined.  This means
      you have to subtract 1 from any values or matries that are indeces.

    * loadmat will always returns floating point values, so any values that
      are actually integers will need to be converted.

6. Create a funcname.py file in the 'opensauce' directory, and put your
   conversion of the matlab code into it.  During conversion pay
   particular attention to the array index origin problem, as this is
   the greatest single source of conversion bugs.

   Note: if the algorithm has sub-functions, you may want to work from the
   simplest of these up, applying steps 1-8 to each function.  See
   test_shrp.py for a good example of this approach.

7. Start debugging.  When you run your test, it will fail.  The first bugs you
   fix will probably be fixing your test code so that it correctly calls the
   function under test, but after that your function code will have bugs as
   well.  Once you get the code to the point where it runs and returns values,
   most likely the values won't match those loaded from the matlab file.  The
   problems may be a need to reformat the matlab data correctly, but most
   likely you will get the wrong values in the returned data.  At this
   point you may want to follow the following procedure:

    * Open up an octave prompt

    * load data.mat

    * copy and paste the first line of the function from the matlab source.
      Observe the value(s) that result(s).

    * In your python conversion, insert a print statement after the
      first line that prints the result of that line.  Run your test.

    * Compare the value printed by your python test run with the value
      computed by octave.  Remember to account for the 1 vs 0 origin
      in comparing index values.

    * Repeat for each successive line until you find the place where your
      program's results are diverging from those produced by octave.

    * Fix the bug

    Continue iterating this procedure until your test passes.

8. Once your code successfully passes the test based on the matlab data,
   you may want to add additional tests using other data sets, or make
   up some input data to make sure all branches of your code execute
   correctly.

9. XXX: A few more steps to come once the runtime framework is fleshed out.

## Check vendored software

There is a script in the main repository that checks where our version of
`opensauce/textgrid.py` matches the one in the nltk repository.  The reason for
the script is to check if there are new changes to the nltk version that should
be incorporated into our version.  If the versions are different, that may be
okay if our version is more recent.  One should check the commit log on the
nltk version to see if there are more recent changes to be pulled into our
version, rather than simply relying on the `check_vendored_software` script.

## Monitor changes in external software

If the tests fail, it's often because there have been changes to external
software (Snack, Praat, REAPER).

* Check Snack is still available as a Debian / Ubuntu package
* Check Snack is still available pre-installed in Mac OS X
* For the continuous integration tests on GitHub, check that the download links
  for Praat point to the latest versions.

In addition:

* Check for updates in the
  [Google REAPER repository](https://github.com/google/REAPER).
* Check for updates in Ryuichi Yamamoto's
  [pyreaper package](https://github.com/r9y9/pyreaper)

We maintain our own pyreaper package, so changes in these repositories don't
affect us, but if there are updates, we may want to incorporate these changes.
New Google REAPER commits can be incorporated by updating the REAPER submodule
in our [pyreaper repository](https://github.com/voicesauce/pyreaper).

## Projects

Check the Issue tracker and TODO.md for ideas.
