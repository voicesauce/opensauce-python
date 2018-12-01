Mac OS X instructions (Homebrew)
================================

Here are some specific instructions on how to setup your Mac OS X machine to
run opensauce-python using the Homebrew package manager.

* [Python setup](#python)
* [REAPER setup](#reaper)
* [Snack setup](#snack)

# <A NAME="python">Python setup</A>

You need to install Python 2.7 or 3.4+ and the Python packages that OpenSauce
depends on.

We describe how to do this using the Homebrew package manager. Follow the
instructions on the [Homebrew website](https://brew.sh/) to install it. Then
run

    $ brew doctor

to see how you can configure your system so that Homebrew is in your path. For
example, you can add the line `export PATH="/usr/local/bin:$PATH"` to your
`.bash_profile`.

If you want Python 2, do

    $ brew install python
    $ brew install python@2
    $ pip2 install --upgrade pip setuptools wheel virtualenv
    $ virtualenv osvenv -p python2
    $ source osvenv/bin/activate
    $ pip2 install numpy scipy

If you want to install the Python 3 versions, use

    $ brew install python
    $ brew install python@2
    $ pip3 install --upgrade pip setuptools wheel virtualenv
    $ virtualenv osvenv -p python3
    $ source osvenv/bin/activate
    $ pip3 install numpy scipy

In the above, we suggest using virtual environments as this is standard
practice. The command beginning with `virtualenv` creates a new virtual
environment named `osenv`. The command beginning with `source` activates the
virtual environment, so that when you install `numpy` and `scipy` in the next
command, these packages are installed into the virtual environment. To exit the
virtual environment, run `deactivate` on the command line.

To learn more about Python virtual environments, see the
[virtualenv documentation](https://virtualenv.pypa.io/en/stable/).

(Note that Homebrew now uses Python 3 as the default, so you need to install
both Python 2 and Python 3. Apparently, there are some dependencies or linking
issues that are resolved by doing this.)

To run the Homebrew's Python (not the pre-installed version on OS X), use
`$ python2` or `$ python3` depending on which Python version you want to run.

Now the Homebrew package versions of Python, NumPy, and SciPy are
installed.

# <A NAME="reaper">REAPER</A> setup

Install [REAPER](https://github.com/google/REAPER) via the
[pyreaper Python package](https://github.com/r9y9/pyreaper), by using the
Python package manager pip.

For Python 2, run

    $ brew install git
    $ source osenv/bin/activate # activate previous virtualenv, if needed
    $ pip2 install cython
    $ pip2 install git+https://github.com/voicesauce/pyreaper

or for Python 3, run

    $ brew install git
    $ source osenv/bin/activate # activate previous virtualenv, if needed
    $ pip3 install cython
    $ pip3 install git+https://github.com/voicesauce/pyreaper

We try to maintain pyreaper to stay up-to-date with the official Google
[REAPER](https://github.com/google/REAPER) repository, but this may not always
be the case. Installing REAPER via the pyreaper Python package is easiest, but
alternatively, you can build the REAPER executable as described in the
[REAPER README](https://github.com/google/REAPER/README.md). Building the
REAPER executable from the official Google repository may be desirable if you
need the latest version of REAPER. In order to build the REAPER executable,
you may need to install `cmake` via Homebrew, i.e. run `brew install cmake`.

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
    for packages in `/System/Library/Tcl/8.5`. **Note: on Mac OS X El Capitan and later, [System Integrity Protection[(https://support.apple.com/en-us/HT204899) is enabled by default and will prevent you from being able to modify anything in the /System directory. You need to first disable it, following instructions [here](https://totalfinder.binaryage.com/sip).**

        $ sudo unzip snack-tcl85.zip -d /System/Library/Tcl/8.5

    Check that Tcl can find the Snack library, by running the Tclsh shell.

        $ tclsh8.5
        % package require snack
        % exit

    When you run the tclsh command package require snack, it should output
    `2.2` if the Snack library has been installed correctly. If instead it
    output `can't find package snack`, then the install failed.
