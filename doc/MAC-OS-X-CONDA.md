Mac OS X instructions (Anaconda Python)
=======================================

Here are some specific instructions on how to setup your Mac OS X machine to
run opensauce-python using Anaconda Python.

* [Python and REAPER setup](#pythonreaper)
* [Snack setup](#snack)

# <A NAME="pythonreaper">Python and REAPER setup</A>

You need to install Python 2.7 or 3.4+ and the Python packages that OpenSauce
depends on.

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

# <A NAME="snack">Snack setup</A>: Run Snack commands through Tcl interpreter

On many versions of OS X, Tcl/Tk 8.4 and Snack 2.2 are installed by default. If
this is the case, we can simply run Snack commands through the Tcl interpreter
using `tclsh8.4`.

However, for Mac OS X High Sierra (Mac OS X 10.13), Tcl/Tk8.4 and Snack are
[not installed by default](https://github.com/voicesauce/opensauce-python/issues/33).

If Snack is not pre-installed on OS X, there are two solutions.

1.  Compile the Snack Tcl library from source. Follow the instructions for
    building Snack on Mac OS X [here](MAC-OS-X-SNACK.md).

2.  If your Mac OS X operating system has Tcl8.5 pre-installed, you can
    download the Snack Tcl 8.5 binaries which we have pre-built, then place
    the Snack library files in the standard Tcl library directory where Tcl
    looks for packages.

    First, download the
    [Snack Tcl 8.5 zip file](https://github.com/voicesauce/opensauce-python/raw/master/opensauce/mac/snack-tcl85.zip).
    Then unzip the file to the Tcl library directory. On Mac OS X, Tcl8.5 looks
    for packages in `/System/Library/Tcl/8.5`.

        $ sudo unzip snack-tcl85.zip -d /System/Library/Tcl/8.5

    Check that Tcl can find the Snack library, by running the Tclsh shell.

        $ tclsh8.5
        % package require snack
        % exit

    When you run the tclsh command package require snack, it should output
    `2.2` if the Snack library has been installed correctly. If instead it
    output `can't find package snack`, then the install failed.
