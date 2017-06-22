"""Interface to the 'snack' audio library.

Snack can be called in several ways.
  1) On Windows, Snack can be run via a standalone binary executable
  2) Snack can be called through the Python/Tkinter inteface
  3) Snack can be called on the system command line through the Tcl shell
"""

from __future__ import division

from subprocess import call

import os
import sys
import inspect
import numpy as np

# Import user-defined global configuration variables
from conf.userconf import user_default_snack_method, user_tcl_shell_cmd

import logging
log = logging.getLogger('opensauce.snack')

sformant_names = ['sF1', 'sF2', 'sF3', 'sF4', 'sB1', 'sB2', 'sB3', 'sB4']

def snack_pitch(wav_fn, method, frame_length=0.001, window_length=0.025,
                max_pitch=500, min_pitch=40, tcl_shell_cmd=None):
    """Return F0 and voicing vectors computed from the data in wav_fn.

    Use the snack esps method and extract the pitch (F0) and voicing values for
    each frame.

    windows_length and frame_shift are in seconds, max_pitch and min_pitch in
    Hertz.  Note the default parameter values are those used in VoiceSauce.

    method refers to the way in which Snack is called:
        'exe'    - Call Snack via Windows executable
        'python' - Call Snack via Python's tkinter Tcl interface
        'tcl'    - Call Snack via Tcl shell

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.  This
    argument is only used if method = 'tcl'
    """
    if method in valid_snack_methods:
        if method == 'exe':
            F0, V = snack_pitch_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch)
        elif method == 'python':
            F0, V = snack_pitch_python(wav_fn, frame_length, window_length, max_pitch, min_pitch)
        elif method == 'tcl':
            F0, V = snack_pitch_tcl(wav_fn, frame_length, window_length, max_pitch, min_pitch, tcl_shell_cmd)
    else:
        raise ValueError('Invalid Snack calling method. Choices are {}'.format(valid_snack_methods))

    return F0, V

def snack_pitch_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch):
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
        raise OSError('snack.exe error')

    # Path for f0 file corresponding to wav_fn
    f0_fn = wav_fn.split('.')[0] + '.f0'
    # Load data from f0 file
    if os.path.isfile(f0_fn):
        F0, V = np.loadtxt(f0_fn, usecols=(0,1), unpack=True)
        # Cleanup and remove f0 file
        os.remove(f0_fn)
    else:
        raise OSError('snack.exe error -- unable to locate .f0 file')

    return F0, V

def snack_pitch_python(wav_fn, frame_length, window_length, max_pitch, min_pitch):
    """Implement snack_pitch by calling Snack through Python's tkinter library

       Note this method can only be used if the user's machine is setup,
       so that Tcl/Tk can be accessed through Python's tkinter library
    """
    try:
        import tkinter
    except ImportError:
        try:
            import Tkinter as tkinter
        except ImportError:
            print("Need Python library tkinter. Is it installed?")

    # HACK: Need to replace single backslash with two backslashes,
    #       so that the Tcl shell reads the file path correctly on Windows
    if sys.platform == 'win32' or sys.platform == 'cygwin':
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

def snack_pitch_tcl(wav_fn, frame_length, window_length, max_pitch, min_pitch, tcl_shell_cmd):
    """Implement snack_pitch by calling Snack through Tcl shell

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.

       Note this method can only be used if Tcl is installed
    """
    # File path for wav file provided to Tcl script
    in_file = wav_fn

    # ERROR: wind_dur parameter must be between [0.0001, 0.1].
    # ERROR: frame_step parameter must be between [1/sampling rate, 0.1].
    # invalid/inconsistent parameters -- exiting.

    # HACK: Tcl shell expects double backslashes in Windows path
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        in_file = in_file.replace('\\', '\\\\')

    tcl_file = os.path.join(os.path.dirname(wav_fn), 'tclforsnackpitch.tcl')

    # Determine name of system command to invoke Tcl shell
    if tcl_shell_cmd is not None:
        tcl_cmd = tcl_shell_cmd
    elif user_tcl_shell_cmd is not None:
        tcl_cmd = user_tcl_shell_cmd
    elif sys.platform == 'darwin':
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
    try:
        return_code = call([tcl_cmd, tcl_file])
    except OSError:
        os.remove(tcl_file)
        raise OSError('Error while attempting to call Snack via Tcl shell.  Is Tcl shell command {} correct?'.format(tcl_cmd))
    else:
        if return_code != 0:
            os.remove(tcl_file)
            raise OSError('Error when trying to call Snack via Tcl shell script.')

    # Load data from f0 file
    f0_file = os.path.splitext(wav_fn)[0] + '.f0'
    if os.path.isfile(f0_file):
        data = np.loadtxt(f0_file).reshape((-1,4))
        F0 = data[:, 0]
        V = data[:, 1]
        # Cleanup and remove f0 file
        os.remove(f0_file)
    else:
        raise OSError('Snack Tcl shell error -- unable to locate .f0 file')

    # Cleanup and remove Tcl script file
    os.remove(tcl_file)

    return F0, V

