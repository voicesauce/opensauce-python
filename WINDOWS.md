Windows instructions
====================

Here are specific instructions on how to setup your Windows machine to run
opensauce-python.  On Windows, it is recommended to install Anaconda's Python
distribution, not the release from the official Python organization.

# Recommended setup: Call Snack using binary executable

When opensauce-python is asked to estimate parameters using Snack, it will use
a stand-alone binary executable `snack.exe`.  This allows the user to skip
installing and setting up Tcl/Tk and Snack.

1.  Install [Anaconda](https://www.continuum.io/) and pick the Python version
    you would like, either Python 2.7 or Python 3.6+.  Anaconda comes with the
    NumPy and SciPy packages pre-installed.

    Be sure to select the option to make Anaconda your default Python by
    setting the system environment variables accordingly.  (This option is
    selected by default.)

2.  From your Windows start menu, search for "Anaconda Prompt" and run this
    program.  You should see a command line prompt, where you can now run
    commands like `> python -m opensauce -h`

# Alternate setup: Allows Snack to be called from Python

If you want to setup your machine so that opensauce-python can call Snack from
Python, the steps are more complicated.

1.  Install [Anaconda](https://www.continuum.io/), the 32-bit version.
    Anaconda comes with the NumPy and SciPy packages pre-installed.  Be sure to
    use 32-bit version, even if you have a 64-bit Windows operating system.

2.  Download the latest version of
    [Snack Speech Toolkit](http://www.speech.kth.se/snack/) "Binary release for
    Windows with Python 2.3" and unzip the file.  Read the
    [installation notes for Snack and Python](http://www.speech.kth.se/snack/pyinstall.html).

3.  Open a Windows command prompt and type

        > where anaconda

    to find out where Anaconda is installed. For example, if you installed
    Anaconda for all users, it might be installed at
    `C:\ProgramData\Anaconda2`.

4.  Follow the installation notes for Snack.  Copy `tkSnack.py` to the `Lib`
    directory.  Assuming Anaconda is installed at `C:\ProgramData\Anaconda2`,
    `tkSnack.py` would be copied to `C:\ProgramData\Anaconda2\Lib`.  Copy the
    `snacklib` folder to the `tcl` directory.  Assuming the same Anaconda
    installation directory, `snacklib` would be copied to
    `C:\ProgramData\Anaconda2\tcl`.

    Now Python will be able to find Snack and call its methods.

5.  From your Windows start menu, search for "Anaconda Prompt" and run this
    program.  You should see a command line prompt, where you can now run
    commands like `> python -m opensauce -h`
