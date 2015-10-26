opensauce-python
================
A Python port of Voicesauce (MATLAB)/OpenSauce (GNU Octave). A set of command-line tools for taking automatic voice measurements from audio recordings.

# Installation

NOTE that OpenSauce depends on the following Python libraries:
* [Scipy](http://www.scipy.org/)

Install these first before proceeding (I recommend installing [Anaconda](https://store.continuum.io/cshop/anaconda/).

In addition, you may need to install Tcl/Tk and Snack. If you're on a Debian machine, try:

	$ sudo apt-get install tk8.4
	$ sudo apt-get install libsnack2

Finally, clone this repository.

Note that the code will probably work with a later versions of tk; it has been
tested with tk8.4 and tk8.5 on linux.

# Quickstart
To run OpenSauce, open a new Terminal window, `cd` into the directory where you cloned `opensauce-python`, and set the `VS_ROOT` environment variable:

        $ cd /path/to/opensauce-python
        $ export VS_ROOT=$PWD

In order to take measurements, OpenSauce needs a directory of wave files, a directory where it can store the output of measurements, a settings file, and a parameters file. The settings file stores extra information that the measurement algorithms use to carry out calculations (e.g. the maximum value to consider for f0 candidates, voiced/unvoiced threshold, etc.). The parameters file is where you can specify the measurements that you want OpenSauce to take. To turn a measurement "on" in the parameters file, change the "0" next to the measurement label to a "1", e.g.

        F0 (Snack)|0 --> F0 (Snack)|1

Default files for settings and parameters are in the folder "defaults/settings/default.csv" and "defaults/parameters/default.csv", and you can find a sound file to use for Quickstart in "defaults/sounds".

To run OpenSauce using the default setup, type the following in Terminal:

        $ ./run.sh

To change the parameters and settings, I recommend that you copy the defaults as new files and edit the copies. You'll also need to modify the corresponding paths in `run.sh`.

# Contributing
See HACKING.

# Resources
* documentation: someday
* [OpenSauce](https://github.com/voicesauce/opensauce)
* [VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/)

# Questions
Please feel free to post a question on the Issue tracker (use the label 'question') or e-mail me at ksilvers at umass dot edu.


