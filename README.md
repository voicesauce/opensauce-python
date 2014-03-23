opensauce-python
================
A Python port of Voicesauce (MATLAB)/OpenSauce (GNU Octave). A set of command-line tools for taking automatic voice measurements from audio recordings.

# Installation

NOTE that OpenSauce depends on the following Python libraries:
* [Scipy](http://www.scipy.org/)

Install these first before proceeding (I recommend installing [Anaconda](https://store.continuum.io/cshop/anaconda/).

1. [Download the tarball](https://github.com/voicesauce/opensauce-python/blob/master/opensauce-python-0.0.0.tar.gz)

2. Open a new Terminal window.

3. Unpack the tarball:

        $ tar xzf opensauce-python-0.0.0.tar.gz

4. Run installation command:

        $ cd opensauce-python-0.0.0
        $ sudo python setup.py install

5. Test it out:

        $ ./test.sh

If step 5 doesn't work, try:

        $ chmod u+x test.sh
        $ ./test.sh

And if THAT doesn't work, submit a bug report in the Issue tracker.

# Quickstart
This Quickstart guide assumes you're using Mac OSX or Linux (tested on Ubuntu), Python 2.7, and that you've installed OpenSauce in directory that is an immediate descendant of your home directory (e.g. ~/opensauce-python-0.0.0).

To run OpenSauce, open a new Terminal window and type the following:

        $ cd ~/opensauce-python-0.0.0

In order to take measurements, OpenSauce needs a directory of wave files, a directory where it can store the output of measurements, a settings file, and a parameters file. The settings file stores extra information that the measurement algorithms use to carry out calculations (e.g. the maximum value to consider for f0 candidates, voiced/unvoiced threshold, etc.). The parameters file is where you can specify the measurements that you want OpenSauce to take. To turn a measurement "on" in the parameters file, change the "0" next to the measurement label to a "1", e.g.

        F0 (Snack)|0 --> F0 (Snack)|1

Default files for settings and parameters are in the folder "defaults/settings/default.csv" and "defaults/parameters/default.csv", and you can find a sound file to use for Quickstart in "defaults/sounds".

To run OpenSauce using the default setup, type the following in Terminal:

        $ python runner defaults/sounds defaults/output

To change the parameters and settings, I recommend that you copy the defaults as new files and edit the copies. In order to run OpenSauce using these new files, use the "--settings" and "--parameters" options:

        $ python runner indir outdir --settings path/to/settings/file --parameters path/to/params/file

# Contributing
See HACKING.

# Resources
* documentation: someday
* [OpenSauce](https://github.com/voicesauce/opensauce)
* [VoiceSauce](http://www.seas.ucla.edu/spapl/voicesauce/)

# Questions
Please feel free to post a question on the Issue tracker (use the label 'question') or e-mail me at ksilvers at umass dot edu.


