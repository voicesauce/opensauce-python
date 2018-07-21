# <A NAME="alternate">Alternate Snack setup</A>: Allows Snack to be called from Python

Note: We do not currently recommend calling Snack from Python/Tkinter because
of [#26](https://github.com/voicesauce/opensauce-python/issues/26).

If you want to setup your machine so that opensauce-python can call Snack from
Python, the steps are more complicated.  Thanks to Shinya Fujie for this
[guide on setting up Mac machines to run Snack in Python](http://qiita.com/fujie/items/afa463275a5e581667e9).

1.  Install the Homebrew package manager.  Follow the instructions on the
    [Homebrew website](https://brew.sh/) to install it.  Then run

        $ brew doctor

    to see how you can configure your system so that Homebrew is in your path.
    For example, you can add the line `export PATH="/usr/local/bin:$PATH"` to
    your `.bash_profile`.

2.  Install Tcl/Tk with Homebrew.

        $ brew install tcl-tk

3.  Install Python and link it to the Tcl-tk package you just installed by
    running the command

        $ brew install python --with-brewed-tk

4.  Install the Homebrew packages for Numpy and Scipy.

        $ brew install numpy scipy

5.  Download the [Snack Sound Toolkit](http://www.speech.kth.se/snack/).  Get
    the Snack 2.2.10 "Source release for all platforms"
    [version](http://www.speech.kth.se/snack/dist/snack2.2.10.tar.gz) and
    extract the archive.

6.  We need to change one line of the source code, to ensure that Snack will
    compile.  Go into the `generic` directory of the archive and open the file
    `jkCanvSpeg.c`.  Navigate to line 39 `#ifndef Solaris`.  On the following
    line, change the code

        #  ifndef TkPutImage

    to

        #  if 0

    Alternatively, you can use sed to do the text replacement in one command.

        $ sed -e '40s/.*/#   if 0/' -i '' generic/jkCanvSpeg.c

7.  Now compile Snack with the Tcl/Tk Homebrew package by running the following
    commands.

        $ ./configure --with-tcl=/usr/local/opt/tcl-tk/lib --with-tk=/usr/local/opt/tcl-tk/lib LDFLAGS=-L/usr/local/opt/tcl-tk/lib CPPFLAGS=-I/usr/local/opt/tcl-tk/include --disable-stubs
        $ make
        $ make DESTDIR=/usr/local/opt/tcl-tk install

    If the compilation fails because of a sed error, try adding the following
    lines to your `.bash_profile`:

        export LC_CTYPE=C
        export LANG=C

    This solution comes from this [StackOverflow answer](https://stackoverflow.com/questions/19242275/re-error-illegal-byte-sequence-on-mac-os-x).