def snack_formants(wav_fn, method, frame_length=0.001, window_length=0.025,
                   pre_emphasis=0.96, lpc_order=12, tcl_shell_cmd=None):
    """Return formant and bandwidth vectors computed from the data in wav_fn.

    Use Snack to estimate formant and bandwidth for each frame

    windows_length and frame_shift are in seconds. pre_emphasis is used to
    specify the amount of preemphasis applied to the signal prior to windowing.
    lpc_order is order for LPC analysis.
    Note the default parameter values are those used in VoiceSauce.

    method refers to the way in which Snack is called:
        'exe'    - Call Snack via Windows executable
        'python' - Call Snack via Python's tkinter Tcl interface
        'tcl'    - Call Snack via Tcl shell

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.  This
    argument is only used if method = 'tcl'
    """
    if method in valid_snack_methods:
        if method == 'exe':
            estimates = snack_formants_exe(wav_fn, frame_length, window_length, pre_emphasis, lpc_order)
        elif method == 'python':
            estimates = snack_formants_python(wav_fn, frame_length, window_length, pre_emphasis, lpc_order)
        elif method == 'tcl':
            estimates = snack_formants_tcl(wav_fn, frame_length, window_length, pre_emphasis, lpc_order, tcl_shell_cmd)
    else:
        raise ValueError('Invalid Snack calling method. Choices are {}'.format(valid_snack_methods))

    return estimates

def snack_formants_exe(wav_fn, frame_length, window_length, pre_emphasis, lpc_order):
    """Implement snack_formants by calling Snack through a Windows standalone
       binary executable

       Note this method can only be used on Windows.
    """
    # Call Snack using system command to run standalone executable
    exe_path = os.path.join(os.path.dirname(__file__), 'Windows', 'snack.exe')
    snack_cmd = [exe_path, 'formant', wav_fn]
    snack_cmd.extend(['-windowlength', str(window_length)])
    snack_cmd.extend(['-framelength', str(frame_length)])
    snack_cmd.extend(['-windowtype', 'Hamming'])
    snack_cmd.extend(['-lpctype', '0'])
    snack_cmd.extend(['-preemphasisfactor', str(pre_emphasis)])
    snack_cmd.extend(['-ds_freq', '10000'])
    snack_cmd.extend(['-lpcorder', str(lpc_order)])
    return_code = call(snack_cmd)

    if return_code != 0:
        raise OSError('snack.exe error')

    # Path for frm file corresponding to wav_fn
    frm_fn = wav_fn.split('.')[0] + '.frm'
    # Load data from frm file
    if os.path.isfile(frm_fn):
        frm_results = np.loadtxt(frm_fn)
        # Cleanup and remove frm file
        os.remove(frm_fn)
    else:
        raise OSError('snack.exe error -- unable to locate .frm file')

    num_cols = frm_results.shape[1]

    estimates = {}
    for i in range(num_cols):
        estimates[sformant_names[i]] = frm_results[:, i]

    return estimates

