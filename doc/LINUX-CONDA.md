Linux instructions (Anaconda Python)
====================================

Here are specific instructions on how to setup your Linux machine to run
opensauce-python using the Anaconda distribution of Python.

1.  Install Anaconda Python 2.7 or 3.x. Follow the
    [instructions on the Conda website](https://conda.io/docs/user-guide/install/download.html).
    Either Anaconda or Miniconda will work. Install the one that
    [suits your needs](https://conda.io/docs/user-guide/install/download.html#anaconda-or-miniconda).

2.  Create a virtual environment for the Python packages you will be
    installing in order to run OpenSauce.

        $ conda create --name opensauce_env
        $ source activate opensauce_env

    We suggest using virtual environments as this is standard practice. The
    command `conda create --name opensauce_env` creates a new virtual
    environment named `opensauce_env`. The command
    `source activate opensauce_env` activates the virtual environment, so that
    when you install the NumPy and SciPy packages in the next step, these
    packages are installed into the virtual environment. To exit the virtual
    environment, run `source deactivate` on the command line.

    To learn more about Python virtual environments, see the
    [Conda documentation](https://conda.io/docs/user-guide/tasks/manage-environments.html).

3.  Install the Python packages [NumPy](http://www.numpy.org/) and
    [SciPy](https://www.scipy.org/) into your virtual environment using the
    Conda package manager.

        $ conda install numpy scipy

4.  Install REAPER

    First, install the `Cython` Python package (a dependency needed to compile
    C++ code for REAPER) and also the `git` and `pip` packages, which are
    needed to install a Python package from a Git repository.

        $ conda install cython git pip

    Now install [REAPER](https://github.com/google/REAPER) via the
    [pyreaper Python package](https://github.com/voicesauce/pyreaper), by using
    the Python package manager pip.

        $ pip install git+https://github.com/voicesauce/pyreaper

    To check that all the Python packages (NumPy, SciPy, pyreaper) have been
    installed, you can list all the packages that have been installed in the
    environment.

        $ conda list

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
