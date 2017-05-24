Linux instructions
==================

Here are specific instructions on how to setup your Linux machine to run
opensauce-python.

1.  Install Python 2.7, if you don't already have it.

2.  Install the Python packages NumPy and SciPy.

    The standard way to install these packages is using the Python package
    manager pip:

        $ python -m pip install --upgrade pip
        $ pip install --user numpy scipy

    (Advanced users might want to install the NumPy and SciPy packages in a
    [virtualenv](https://virtualenv.pypa.io).)

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

    Note that the code will probably work with a later versions of tk; it has
    been tested with tk8.4 and tk8.5 on Linux.
