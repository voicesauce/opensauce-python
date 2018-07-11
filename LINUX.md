Linux instructions
==================

Here are specific instructions on how to setup your Linux machine to run
opensauce-python.

1.  Install [Python 2.7 or 3.4+](https://www.python.org/), if you don't already
    have it. If your Linux OS has a package manager, it's easiest to install
    the Python via the package manager. For example, to install Python 3 on
    Ubuntu,

        $ sudo apt-get install python3

    Also, be sure to install [pip](https://pip.pypa.io/en/stable/installing/)
    and [virtualenv](https://virtualenv.pypa.io/en/stable/).

2.  Install the Python packages [NumPy](http://www.numpy.org/) and
    [SciPy](https://www.scipy.org/).

    The standard way to install these packages is using the
    [Python package manager pip](https://packaging.python.org/installing/):

        $ python -m pip install --upgrade pip virtualenv
        $ virtualenv osenv -p python
        $ source osenv/bin/activate
        $ pip install --user numpy scipy

    (You may need to substitute `python2` or `python3` for `python` and `pip2`
    or `pip3` for `pip`, depending on which version of Python you want to use
    and which Linux distribution you are using.)

    In the above, we suggest using virtual environments as this is standard
    practice. The command `virtualenv osenv -p python` creates a new virtual
    environment named `osenv`. The command `source osenv/bin/activate`
    activates the virtual environment, so that when you install `numpy` and
    `scipy` in the next command, these packages are installed into the virtual
    environment. To exit the virtual environment, run `deactivate` on the
    command line.

    To learn more about Python virtual environments, see the
    [virtualenv documentation](https://virtualenv.pypa.io/en/stable/).

    Debian / Ubuntu users might prefer to install NumPy and SciPy system-wide
    via their package manager.

        $ sudo apt-get install python-numpy python-scipy

    However, the system-wide packages are usually not up-to-date. Installing
    Python packages using pip gives you the latest versions.

    (For Python 3, instead use `python3-numpy` and `python3-scipy`.  You may
    also need to install the package `python3-tk`.)

    If you have trouble, look at the
    [SciPy documentation](https://www.scipy.org/install.html).

3.  Install Tcl/Tk and Snack Sound Toolkit

    If you're on a Debian / Ubuntu machine, install the relevant packages using
    these commands:

        $ sudo apt-get install tk8.4
        $ sudo apt-get install tcl-snack

    This will install both Tcl/Tk version 8.4 and Snack 2.2.

    Sometimes, Tcl/Tk is already installed.  If not, you may need to install
    Tcl/Tk using the package manager.  Many Linux distributions allow you to
    install Snack from their package repository, including distributions based
    on Fedora and Arch.  This is the easiest way to install Snack on Linux.

    Note that the code will probably work with a later versions of Tcl/Tk; it
    has been tested with tk8.4 and tk8.5 on Linux.  Note that on some Linux
    distributions, people report a [bug that prevents Snack from working on Python with Tcl/Tk 8.6](https://bugs.launchpad.net/ubuntu/+source/snack/+bug/1510562).

    If you want to call Snack from Python, you may need to do additional setup.
    To find information about this, search for "Tkinter <name of Linux
    distribution you're using>".  However, we do not currently recommend
    Snack from Python/Tkinter because of
    [#26](https://github.com/voicesauce/opensauce-python/issues/26).

4.  Install REAPER

    Install [REAPER](https://github.com/google/REAPER) via the
    [pyreaper Python package](https://github.com/voicesauce/pyreaper), by using
    the Python package manager pip.

        $ pip install cython
        $ pip install git+https://github.com/voicesauce/pyreaper

    Installing the Python package is easiest, but alternatively, you can
    build the REAPER executable as described in the
    [REAPER README](https://github.com/google/REAPER/README.md)

    We try to maintain pyreaper to stay up-to-date with the official Google
    [REAPER](https://github.com/google/REAPER) repository, but if it's not
    up-to-date, you can build the REAPER executable on the latest code in
    the Google repository.
