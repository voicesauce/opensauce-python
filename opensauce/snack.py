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

import logging
log = logging.getLogger('opensauce.snack')

# Variable names for Snack formant and bandwidth vectors
sformant_names = ['sF1', 'sF2', 'sF3', 'sF4', 'sB1', 'sB2', 'sB3', 'sB4']

def snack_pitch(wav_fn, method, data_len, frame_shift=1,
                window_size=25, max_pitch=500, min_pitch=40,
                tcl_shell_cmd=None):
    """Return F0 and voicing vectors computed from the data in wav_fn.

    Use Snack to estimate the pitch (F0) and voicing values for each frame.
    Includes padding to fill out entire data vectors.  The Snack pitch
    values don't start until a half frame into the audio, so the first
    half-frame is NaN.

    method refers to the way in which Snack is called:
        'exe'    - Call Snack via Windows executable
        'python' - Call Snack via Python's tkinter Tcl interface
        'tcl'    - Call Snack via Tcl shell

    data_len is the number of data (time) points that will be output to the
    user.  All measurement vectors need to have this length.

    windows_size and frame_shift are in milliseconds, max_pitch and min_pitch
    in Hertz.  Note the default parameter values are those used in VoiceSauce.

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.  This
    argument is only used if method = 'tcl'
    """
    # Get raw Snack F0 and V vectors
    F0_raw, V_raw = snack_raw_pitch(wav_fn, method, frame_shift, window_size, max_pitch, min_pitch, tcl_shell_cmd)

    # Pad F0 and V with NaN
    # First half frame is NaN
    pad_head_F0 = np.full(np.int_(np.floor(window_size / frame_shift / 2)), np.nan)
    # Pad end with NaN
    pad_tail_F0 = np.full(data_len - (len(F0_raw) + len(pad_head_F0)), np.nan)
    F0_out = np.hstack((pad_head_F0, F0_raw, pad_tail_F0))

    # First half frame is NaN
    pad_head_V = np.full(np.int_(np.floor(window_size / frame_shift / 2)), np.nan)
    # Pad end with NaN
    pad_tail_V = np.full(data_len - (len(V_raw) + len(pad_head_V)), np.nan)
    V_out = np.hstack((pad_head_V, V_raw, pad_tail_V))

    return F0_out, V_out

def snack_raw_pitch(wav_fn, method, frame_shift=1, window_size=25,
                    max_pitch=500, min_pitch=40, tcl_shell_cmd=None):
    """Return F0 and voicing vectors computed from the data in wav_fn.

    The vectors returned here are the raw Snack output, without padding
    """
    if method in valid_snack_methods:
        if method == 'exe':
            F0_raw, V_raw = snack_raw_pitch_exe(wav_fn, frame_shift, window_size, max_pitch, min_pitch)
        elif method == 'python':
            F0_raw, V_raw = snack_raw_pitch_python(wav_fn, frame_shift, window_size, max_pitch, min_pitch)
        elif method == 'tcl':
            F0_raw, V_raw = snack_raw_pitch_tcl(wav_fn, frame_shift, window_size, max_pitch, min_pitch, tcl_shell_cmd)
    else:
        raise ValueError('Invalid Snack calling method. Choices are {}'.format(valid_snack_methods))

    return F0_raw, V_raw

def snack_raw_pitch_exe(wav_fn, frame_shift, window_size, max_pitch, min_pitch):
    """Implement snack_raw_pitch by calling Snack through a Windows standalone
       binary executable

       Note this method can only be used on Windows.
    """
    # Call Snack using system command to run standalone executable
    exe_path = os.path.join(os.path.dirname(__file__), 'Windows', 'snack.exe')
    snack_cmd = [exe_path, 'pitch', wav_fn, '-method', 'esps']
    snack_cmd.extend(['-framelength', str(frame_shift / 1000)])
    snack_cmd.extend(['-windowlength', str(window_size / 1000)])
    snack_cmd.extend(['-maxpitch', str(max_pitch)])
    snack_cmd.extend(['-minpitch', str(min_pitch)])
    return_code = call(snack_cmd)

    if return_code != 0:
        raise OSError('snack.exe error')

    # Path for f0 file corresponding to wav_fn
    f0_fn = wav_fn.split('.')[0] + '.f0'
    # Load data from f0 file
    if os.path.isfile(f0_fn):
        F0_raw, V_raw = np.loadtxt(f0_fn, dtype=float, usecols=(0,1), unpack=True)
        # Cleanup and remove f0 file
        os.remove(f0_fn)
    else:
        raise OSError('snack.exe error -- unable to locate .f0 file')

    return F0_raw, V_raw