def snack_formants_python(wav_fn, frame_length, window_length, pre_emphasis, lpc_order):
    """Implement snack_formants by calling Snack through Python's tkinter library

       Note this method can only be used if the user's machine is setup,
       so that Tcl/Tk can be accessed through Python's tkinter library
    """
    try:
        import tkinter
    except ImportError:
        try:
            import Tkinter as tkinter
        except ImportError:
            print("Need Python library tkinter. Is it installed?")

    # HACK: Need to replace single backslash with two backslashes,
    #       so that the Tcl shell reads the file path correctly on Windows
    if sys.platform == 'win32' or sys.platform == 'cygwin':
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
    cmd = ['s formant']
    cmd.extend(['-windowlength {}'.format(window_length)])
    cmd.extend(['-framelength {}'.format(frame_length)])
    cmd.extend(['-windowtype Hamming'])
    cmd.extend(['-lpctype 0'])
    cmd.extend(['-preemphasisfactor {}'.format(pre_emphasis)])
    cmd.extend(['-ds_freq 10000'])
    cmd.extend(['-lpcorder {}'.format(lpc_order)])
    tcl.eval('set data [{}]'.format(' '.join(cmd)))
    # XXX check for errors here and log and abort if there is one.  Result
    # string will start with ERROR:.
    num_frames = int(tcl.eval('llength $data'))
    num_cols = len(sformant_names)
    estimates = {}
    for n in sformant_names:
        estimates[n] = np.empty(num_frames)
    for i in range(num_frames):
        values = tcl.eval('lindex $data ' + str(i)).split()
        for j in range(num_cols):
            estimates[sformant_names[j]][i] = np.float_(values[j])

    return estimates

def snack_formants_tcl(wav_fn, frame_length, window_length, pre_emphasis, lpc_order, tcl_shell_cmd):
    """Implement snack_formants by calling Snack through Tcl shell

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.

       Note this method can only be used if Tcl is installed
    """
    # File path for wav file provided to Tcl script
    in_file = wav_fn

    # ERROR: wind_dur parameter must be between [0.0001, 0.1].
    # ERROR: frame_step parameter must be between [1/sampling rate, 0.1].
    # invalid/inconsistent parameters -- exiting.

    # HACK: Tcl shell expects double backslashes in Windows path
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        in_file = in_file.replace('\\', '\\\\')

    tcl_file = os.path.join(os.path.dirname(wav_fn), 'tclforsnackformant.tcl')

    # Determine name of system command to invoke Tcl shell
    if tcl_shell_cmd is not None:
        tcl_cmd = tcl_shell_cmd
    elif user_tcl_shell_cmd is not None:
        tcl_cmd = user_tcl_shell_cmd
    elif sys.platform == 'darwin':
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
    script += 'set fd [open [file rootname {}].frm w]\n'.format(in_file)
    script += 'puts $fd [join [s formant -windowlength {} -framelength {} -windowtype Hamming -lpctype 0 -preemphasisfactor {} -ds_freq 10000 -lpcorder {}]\n\n]\n'.format(window_length, frame_length, pre_emphasis, lpc_order)
    script += 'close $fd\n\n'
    script += 'exit'
    f.write(script)
    f.close()

    # Run Tcl script
    try:
        return_code = call([tcl_cmd, tcl_file])
    except OSError:
        os.remove(tcl_file)
        raise OSError('Error while attempting to call Snack via Tcl shell.  Is Tcl shell command {} correct?'.format(tcl_cmd))
    else:
        if return_code != 0:
            os.remove(tcl_file)
            raise OSError('Error when trying to call Snack via Tcl shell script.')

    # Load data from f0 file
    frm_file = os.path.splitext(wav_fn)[0] + '.frm'
    num_cols = len(sformant_names)
    if os.path.isfile(frm_file):
        frm_results = np.loadtxt(frm_file).reshape((-1, num_cols))
        estimates = {}
        for i in range(num_cols):
            estimates[sformant_names[i]] = frm_results[:, i]
        # Cleanup and remove f0 file
        os.remove(frm_file)
    else:
        raise OSError('Snack Tcl shell error -- unable to locate .frm file')

    # Cleanup and remove Tcl script file
    os.remove(tcl_file)

    return estimates

all_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
prefix_len = len('snack_pitch_')
valid_snack_methods = [x[0][prefix_len:] for x in all_functions if x[0].startswith('snack_pitch_')]
