from __future__ import division
import os


def get_snack_f0(soundfile):

    # ERROR: wind_dur parameter must be between [0.0001, 0.1].
    # ERROR: frame_step parameter must be between [1/sampling rate, 0.1].
    # invalid/inconsistent parameters -- exiting.

    # if len(sys.argv) != 2:
    #     print "usage python snack_ks.py [infile]"
    #
    # infile = sys.argv[1]
    infile = soundfile.wavfile

    tclfile = 'tclforsnackpitch.tcl'

    # you can change these #
    frameshift = 0.01  # must be between 1/Fs and 0.1
    # frameshift = soundfile.settings["frameshift"]
    # windowlength = 0.25 # must be between 0.0001 and 0.1
    # windowlength = soundfile.settings["windowsize"]
    windowlength = 0.01
    maxF0 = 400
    minF0 = 90

    cmd1 = 'tclsh'
    f = open(tclfile, 'w')
    cmd = '#!/bin/bash\n'
    cmd += '# the next line restarts with wish \\\n'
    cmd += 'exec wish8.4 "$0" "$@"\n\n'
    cmd += 'package require snack\n\n'
    cmd += 'snack::sound s\n\n'
    cmd += 's read '+infile+'\n\n'
    cmd += 'set fd [open [file rootname '+infile+'].f0 w]\n'
    cmd += 'puts $fd [join [s pitch -method esps -framelength '+str(frameshift)+' -windowlength '+str(windowlength)+' -maxpitch '+str(maxF0)+' -minpitch '+str(minF0)+']\n\n]\n'
    cmd += 'close $fd\n\n'
    cmd += 'exit'
    f.write(cmd)
    f.close()

    os.system(cmd1+' '+tclfile)

    f0file = soundfile.wavfile[:-4]+".f0"
    raw = []
    with open(f0file, "r") as f:
        raw = f.read()

    raw = raw.split()
    f0 = [0.0]*len(raw)
    for i in range(len(raw)):
        f0[i] = float(raw[i])

    return f0
