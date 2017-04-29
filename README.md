opensauce-python
================

This is a Python port of
[VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/) (written in MATLAB) /
[OpenSauce](https://github.com/voicesauce/opensauce) (written in GNU Octave).
It provides a set of command-line tools for taking automatic voice measurements
from audio recordings.

# Installation

1.  NOTE that OpenSauce depends on the Python packages
    [NumPy](http://www.numpy.org/) and [SciPy](http://www.scipy.org/).

    To install these packages on a Mac or Linux machine, you can use pip:

        $ python -m pip install --upgrade pip
        $ pip install --user numpy scipy

    (Advanced users might want to install the NumPy and SciPy packages in a
    [virtualenv](https://virtualenv.pypa.io).)

    Debian / Ubuntu users might prefer to install NumPy and SciPy system-wide
    via their package manager:

        $ sudo apt-get install python-numpy python-scipy

    If you have trouble, look at the
    [SciPy documentation](https://www.scipy.org/install.html).

    Another way to obtain these packages is to install
    [Anaconda](https://www.continuum.io) as your Python distribution. Anaconda
    includes the NumPy and SciPy packages by default.

2.  In addition, you may need to install Tcl/Tk and Snack. If you're on a Debian
    / Ubuntu machine, install the relevant packages using these commands:

        $ sudo apt-get install tk8.4
        $ sudo apt-get install libsnack2

    Note that the code will probably work with a later versions of tk; it has
    been tested with tk8.4 and tk8.5 on Linux.

3.  Finally, clone this repository.

        $ git clone https://github.com/voicesauce/opensauce-python.git

# Quickstart

(Note that these are interim instructions. Eventually there will be
installation instructions and an 'opensauce' command.)

To run OpenSauce, open a new terminal window, `cd` into the directory where you
cloned `opensauce-python`:

    $ cd /path/to/opensauce-python

You can view the command help by typing:

    $ python -m opensauce --help

or alternatively:

    $ python -m opensauce --h

Here's an example of how to use the command line interface.  To process a sound
file and get the snackF0 and SHR measurements written to a CSV file, do:

    $ python -m opensauce --measurements snackF0 SHR -o out.csv /path/to/file.wav

Or alternatively, you can put file path to the sound file first.

    $ python -m opensauce /path/to/file.wav --measurements snackF0 SHR -o out.csv

The CSV format used is Excel tab delimited.

You can process multiple wav files by using shell wildcards.  Suppose
your wav files are in the directory `data/sample1`.  You can process
all of them by typing:

    $ python -m opensauce --measurements snackF0 SHR -o out.csv data/sample1/*.wav

If you want to write the output to stdout (that is, displayed on the terminal)
instead of writing to a file, leave off the `-o` optional argument.  For
example, this command writes the snackF0 and SHR measurements to stdout and
does not use TextGrid information.

    $ python -m opensauce --measurements snackF0 SHR --no-textgrid /path/to/file.wav

Any options you can specify on the command line you can also put into a
settings file, one option and its arguments per line.  You can also or
alternatively have a measurements file containing one measurement per line.
OpenSauce looks for the settings and measurement files first in the current
directory, then in your home directory, and then in your `.config/opensauce`
directory.  (For more information, run `$ python -m opensauce --help` again).
Options and measurements specified on the command line override those specified
in a settings or measurements file.

Currently only the snackF0, shrF0, and SHR measurements are supported. (Again,
you can run `$ python -m opensauce --help` to see which measurements are
available.

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

# Contributing

See [HACKING](HACKING.md).

# Resources

* Documentation: someday
* [OpenSauce](https://github.com/voicesauce/opensauce)
* [VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/)

# Questions

Please feel free to post a question on the Issue tracker (use the label
'question').
