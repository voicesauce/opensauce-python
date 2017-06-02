# Workflow

To contribute code, edit, etc:

1. [Install Git](http://git-scm.com/book/en/Getting-Started-Installing-Git) (if
   you haven't already)

2. Make a GitHub account

3. Clone the repo:

        $ git clone https://github.com/voicesauce/opensauce-python.git
        $ cd opensauce-python

4. To run unit tests, run the Python standard testing library `unittest` as a
   module on the command line.

   To run all the tests:

        $ python -m unittest test

   To run tests in one test file (for example, the tests in `test_cli.py`):

        $ python -m unittest test.test_cli

   To run tests in one class of one test file (for example, `TestCLI`):

        $ python -m unittest test.test_cli.TestCLI

   To run a single test in one class of one test file (for example, `test_m`):

        $ python -m unittest test.test_cli.TestCLI.test_m

   Following the convention of `unittest`, all tests and test files begin with
   `test_`.

   To see all the available options for running `unittest`, display help:

        $ python -m unittest -h

5. To run code checkers on Python code (.py files), use one or more of these
   Python packages:

        * [pycodestyle](https://pypi.python.org/pypi/pycodestyle)
        * [pyflakes](https://pypi.python.org/pypi/pyflakes)
        * [pydocstyle](https://pypi.python.org/pypi/pydocstyle)
        * [pylint](https://www.pylint.org/)

   If you don't have these packages, you need to install them using pip.  It's
   good to start with pycodestyle and pyflakes, which work well for basic checking.

   Some examples of how to run the code checkers for pycodestyle and pyflakes:

        $ pycodestyle /path/to/python_file
        $ pyflakes /path/to/python_file

6. Write code, edit code, test code.  Ideally, add tests to the set of
   unit tests in the tests directory to cover any new or changed code.
   New tests will be automatically picked up by the test runner if
   (a) any test class subclasses unittest.TestCase and (b) any
   test method name starts with the string 'test_'.

7. To track added or changed files, use "git add":

        $ git add path/to/file

8. Once you're ready to commit your changes, use "git commit":

        $ git commit

   An editing window will open for the commit message.  Please start it with a
   one line summary of the change, a blank line, and then a paragraph or two
   about the motivation for the change and what the changes are.

9. Push your changes to the cloud (it'll ask for your GitHub username and
   password):

        $ git push

   In order to sync your version of the repo with the master copy, use "git pull":

        $ git pull

   If something breaks or anything is confusing, post a question on the Issue tracker.

# How to do an algorithm conversion

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

# Check vendored software

There is a script in the main repository that checks where our version of
`opensauce/textgrid.py` matches the one in the nltk repository.  The reason for
the script is to check if there are new changes to the nltk version that should
be incorporated into our version.  If the versions are different, that may be
okay if our version is more recent.  One should check the commit log on the
nltk version to see if there are more recent changes to be pulled into our
version, rather than simply relying on the `check_vendored_software` script.

# Projects

Check the Issue tracker and TODO.md for ideas.


