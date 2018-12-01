Linux instructions (Standard Python)
====================================

Here are specific instructions on how to setup your Linux machine to run
opensauce-python, using standard Python.

1.  Install [Python 2.7 or 3.4+](https://www.python.org/), if you don't already
    have it. If your Linux OS has a package manager, it's easiest to install
    the Python via the package manager. For example, to install Python 3 on
    Ubuntu,

        $ sudo apt-get install python3

    Also, be sure to install [pip](https://pip.pypa.io/en/stable/installing/)
    and [virtualenv](https://virtualenv.pypa.io/en/stable/).

2.  Create a virtual environment for the Python packages you will be
    installing in order to run OpenSauce.

        $ python -m pip install --upgrade pip virtualenv
        $ virtualenv opensauce_env -p python
        $ source opensauce_env/bin/activate

    (You may need to substitute `python2` or `python3` for `python` and `pip2`
    or `pip3` for `pip` in the above commands, depending on which version of
    Python you want to use and which Linux distribution you are using.)

    In the above, we suggest using virtual environments as this is standard
    practice. The command `virtualenv opensauce_env -p python` creates a new
    virtual environment named `opensauce_env`. The command
    `source opensauce_env/bin/activate` activates the virtual environment, so
    that when you install `numpy` and `scipy` in the next command, these
    packages are installed into the virtual environment. To exit the virtual
    environment, run `deactivate` on the command line.

    To learn more about Python virtual environments, see the
    [virtualenv documentation](https://virtualenv.pypa.io/en/stable/).

3.  Install the Python packages [NumPy](http://www.numpy.org/) and
    [SciPy](https://www.scipy.org/) into your virtual environment.

        $ pip install numpy scipy

    (You may need to substitute `pip2` or `pip3` for `pip` in the above
    commands, depending on which version of Python you want to use and which
    Linux distribution you are using.)

4.  Install REAPER

    Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
    if you don't already have it. Git is needed, so that we can install REAPER
    from a Git repository.

    Now install [REAPER](https://github.com/google/REAPER) via the
    [pyreaper Python package](https://github.com/voicesauce/pyreaper), by using
    the Python package manager pip and Git.

        $ pip install cython
        $ pip install git+https://github.com/voicesauce/pyreaper

    We try to maintain pyreaper to stay up-to-date with the official Google
    [REAPER](https://github.com/google/REAPER) repository, but this may not
    always be the case. Installing REAPER via the pyreaper Python package is
    easiest, but alternatively, you can build the REAPER executable as
    described in the
    [REAPER README](https://github.com/google/REAPER/README.md). Building the
    REAPER executable from the official Google repository may be desirable if
    you need the latest version of REAPER.

5.  Install Tcl/Tk and Snack Sound Toolkit

    If you're on a Debian / Ubuntu machine, install the relevant packages using
    these commands:

        $ sudo apt-get install tk8.4 tcl8.4
        $ sudo apt-get install tcl-snack

    This will install both Tcl/Tk version 8.4 and Snack 2.2.

    If you are using a different Linux distribution, look for the Tcl/Tk and
    Snack packages for your distribution. We have verified that Tcl/Tk and
    Snack packages are available for Arch based distributions and work
    correctly with OpenSauce.

    Note that the code will probably work with a later versions of Tcl/Tk; it
    has been tested with tk8.4 and tk8.5 on Linux.  Note that on some Linux
    distributions, people report a [bug that prevents Snack from working on Python with Tcl/Tk 8.6](https://bugs.launchpad.net/ubuntu/+source/snack/+bug/1510562).
