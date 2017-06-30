Mac OS X instructions
=====================

Here are some specific instructions on how to setup your Mac OS X machine to
run opensauce-python.

# Recommended setup: Run Snack commands through Tcl interpreter

It appears that Mac OS X ships with Tcl/Tk 8.4 by default, and Apple's version
of Tcl/Tk8.4 comes with Snack 2.2

So we can simply run Snack commands through the Tcl interpreter using `tclsh`.

Then it only remains to install Python 2.7 or 3.6+ and the Python packages
[NumPy](http://www.numpy.org/) and [Scipy](https://www.scipy.org/).  There are
several ways to do this.

*   Mac OS X comes with Python 2.7 pre-installed. If you choose to use this
    pre-installed Python, you only need to install Numpy and Scipy.

    The standard way to install these packages is using the
    [Python package manager pip](https://packaging.python.org/installing/):

        $ python -m pip install --upgrade pip
        $ pip install --user numpy scipy

*   You can use the Homebrew package manager.  Follow the instructions on the
    [Homebrew website](https://brew.sh/) to install it.  Then run

        $ brew doctor

    to see how you can configure your system so that Homebrew is in your path.
    For example, you can add the line `export PATH="/usr/local/bin:$PATH"` to
    your `.bash_profile`.

    Then install Python 2.7, NumPy, and Scipy using

        $ brew install python numpy scipy

    If you want to install the Python 3 versions, use

        $ brew install python3
        $ brew install numpy --with-python3
        $ brew install matplotlib --with-python3

    Now the Homebrew package versions of Python, NumPy, and SciPy are
    installed.

*   You can install the Anaconda distribution of Python.  Follow the
    directions on the [Anaconda website](https://www.continuum.io) and install
    Python.  NumPy and SciPy come pre-installed.

If you only want to play with the software and don't use Python very often,
using the pre-installed Python (Method 1) might be appropriate.  If you use
Python frequently, a package manager like Homebrew or Conda (Anaconda) is
recommended.  Installing Anaconda requires the least amount of technical
knowledge.

# Alternate setup: Allows Snack to be called from Python

If you want to setup your machine so that opensauce-python can call Snack from
Python, the steps are more complicated.  Thanks to Shinya Fujie for this
[guide on setting up Mac machines to run Snack in Python](http://qiita.com/fujie/items/afa463275a5e581667e9).

1.  Install the Homebrew package manager.  Follow the instructions on the
    [Homebrew website](https://brew.sh/) to install it.  Then run

        $ brew doctor

    to see how you can configure your system so that Homebrew is in your path.
    For example, you can add the line `export PATH="/usr/local/bin:$PATH"` to
    your `.bash_profile`.

2.  Install Tcl/Tk with Homebrew.

        $ brew install tcl-tk

3.  Install Python and link it to the Tcl-tk package you just installed by
    running the command

        $ brew install python --with-brewed-tk

4.  Install the Homebrew packages for Numpy and Scipy.

        $ brew install numpy scipy

5.  Download the [Snack Sound Toolkit](http://www.speech.kth.se/snack/).  Get
    the Snack 2.2.10 "Source release for all platforms"
    [version](http://www.speech.kth.se/snack/dist/snack2.2.10.tar.gz) and
    extract the archive.

6.  We need to change one line of the source code, to ensure that Snack will
    compile.  Go into the `generic` directory of the archive and open the file
    `jkCanvSpeg.c`.  Navigate to line 39 `#ifndef Solaris`.  On the following
    line, change the code

        #  ifndef TkPutImage

    to

        #  if 0

7.  Now compile Snack with the Tcl/Tk Homebrew package by running the following
    commands.

        $ ./configure --with-tcl=/usr/local/opt/tcl-tk/lib --with-tk=/usr/local/opt/tcl-tk/lib LDFLAGS=-L/usr/local/opt/tcl-tk/lib CPPFLAGS=-I/usr/local/opt/tcl-tk/include --disable-stubs
        $ make
        $ make DESTDIR=/usr/local/opt/tcl-tk install

    If the compilation fails because of a sed error, try adding the following
    lines to your `.bash_profile`:

        export LC_CTYPE=C
        export LANG=C

    This solution comes from this [StackOverflow answer](https://stackoverflow.com/questions/19242275/re-error-illegal-byte-sequence-on-mac-os-x).
