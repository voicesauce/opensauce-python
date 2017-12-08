Windows instructions
====================

Here are specific instructions on how to setup your Windows machine to run
opensauce-python.  On Windows, it is recommended to install Anaconda's Python
distribution, not the release from the official Python organization.

* [Recommended Snack setup](#tcl)
* [Alternate Snack setup using Python/Tkinter](#python)
* [Alternate Snack setup using binary executable](#exe)
* [REAPER setup](#reaper)

# <A NAME="tcl">Recommended Snack setup</A>: Call Snack in Tcl shell

1. Install Anaconda as described in the previous section.  Either 32-bit or
   64-bit versions should work.

2. Install ActiveState's [ActiveTcl](https://www.activestate.com/activetcl).
   Be sure to pick the 32-bit version.  The 64-bit version will not work with
   Snack.

3. Download Snack v2.2.10,
   [Binary release for Windows with Tcl/Tk 8.1-8.4](http://www.speech.kth.se/snack/dist/snack2210-tcl.zip)

4. Unzip the file to a folder, and in the resulting folder, double-click on
   `install.tcl`.  This will install Snack.

We have successfully run Snack in Tcl using Active Tcl version 8.5, 32-bit.

# <A NAME="python">Alternate Snack setup</A>: Allows Snack to be called from Python

*Note: Please take a look at
[#26](https://github.com/voicesauce/opensauce-python/issues/26), so you are
aware of the issue involved in using Python's Tkinter library.*

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

# <A NAME="reaper">REAPER setup</A>

1.  Install [Cygwin](https://www.cygwin.com/)
2.  Install the Cygwin packages `git`, `make`, `cmake`, `gcc-core`, `gcc-g++`.
3.  Run the Cygwin program, so that you see a terminal window.
4.  Follow the instructions in the REAPER Git repository
    [README](https://github.com/google/REAPER) and type the following commands
    in the terminal window:

        $ git clone https://github.com/google/REAPER.git
        $ cd REAPER
        $ mkdir build
        $ cd build
        $ cmake ..
        $ make

    Now the executable file `reaper.exe` will be in the folder
    [your Cygwin home directory]/REAPER/build
5.  Add `C:\cygwin\bin` (32-bit Cygwin) or `C:\cygwin64\bin` (64-bit Cygwin)
    to your environment variable named `PATH`.  This step is needed, so that
    when `reaper.exe` is called on the command line, the operating system can
    find the `cygwin1.dll` file it needs.