def snack_raw_pitch_python(wav_fn, frame_shift, window_size, max_pitch, min_pitch):
    """Implement snack_raw_pitch by calling Snack through Python's tkinter library

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
    cmd.extend(['-framelength {}'.format(frame_shift / 1000)])
    cmd.extend(['-windowlength {}'.format(window_size / 1000)])
    cmd.extend(['-maxpitch {}'.format(max_pitch)])
    cmd.extend(['-minpitch {}'.format(min_pitch)])
    # Run Snack pitch command
    tcl.eval('set data [{}]'.format(' '.join(cmd)))
    # XXX check for errors here and log and abort if there is one.  Result
    # string will start with ERROR:.
    # Collect results and save in return variables
    num_frames = int(tcl.eval('llength $data'))
    F0_raw = np.empty(num_frames)
    V_raw = np.empty(num_frames)
    # snack returns four values per frame, we only care about the first two.
    for i in range(num_frames):
        values = tcl.eval('lindex $data ' + str(i)).split()
        F0_raw[i] = np.float_(values[0])
        V_raw[i] = np.float_(values[1])

    return F0_raw, V_raw

def snack_raw_pitch_tcl(wav_fn, frame_shift, window_size, max_pitch, min_pitch, tcl_shell_cmd):
    """Implement snack_raw_pitch by calling Snack through Tcl shell

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

    # Name of the file containing the Tcl script
    tcl_file = os.path.join(os.path.dirname(wav_fn), 'tclforsnackpitch.tcl')

    # Write Tcl script which will call Snack pitch calculation
    f = open(tcl_file, 'w')
    script = "#!/usr/bin/env bash\n"
    script += '# the next line restarts with tclsh \\\n'
    script += 'exec {} "$0" "$@"\n\n'.format(tcl_shell_cmd)
    script += 'package require snack\n\n'
    script += 'snack::sound s\n\n'
    script += 's read {}\n\n'.format(in_file)
    script += 'set fd [open [file rootname {}].f0 w]\n'.format(in_file)
    script += 'puts $fd [join [s pitch -method esps -framelength {} -windowlength {} -maxpitch {} -minpitch {}]\n\n]\n'.format(frame_shift / 1000, window_size / 1000, max_pitch, min_pitch)
    script += 'close $fd\n\n'
    script += 'exit'
    f.write(script)
    f.close()

    # Run the Tcl script
    try:
        return_code = call([tcl_shell_cmd, tcl_file])
    except OSError:
        os.remove(tcl_file)
        raise OSError('Error while attempting to call Snack via Tcl shell.  Is Tcl shell command {} correct?'.format(tcl_shell_cmd))
    else:
        if return_code != 0:
            os.remove(tcl_file)
            raise OSError('Error when trying to call Snack via Tcl shell script.')

    # Load results from the f0 file output by the Tcl script
    # And save into return variables
    f0_file = os.path.splitext(wav_fn)[0] + '.f0'
    if os.path.isfile(f0_file):
        data = np.loadtxt(f0_file, dtype=float).reshape((-1,4))
        F0_raw = data[:, 0]
        V_raw = data[:, 1]
        # Cleanup and remove f0 file
        os.remove(f0_file)
    else:
        raise OSError('Snack Tcl shell error -- unable to locate .f0 file')

    # Cleanup and remove Tcl script file
    os.remove(tcl_file)

    return F0_raw, V_raw

def snack_formants(wav_fn, method, data_len, frame_shift=1,
                   window_size=25, pre_emphasis=0.96, lpc_order=12,
                   tcl_shell_cmd=None):
    """Return formant and bandwidth vectors computed from the data in wav_fn

    Use Snack to estimate formant and bandwidth for each frame
    Includes padding to fill out entire data vectors.  The Snack pitch
    values don't start until a half frame into the audio, so the first
    half-frame is NaN.

    method refers to the way in which Snack is called:
        'exe'    - Call Snack via Windows executable
        'python' - Call Snack via Python's tkinter Tcl interface
        'tcl'    - Call Snack via Tcl shell

    data_len is the number of data (time) points that will be output to the
    user.  All measurement vectors need to have this length.

    window_size and frame_shift are in milliseconds. pre_emphasis is used to
    specify the amount of preemphasis applied to the signal prior to windowing.
    lpc_order is order for LPC analysis.
    Note the default parameter values are those used in VoiceSauce.

    tcl_shell_cmd is the name of the command to invoke the Tcl shell.  This
    argument is only used if method = 'tcl'
    """
    # Compute raw formant and bandwidth estimates using Snack
    estimates_raw = snack_raw_formants(wav_fn, method, frame_shift, window_size, pre_emphasis, lpc_order, tcl_shell_cmd)

    # Pad estimates with NaN
    estimates = {}
    for n in sformant_names:
        # First half frame is NaN
        pad_head = np.full(np.int_(np.floor(window_size / frame_shift / 2)), np.nan)
        # Pad end with NaN
        pad_tail = np.full(data_len - (len(estimates_raw[n]) + len(pad_head)), np.nan)
        estimates[n] = np.hstack((pad_head, estimates_raw[n], pad_tail))

    return estimates

