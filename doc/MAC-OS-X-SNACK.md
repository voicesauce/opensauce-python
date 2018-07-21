Building Snack on Mac OS X
==========================

1.  Download the Snack 2.2.10
    [source code](http://www.speech.kth.se/snack/dist/snack2.2.10.tar.gz)
    and extract the file.

        $ tar -xzf snack2.2.10.tar.gz

    This command will extract all the source files into a `snack2.2.10`
    folder.

2.  Follow the directions in the `snack2.2.10/mac/README`, but with slightly
    different paths. Change to the `snack2.2.10/unix` directory. Then run:

        $ ./configure --with-tcl=/System/Library/Frameworks/Tcl.framework --with-tk=/System/Library/Frameworks/Tk.framework

    Note that contrary to the README instructions, the correct path is `/System/Library/Frameworks/...` and not `/Library/Frameworks/...`. (Thanks to this [blog post](https://codeforfun.wordpress.com/2010/09/13/osx-tcltk-and-snack/) for the correction.)

    Open `Makefile` and note the 3rd and 7th lines in the makefile:

        TCL_INCPATH = /BuildRoot/Library/Caches/com.apple.xbs/Sources/tcl/tcl-118.50.1/tcl/tcl/generic

        TK_INCPATH  = /BuildRoot/Library/Caches/com.apple.xbs/Sources/tcl/tcl-118.50.1/tk/tk/generic

    You need to change `TCL_INCPATH` to
    `/System/Library/Frameworks/Tcl.framework/Headers` and `TK_INCPATH` to
    `/System/Library/Frameworks/Tk.framework/Headers`

    You can do this manually by opening up the file and typing in the paths.

    Or you can do it on the command line by using sed:

        $ sed -e '3s~.*~TCL_INCPATH = /System/Library/Frameworks/Tcl.framework/Headers~' -i '' Makefile
        $ sed -e '7s~.*~TK_INCPATH = /System/Library/Frameworks/Tk.framework/Headers~' -i '' Makefile

    (Here we are using `~` as the delimiter in sed instead of `/`, since there are forward slashes `/` in the path name variable.)

3.  Now we can compile the Snack library using make.

        $ make

    If you get the error `sed: RE error: illegal byte sequence`, then try:

        $ export LC_CTYPE=C && export LANG=C && export LC_ALL=C && make

    Build the Snack library by running

        $ sudo make install

    The Snack library should be installed in `/lib/snack2.2`.

    (Alternatively, you can install to a specific directory using
    `$ make DESTDIR=/path/to/directory install`)

4.  Copy the Snack library to the folder where Tcl looks for packages. On
    Mac OS X High Sierra which uses Tcl8.5, this should be
    `/System/Library/Tcl/8.5`.

        $ sudo cp -R /lib/snack2.2 /System/Library/Tcl/8.5

    (If you installed to a different directory, replace `/lib/snack2.2` with
    the name of that directory.)

    Check that Tcl can find the Snack library, by running the Tclsh shell.

        $ tclsh8.5
        % package require snack
        % exit

    When you run the tclsh command `package require snack`, it should output
    `2.2` if the Snack library has been installed correctly. If instead it
    output `can't find package snack`, then the install failed.

    If you are running a different version of Tcl (e.g. Tcl8.6), change the
    references to `8.5` in the above to your version (e.g. `8.6`).
