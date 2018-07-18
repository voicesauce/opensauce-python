opensauce-python
================

This is a Python port of
[VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/) (written in MATLAB) /
[OpenSauce](https://github.com/voicesauce/opensauce) (written in GNU Octave).
It provides a set of command-line tools for taking automatic voice measurements
from audio recordings.

# Project status

[![Travis CI build status](https://travis-ci.org/voicesauce/opensauce-python.svg?branch=master)](https://travis-ci.org/voicesauce/opensauce-python)
[![codecov status](https://codecov.io/gh/voicesauce/opensauce-python/branch/master/graph/badge.svg)](https://codecov.io/gh/voicesauce/opensauce-python)

# Requirements

* Windows, Mac OS X, or Linux operating system
* Python 2.7 or 3.4+
* Python packages [NumPy](http://www.numpy.org/) and [SciPy](http://www.scipy.org/)

OpenSauce has been successfully tested on Ubuntu 14.04 and 16.04,
Manjaro 17.0, Windows 7 64-bit, and Mac OS X 10.11 El Capitan. We have also
successfully tested OpenSauce using the Anaconda distribution of Python on
Windows, Mac OS X, and Linux.

If you want to use Snack to estimate parameters, you need to install the
following:
* Tcl/Tk 8.4+ (needed to run Snack Sound Toolkit)
* [Snack Sound Toolkit](http://www.speech.kth.se/snack/) (v2.2)

If you want to use Praat to estimate parameters, you need to download the
Praat software.
* [Praat](http://www.fon.hum.uva.nl/praat/) (version 6.0.20+)

OpenSauce has been tested with Praat v6.0.20 - v6.0.35 on Linux.  It's possible
that OpenSauce may work with Praat version 6.0.03 or higher, but that has not
been tested.

If you want to use REAPER to estimate F0, you need to either install the
corresponding Python package pyreaper or build it using a C compiler.

* Python packages [Cython](http://cython.org/) and
  [pyreaper](https://github.com/voicesauce/pyreaper)
  (Note: Cython and NumPy are requirements for pyreaper)

OR

* Build REAPER from [source](https://github.com/google/REAPER)

*Note: Currently, the only input files supported are WAV files in 16-bit
integer PCM format.  Praat can only read certain file types described in their
[documentation](http://www.fon.hum.uva.nl/praat/manual/Sound_files_3__Files_that_Praat_can_read.html).
Snack can only read the file types described in their
[documentation](http://www.speech.kth.se/snack/man/snack2.2/tcl-man.html#sound).
REAPER only supports 16-bit integer PCM input files.  If you would like to see
other file types supported, please let us know in the issue tracker!*

# Installation

1.  Install Python, the Python packages NumPy / SciPy / Reaper, and Snack Sound
    Toolkit, if you don't already have them. Installing Snack can be
    non-trivial, so we recommend that you follow the recommendations in the
    instructions below for this step.

    * [Windows specific instructions](WINDOWS.md)
    * Mac OS X specific instructions ([Homebrew](MAC-OS-X.md),
      [Anaconda Python](MAC-OS-X-CONDA.md))
    * Linux specific instructions ([Standard Python](LINUX.md),
      [Anaconda Python](LINUX-CONDA.md))

2.  Download Praat, if you don't already have it.  On Linux, if you have
    trouble with the full featured Praat executable, you can download and use
    the "barren" version instead.  The barren version lacks the GUI and other
    features, but those aren't needed for OpenSauce.

3.  Install Git, if you don't have it on your machine.  See the official Git
    website for [recommendations on how to install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

4.  Finally, navigate to the directory where you want to download opensauce and
    clone this repository using Git.

        $ git clone https://github.com/voicesauce/opensauce-python.git

5.  To get updates to the software, use the `git pull` command inside the
    `opensauce-python` directory.

        $ git pull

# Quickstart

(Note that these are interim instructions. Eventually there will be an
'opensauce' command.)

To run OpenSauce, open a new terminal window, `cd` into the directory where you
cloned `opensauce-python`:

    $ cd /path/to/opensauce-python

You can view the command help by typing:

    $ python -m opensauce --help

or alternatively:

    $ python -m opensauce --h

Here's an example of how to use the command line interface.  To process a sound
file and get the SHR measurements written to a CSV file, do:

    $ python -m opensauce --measurements SHR -o out.csv /path/to/file.wav

Or alternatively, you can put file path to the sound file first.

    $ python -m opensauce /path/to/file.wav --measurements SHR -o out.csv

The default output format used is Excel tab delimited.  You can also output
files that are comma delimited using the option `--output-delimiter`.

You can list multiple measurements in a single command. To process a sound file
and get the PraatF0 and SHR measurements written to a CSV file, do:

    $ python -m opensauce --measurements praatF0 SHR -o out.csv /path/to/file.wav

(Note that if a Snack, Praat, or REAPER command doesn't appear to be working
even though you installed the program, you may need to move the Snack / Praat
/ REAPER executable to the default location or set the correct path by using a
settings file or passing the correct path through a parameter. See next
section for details.)

You can process multiple wav files by using shell wildcards.  Suppose
your wav files are in the directory `data/sample1`.  You can process
all of them by typing:

    $ python -m opensauce --measurements SHR -o out.csv data/sample1/*.wav

If you want to write the output to stdout (that is, displayed on the terminal)
instead of writing to a file, leave off the `-o` optional argument.  For
example, this command writes the SHR measurements to stdout and
does not use TextGrid information.

    $ python -m opensauce --measurements SHR --no-textgrid /path/to/file.wav

To view other measurement options, run `$ python -m opensauce --help` to see
which measurements are available.)

The command line interface has default values for all the different options.
To see the default values, run the help command: `python -m opensauce -h`.

If you want to use TextGrid files in your analysis, make sure that each sound
file you analyze `name.wav`, has a corresponding TextGrid file with the same
base filename followed by the `.TextGrid` extension, e.g. `name.TextGrid`.
Capitalization is important, so `name.TextGrid` will be found, but
`name.textgrid` will not.

Note there is one subtlety with using the command line interface.  You cannot
specify the sound files right after the `--measurements` option.

A command, such as,

    $ python -m opensauce --measurements SHR /path/to/file.wav

would fail to be parsed correctly because the path of the sound file is
interpreted as a measurement.  Either make sure that there is another option
specified after measurements,

    $ python -m opensauce --measurements SHR --no-labels /path/to/file.wav

or specify the sound file at the beginning.

    $ python -m opensauce /path/to/file.wav --measurements SHR

# Adjusting settings for Snack, Praat, and REAPER

Snack, Praat, and REAPER are all external programs, outside of OpenSauce.
OpenSauce calls these programs when the corresponding measurements (Snack /
Praat / REAPER) are requested by the user.

When Snack measurements are requested, OpenSauce tries to use default values
for the Tcl shell command. When Praat measurements are requested, OpenSauce
calls the Praat executable. When REAPER measurements are requested with the
`use-creaper` parameter, OpenSauce calls the REAPER executable. If the default
values don't match your installation, you will need to either move the
executables to the default locations or explicitly specify the path to the
executable location on your system.

Note, if you install the pyreaper Python package and request REAPER
measurements with the `use-pyreaper` parameter, you don't need to worry about
setting the path to the REAPER executable.

For Snack, the default Tcl shell command is `tclsh8.4` on Mac OS X, and `tclsh`
on Windows and Linux.

For Praat, the default path is `/Applications/Praat.app/Contents/MacOS/Praat`
on Mac OS X, `C:\Program Files\Praat.exe` on Windows, and `/usr/bin/praat` on
Linux.

For REAPER, the default path to the REAPER executable is `/usr/bin/reaper`.

If you are calling Snack via the Tcl shell, you can set the command that runs
the Tcl shell interpreter using the `--tcl-cmd` command line option.  For
example, if we use run

    $ python -m opensauce --measurements snackF0 --tcl-cmd tclsh8.5 /path/to/file.wav

this tells OpenSauce to use the command `tclsh8.5` to run the Tcl shell
interpreter (specifically Tcl version 8.5).  This is especially useful if you
have multiple versions of Tcl installed on your machine.

To specify your own path for the Praat executable, use the command line option
`--praat-path`.  For example,

    $ python -m opensauce --measurements praatF0 --praat-path /home/username/praat /path/to/file.wav

will run the Praat executable located at `/home/username/praat`.

To specify your own path for the REAPER executable, use the command line option
`--reaper-path`.  For example,

    $ python -m opensauce --measurements reaperF0 --reaper-path /home/username/reaper /path/to/file.wav

will run the REAPER executable located at `/home/username/reaper`.

Since you will probably be running Snack / Praat / REAPER the same way every
time you use OpenSauce, it is best to set these preferences automatically
through a settings file, as described in the next section.

# Settings and measurement files

If it is inconvenient to enter options on the command line, you can also do
this via a settings and/or measurements file.

Any options you can specify on the command line you can put into a settings
file, one option and its arguments per line.  On the command line, you can
specify a settings file to use, with a command like

    $ python -m opensauce -s /path/to/my_settings /path/to/file.wav

or alternatively,

    $ python -m opensauce --settings /path/to/my_settings /path/to/file.wav

To run your favorite settings by default, you can copy your settings file to
one of the locations `./opensauce.settings`, `~/.config/opensauce/settings`,
or `~/.opensaucerc`.  Opensauce will automatically search each of these
locations, in the above order, for a default settings file, if no settings file
is explicitly specified on the command line.  The first file found will be
used.

An example settings file is included in this repository, called
`opensauce.settings.example`.  You can copy this file to `opensauce.settings`
to see how the settings file works.  Run OpenSauce on a sound file with no
settings file specified, like this:

    $ python -m opensauce /path/to/file.wav

You can also have a measurements file containing one measurement per line.  On
the command line, you can specify a measurements file to use, with a command
like

    $ python -m opensauce -m my_measurements /path/to/file.wav

To run your favorite settings by default, you can copy your measurements file
to one of the locations `./opensauce.measurements`,
`~/.config/opensauce/measurements`, or `~/.opensauce.measurements`.  Opensauce
will automatically search each of these locations, in the above order, for a
default settings file, if no settings file is explicitly specified on the
command line.  The first file found will be used.

An example settings file is included in this repository, called
`opensauce.measurements.example`.  You can copy this file to
`opensauce.measurements` to see how the measurements file works.  Run OpenSauce
on a sound file with no measurements file specified, like this:

    $ python -m opensauce /path/to/file.wav

Note that if you specify measurements in both the settings and measurements
files, the measurements in the settings file will override those in the
measurements file.  Similarly, options and measurements specified on the
command line override those specified in a settings or measurements file.

# Contributing

See [CONTRIBUTING](CONTRIBUTING.md).

# Resources

* Documentation: someday
* [OpenSauce](https://github.com/voicesauce/opensauce)
* [VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/)
* [STRAIGHT speech software](http://www.wakayama-u.ac.jp/~kawahara/STRAIGHTadv/index_e.html)

# Questions

Please feel free to post a question on the Issue tracker (use the label
'question').

# Acknowledgments

Thanks to Ryuichi Yamamoto for his help getting pyreaper working.
