"""Interface to the 'snack' audio library.

Snack can be called in several ways.
  1) On Windows, Snack can be run via a standalone binary executable
  2) Snack can be called through the Python/Tkinter inteface
  3) Snack can be called on the system command line through the Tcl shell
"""

from __future__ import division

from sys import platform
from subprocess import call

import os
import numpy as np

# Import user-defined global configuration variables
from tools.userconf import user_default_snack_method, user_tcl_shell_cmd

import logging
log = logging.getLogger('opensauce.snack')

# Only import tkinter if the user wants to call Snack from Python
if user_default_snack_method == 'python':
    try:
        import tkinter
    except ImportError:
        try:
            import Tkinter as tkinter
        except ImportError:
            print("Need Python library tkinter. Is it installed?")

def snack_pitch(wav_fn, method, frame_length=0.001, window_length=0.0025,
                max_pitch=500, min_pitch=40):
    """Return F0 and voicing vectors computed from the data in wav_fn.

    Use the snack esps method and extract the pitch (F0) and voicing values for
    each frame.

    windows_length and frame_shift are in seconds, max_pitch and min_pitch in
    Hertz.  Note the default parameter values are those used in VoiceSauce.
    """
    if method == 'exe':
        F0, V = snack_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch)
    elif method == 'python':
        F0, V = snack_python(wav_fn, frame_length, window_length, max_pitch, min_pitch)
    elif method == 'tcl':
        F0, V = snack_tcl(wav_fn, frame_length, window_length, max_pitch, min_pitch)
    else:
        raise ValueError("Invalid Snack calling method. Choices are 'exe', 'python', and 'tcl'")

    return F0, V

def snack_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch):
    """Implement snack_pitch by calling Snack through a Windows standalone
       binary executable

       Note this method can only be used on Windows.
    """
    # Call Snack using system command to run standalone executable
    exe_path = os.path.join(os.path.dirname(__file__), 'Windows', 'snack.exe')
    snack_cmd = [exe_path, 'pitch', wav_fn, '-method', 'esps']
    snack_cmd.extend(['-framelength', str(frame_length)])
    snack_cmd.extend(['-windowlength', str(window_length)])
    snack_cmd.extend(['-maxpitch', str(max_pitch)])
    snack_cmd.extend(['-minpitch', str(min_pitch)])
    return_code = call(snack_cmd)

    if return_code != 0:
        raise EnvironmentError('snack.exe error')

    # Path for f0 file corresponding to wav_fn
    f0_fn = wav_fn.split('.')[0] + '.f0'
    # Load data from f0 file
    if os.path.isfile(f0_fn):
        F0, V = np.loadtxt(f0_fn, usecols=(0,1), unpack=True)
        # Cleanup and remove f0 file
        os.remove(f0_fn)
    else:
        raise EnvironmentError('snack.exe error -- unable to locate .f0 file')

    return F0, V

def snack_python(wav_fn, frame_length, window_length, max_pitch, min_pitch):
    """Implement snack_pitch by calling Snack through Python's tkinter library

       Note this method can only be used if the user's machine is setup,
       so that Tcl/Tk can be accessed through Python's tkinter library
    """
    # HACK: Need to replace single backslash with two backslashes,
    #       so that the Tcl shell reads the file path correctly on Windows
    if platform == 'win32' or platform == 'cygwin':
        wav_fn = wav_fn.replace('\\', '\\\\')

    # XXX I'm assuming Hz for pitch; the docs don't actually say that.
    # http://www.speech.kth.se/snack/man/snack2.2/tcl-man.html#spitch
    tcl = tkinter.Tcl()
    try:
        # XXX This will trigger a message 'cannot open /dev/mixer' on the
        # console if you don't have a /dev/mixer.  You don't *need* a mixer to
        # snack the way we are using it, but there's no practical way to
        # suppress the message without modifying the snack source.  Fortunately
        # most people running opensauce will in fact have a /dev/mixer.
        tcl.eval('package require snack')
    except tkinter.TclError as err:
        log.critical('Cannot load snack (is it installed?): %s', err)
        return
    tcl.eval('snack::sound s')
    tcl.eval('s read {}'.format(wav_fn))
    cmd = ['s pitch -method esps']
    # Let snack use its defaults if no value specified for the keywords.
    cmd.extend(['-framelength {}'.format(frame_length)])
    cmd.extend(['-windowlength {}'.format(window_length)])
    cmd.extend(['-maxpitch {}'.format(max_pitch)])
    cmd.extend(['-minpitch {}'.format(min_pitch)])
    tcl.eval('set data [{}]'.format(' '.join(cmd)))
    # XXX check for errors here and log and abort if there is one.  Result
    # string will start with ERROR:.
    num_frames = int(tcl.eval('llength $data'))
    F0 = np.empty(num_frames)
    V = np.empty(num_frames)
    # snack returns four values per frame, we only care about the first two.
    for i in range(num_frames):
        values = tcl.eval('lindex $data ' + str(i)).split()
        F0[i] = np.float_(values[0])
        V[i] = np.float_(values[1])
    return F0, V

def snack_tcl(wav_fn, frame_length, window_length, max_pitch, min_pitch):
    """Implement snack_pitch by calling Snack through Tcl shell

       Note this method can only be used if Tcl is installed
    """
    # File path for wav file provided to Tcl script
    in_file = wav_fn

    # ERROR: wind_dur parameter must be between [0.0001, 0.1].
    # ERROR: frame_step parameter must be between [1/sampling rate, 0.1].
    # invalid/inconsistent parameters -- exiting.

    # HACK: Tcl shell expects double backslashes in Windows path
    if platform == 'win32' or platform == 'cygwin':
        in_file = in_file.replace('\\', '\\\\')

    tcl_file = os.path.join(os.path.dirname(wav_fn), 'tclforsnackpitch.tcl')

    # Determine name of system command to invoke Tcl shell
    if user_tcl_shell_cmd is not None:
        tcl_cmd = user_tcl_shell_cmd
    elif platform == 'darwin':
        tcl_cmd = 'tclsh8.4'
    else:
        tcl_cmd = 'tclsh'

    # Write Tcl script
    f = open(tcl_file, 'w')
    script = "#!/usr/bin/env bash\n"
    script += '# the next line restarts with tclsh \\\n'
    script += 'exec {} "$0" "$@"\n\n'.format(tcl_cmd)
    script += 'package require snack\n\n'
    script += 'snack::sound s\n\n'
    script += 's read {}\n\n'.format(in_file)
    script += 'set fd [open [file rootname {}].f0 w]\n'.format(in_file)
    script += 'puts $fd [join [s pitch -method esps -framelength {} -windowlength {} -maxpitch {} -minpitch {}]\n\n]\n'.format(frame_length, window_length, max_pitch, min_pitch)
    script += 'close $fd\n\n'
    script += 'exit'
    f.write(script)
    f.close()

    # Run Tcl script
    return_code = call([tcl_cmd, tcl_file])

    if return_code != 0:
        raise EnvironmentError('Error when trying to call Snack via Tcl shell script.  Is Tcl/Tk installed?')

    # Load data from f0 file
    f0_file = os.path.splitext(wav_fn)[0] + '.f0'
    if os.path.isfile(f0_file):
        data = np.loadtxt(f0_file).reshape((-1,4))
        F0 = data[:, 0]
        V = data[:, 1]
        # Cleanup and remove f0 file
        os.remove(f0_file)
    else:
        raise EnvironmentError('Snack Tcl shell error -- unable to locate .f0 file')

    # Cleanup and remove Tcl script file
    os.remove(tcl_file)

    return F0, V
