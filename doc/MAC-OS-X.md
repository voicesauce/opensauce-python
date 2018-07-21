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

However, for Mac OS X High Sierra (Mac OS X 10.13), Tcl/Tk8.4 and Snack 2.2
are
[not installed by default](https://github.com/voicesauce/opensauce-python/issues/33).
