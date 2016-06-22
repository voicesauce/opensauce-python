opensauce-python
================

A Python port of Voicesauce (MATLAB)/OpenSauce (GNU Octave). A set of
command-line tools for taking automatic voice measurements from audio
recordings.


# Installation

NOTE that OpenSauce depends on the following Python libraries:
* [Scipy](http://www.scipy.org/)

Install these first before proceeding (I recommend installing
[Anaconda](https://store.continuum.io/cshop/anaconda/).

In addition, you may need to install Tcl/Tk and Snack. If you're on a Debian
machine, try:

        $ sudo apt-get install tk8.4
        $ sudo apt-get install libsnack2

Finally, clone this repository.

Note that the code will probably work with a later versions of tk; it has been
tested with tk8.4 and tk8.5 on linux.


# Quickstart

(Note that these are interim instructions...eventually there will be
installation instructions and an 'opensauce' command.)

To run OpenSauce, open a new Terminal window, `cd` into the directory where you
cloned `opensauce-python`:

        $ cd /path/to/opensauce-python

You can view the command help by typing:

        $ python -m opensauce --help

To process a file and get the snackF0 and SHR measurements as output, do:

        $ python -m opensauce /path/to/file.wav -m snackF0 -m SHR

The csv formatted data will be written to stdout (that is, displayed
on the terminal).  To write it to a file you can either redirect stdout
or do:

        $ python -m opensauce /path/to/file.wav -m snackF0 -m SHR -o out.csv

You can process multiple wav files by using shell wildcards.  Suppose
your wav files are in the directory 'data/sample1'.  You can process
all of them by typing:

        $ python -m opensauce data/sample1/*.wav -m snackF0 -m SHR -o out.csv

Any options you can specify on the command line you can also put into a
settings file, one option and its arguments per line.  You can also or
alternatively have a measurements file containing one measurement per line.
opensauce looks for the settings and measurement files first in the current
directory, then in your home directory, and then in your .config/opensauce
directory.  (This is all documented in the --help).  Options and
measurements specified on the command line override those specified in
a settings or measurements file.

Currently only the snackF0, shrF0, and SHR measurements are supported,
as indicated by the --help information (which will be the most up to date
information, so check it!)


# Contributing

See HACKING.


# Resources

* documentation: someday
* [OpenSauce](https://github.com/voicesauce/opensauce)
* [VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/)


# Questions

Please feel free to post a question on the Issue tracker (use the label
'question') or e-mail me at ksilvers at umass dot edu.
