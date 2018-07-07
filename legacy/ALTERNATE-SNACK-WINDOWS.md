# <A NAME="exe">Alternate Snack setup</A>: Call Snack using binary executable

When opensauce-python is asked to estimate parameters using Snack, it can use
a stand-alone binary executable `snack.exe`.  This allows the user to skip
installing and setting up Tcl/Tk and Snack.

*Note: Currently, we don't recommend using the binary executable.  For
details, see
[#27](https://github.com/voicesauce/opensauce-python/issues/27).*

1.  Install [Anaconda](https://www.continuum.io/) and pick the Python version
    you would like, either Python 2.7 or Python 3.4+.  Anaconda comes with the
    NumPy and SciPy packages pre-installed.

    Be sure to select the option to make Anaconda your default Python by
    setting the system environment variables accordingly.  (This option is
    selected by default.)

2.  From your Windows start menu, search for "Anaconda Prompt" and run this
    program.  You should see a command line prompt, where you can now run
    commands like `> python -m opensauce -h`

