Windows instructions
====================

Here are some specific instructions on how to setup your Windows machine to
run opensauce-python.

1. Install [Anaconda](https://www.continuum.io/), the 32-bit Python 2.7
   version.  This is important; use 32-bit version, even if you have a 64-bit
   Windows operating system.  The Snack Sound Toolkit is very old, and can only
   run on 32-bit software.  Currently, only Python 2.7 is supported on
   opensauce-python.  Python 3.x is not supported.

2. Download the [Snack Speech Toolkit](http://www.speech.kth.se/snack/),
   "Binary release for Windows with Python 2.3" and unzip the file.  Read the
   [installation notes for Snack and Python](http://www.speech.kth.se/snack/pyinstall.html).

3. Open a Windows command prompt and type

        > where anaconda

   to find out where Anaconda is installed. For example, if you installed
   Anaconda for all users, it might be installed at
   `C:\ProgramData\Anaconda2`.

4. Follow the installation notes for Snack.  Copy `tkSnack.py` to the `Lib`
   directory.  Assuming Anaconda is installed at `C:\ProgramData\Anaconda2`,
   `tkSnack.py` would be copied to `C:\ProgramData\Anaconda2\Lib`.  Copy the
   `snacklib` folder to the `tcl` directory.  Assuming the same Anaconda
   installation directory, `snacklib` would be copied to
   `C:\ProgramData\Anaconda2\tcl`.