def snack_raw_formants(wav_fn, method, frame_shift=1, window_size=25,
                       pre_emphasis=0.96, lpc_order=12, tcl_shell_cmd=None):
    """Return formant and bandwidth vectors computed from the data in wav_fn

    The vectors returned here are the raw Snack output, without padding
    """
    if method in valid_snack_methods:
        if method == 'exe':
            estimates_raw = snack_raw_formants_exe(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order)
        elif method == 'python':
            estimates_raw = snack_raw_formants_python(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order)
        elif method == 'tcl':
            estimates_raw = snack_raw_formants_tcl(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order, tcl_shell_cmd)
    else:
        raise ValueError('Invalid Snack calling method. Choices are {}'.format(valid_snack_methods))

    return estimates_raw

def snack_raw_formants_exe(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order):
    """Implement snack_formants by calling Snack through a Windows standalone
       binary executable

       Note this method can only be used on Windows.
    """
    # Call Snack using system command to run standalone executable
    exe_path = os.path.join(os.path.dirname(__file__), 'Windows', 'snack.exe')
    snack_cmd = [exe_path, 'formant', wav_fn]
    snack_cmd.extend(['-windowlength', str(window_size / 1000)])
    snack_cmd.extend(['-framelength', str(frame_shift / 1000)])
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
        frm_results = np.loadtxt(frm_fn, dtype=float)
        # Cleanup and remove frm file
        os.remove(frm_fn)
    else:
        raise OSError('snack.exe error -- unable to locate .frm file')

    # Save data into dictionary
    num_cols = frm_results.shape[1]
    estimates_raw = {}
    for i in range(num_cols):
        estimates_raw[sformant_names[i]] = frm_results[:, i]

    return estimates_raw

def snack_raw_formants_python(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order):
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
    cmd.extend(['-windowlength {}'.format(window_size / 1000)])
    cmd.extend(['-framelength {}'.format(frame_shift / 1000)])
    cmd.extend(['-windowtype Hamming'])
    cmd.extend(['-lpctype 0'])
    cmd.extend(['-preemphasisfactor {}'.format(pre_emphasis)])
    cmd.extend(['-ds_freq 10000'])
    cmd.extend(['-lpcorder {}'.format(lpc_order)])
    # Run Snack formant command
    tcl.eval('set data [{}]'.format(' '.join(cmd)))
    # XXX check for errors here and log and abort if there is one.  Result
    # string will start with ERROR:.
    # Collect results in dictionary
    num_frames = int(tcl.eval('llength $data'))
    num_cols = len(sformant_names)
    estimates_raw = {}
    for n in sformant_names:
        estimates_raw[n] = np.empty(num_frames)
    for i in range(num_frames):
        values = tcl.eval('lindex $data ' + str(i)).split()
        for j in range(num_cols):
            estimates_raw[sformant_names[j]][i] = np.float_(values[j])

    return estimates_raw

def snack_raw_formants_tcl(wav_fn, frame_shift, window_size, pre_emphasis, lpc_order, tcl_shell_cmd):
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

    # Write Tcl script to compute Snack formants
    f = open(tcl_file, 'w')
    script = "#!/usr/bin/env bash\n"
    script += '# the next line restarts with tclsh \\\n'
    script += 'exec {} "$0" "$@"\n\n'.format(tcl_shell_cmd)
    script += 'package require snack\n\n'
    script += 'snack::sound s\n\n'
    script += 's read {}\n\n'.format(in_file)
    script += 'set fd [open [file rootname {}].frm w]\n'.format(in_file)
    script += 'puts $fd [join [s formant -windowlength {} -framelength {} -windowtype Hamming -lpctype 0 -preemphasisfactor {} -ds_freq 10000 -lpcorder {}]\n\n]\n'.format(window_size / 1000, frame_shift / 1000, pre_emphasis, lpc_order)
    script += 'close $fd\n\n'
    script += 'exit'
    f.write(script)
    f.close()

    # Run Tcl script
    try:
        return_code = call([tcl_shell_cmd, tcl_file])
    except OSError:
        os.remove(tcl_file)
        raise OSError('Error while attempting to call Snack via Tcl shell.  Is Tcl shell command {} correct?'.format(tcl_shell_cmd))
    else:
        if return_code != 0:
            os.remove(tcl_file)
            raise OSError('Error when trying to call Snack via Tcl shell script.')

    # Load results from f0 file and save into return variables
    frm_file = os.path.splitext(wav_fn)[0] + '.frm'
    num_cols = len(sformant_names)
    if os.path.isfile(frm_file):
        frm_results = np.loadtxt(frm_file, dtype=float).reshape((-1, num_cols))
        estimates_raw = {}
        for i in range(num_cols):
            estimates_raw[sformant_names[i]] = frm_results[:, i]
        # Cleanup and remove f0 file
        os.remove(frm_file)
    else:
        raise OSError('Snack Tcl shell error -- unable to locate .frm file')

    # Cleanup and remove Tcl script file
    os.remove(tcl_file)

    return estimates_raw

all_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
prefix_len = len('snack_raw_pitch_')
valid_snack_methods = [x[0][prefix_len:] for x in all_functions if x[0].startswith('snack_raw_pitch_')]
