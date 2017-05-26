Linux instructions
==================

Here are specific instructions on how to setup your Linux machine to run
opensauce-python.

1.  Install [Python 2.7](https://www.python.org/), if you don't already have
    it.

2.  Install the Python packages [NumPy](http://www.numpy.org/) and
    [SciPy](https://www.scipy.org/).

    The standard way to install these packages is using the
    [Python package manager pip](https://packaging.python.org/installing/):

        $ python -m pip install --upgrade pip
        $ pip install --user numpy scipy

    Debian / Ubuntu users might prefer to install NumPy and SciPy system-wide
    via their package manager:

        $ sudo apt-get install python-numpy python-scipy

    If you have trouble, look at the
    [SciPy documentation](https://www.scipy.org/install.html).

3.  Install Snack Sound Toolkit

    If you're on a Debian / Ubuntu machine, install the relevant packages using
    these commands:

        $ sudo apt-get install tk8.4
        $ sudo apt-get install libsnack2

    This will install both Tcl/Tk version 8.4 and Snack 2.2.

    Note that the code will probably work with a later versions of Tcl/Tk; it has
    been tested with tk8.4 and tk8.5 on Linux.
