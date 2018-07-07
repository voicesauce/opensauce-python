Mac OS X instructions
=====================

Here are some specific instructions on how to setup your Mac OS X machine to
run opensauce-python.

* [Python setup](#python)
* [Snack setup](#snack)
* [REAPER setup](#reaper)

# <A NAME="python">Python setup</A>

You need to install Python 2.7 or 3.4+ and the Python packages
[NumPy](http://www.numpy.org/) and [Scipy](https://www.scipy.org/).  There are
several ways to do this.

1.  Mac OS X comes with Python 2.7 pre-installed. If you choose to use this
    pre-installed Python, you only need to install Numpy and Scipy.

    The standard way to install these packages is using the
    [Python package manager pip](https://packaging.python.org/installing/):

        $ python -m pip install --upgrade pip
        $ pip install --user numpy scipy

2.  You can use the Homebrew package manager.  Follow the instructions on the
    [Homebrew website](https://brew.sh/) to install it.  Then run

        $ brew doctor

    to see how you can configure your system so that Homebrew is in your path.
    For example, you can add the line `export PATH="/usr/local/bin:$PATH"` to
    your `.bash_profile`.

    If you want Python 2, do

        $ brew install python
        $ brew upgrade python
        $ brew install python@2
        $ pip2 install --upgrade pip setuptools virtualenv
        $ virtualenv osvenv -p python2 # create virtualenv
        $ source osvenv/bin/activate # activate virtualenv
        $ pip2 install numpy scipy

    If you want to install the Python 3 versions, use

        $ brew install python
        $ brew upgrade python
        $ brew install python@2
        $ pip3 install --upgrade pip setuptools virtualenv
        $ virtualenv osvenv -p python3 # create virtualenv
        $ source osvenv/bin/activate # activate virtualenv
        $ pip3 install numpy scipy

    In the above, we suggest using virtual environments as this is standard
    practice. To learn more about Python virtual environments, see the
    [virtualenv documentation](https://virtualenv.pypa.io/en/stable/).

    (Note that Homebrew now uses Python 3 as the default, so you need to
    install both Python 2 and Python 3. Apparently, there are some
    dependencies or linking issues that are resolved by doing this.)

    To run the Homebrew's Python (not the pre-installed version on OS X), use
    `$ python2` or `$ python3` depending on which Python version you want to
    run.

    Now the Homebrew package versions of Python, NumPy, and SciPy are
    installed.

3   You can install the Anaconda distribution of Python.  Follow the
    directions on the [Anaconda website](https://www.continuum.io) and install
    Python.  NumPy and SciPy come pre-installed.

We recommend that you avoid the pre-installed Python (Method 1) and use a
package manager like Homebrew or Anaconda instead.  Installing Anaconda
requires the least amount of technical knowledge, though Homebrew is not too
difficult to learn.

# <A NAME="snack">Snack setup</A>: Run Snack commands through Tcl interpreter

It appears that Mac OS X ships with Tcl/Tk 8.4 by default, and Apple's version
of Tcl/Tk8.4 comes with Snack 2.2

So we can simply run Snack commands through the Tcl interpreter using `tclsh`.

# <A NAME="reaper">REAPER</A> setup

Install [REAPER](https://github.com/google/REAPER) via the
[pyreaper Python package](https://github.com/r9y9/pyreaper), by using the
Python package manager pip.

    $ pip install cython
    $ pip install git+https://github.com/voicesauce/pyreaper

If you are using Homebrew, for Python 2, run

    $ source osenv/bin/activate # activate previous virtualenv, if needed
    $ pip2 install cython
    $ pip2 install git+https://github.com/voicesauce/pyreaper

or for Python 3, run

    $ source osenv/bin/activate # activate previous virtualenv, if needed
    $ pip3 install cython
    $ pip3 install git+https://github.com/voicesauce/pyreaper

    Installing the Python package is easiest, but alternatively, you can
    build the REAPER executable as described in the
    [REAPER README](https://github.com/google/REAPER/README.md)

    We try to maintain pyreaper to stay up-to-date with the official Google
    [REAPER](https://github.com/google/REAPER) repository, but if it's not
    up-to-date, you can build the REAPER executable on the latest code in
    the Google repository.
