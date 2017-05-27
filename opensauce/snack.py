"""Interface to the 'snack' audio library.

Requires that snack be installed where the tcl/tk used by Python can find it.
On linux systems this normally means installing it via the system package
manager.

"""

# XXX We may need to add a call to snack.exe on Windows if a snack install on
# Windows isn't visible to Windows Python.

from __future__ import division

from subprocess import call

import os
import numpy as np

import logging
log = logging.getLogger('opensauce.snack')

try:
    import tkinter
except ImportError:
    import Tkinter as tkinter


def snack_pitch(wav_fn, method, frame_length=None, window_length=None,
                max_pitch=None, min_pitch=None):
    """Return F0 and voicing vectors computed from the data in wav_fn.

    Use the snack esps method and extract the pitch (F0) and voicing values for
    each frame.

    windows_size and frame_shift are in seconds, max_pitch and min_pitch in
    Hertz.  Defaults are the snack defaults.

    """
    if method == 'exe':
        F0, V = snack_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch)
    elif method == 'python':
        F0, V = snack_python(wav_fn, frame_length, window_length, max_pitch, min_pitch)
    elif method == 'tcl':
        raise NotImplementedError('tcl method not implemented yet')
    else:
        raise ValueError("Invalid Snack calling method. Choices are 'exe', 'python', and 'tcl'")

    return F0, V

def snack_exe(wav_fn, frame_length, window_length, max_pitch, min_pitch):

    exe_path = os.path.join(os.path.dirname(__file__), 'Windows', 'snack.exe')
    snack_cmd = [exe_path, 'pitch', wav_fn, '-method', 'esps']
    if frame_length is not None:
        snack_cmd.extend(['-framelength', str(frame_length)])
    if window_length is not None:
        snack_cmd.extend(['-windowlength', str(window_length)])
    if max_pitch is not None:
        snack_cmd.extend(['-maxpitch', str(max_pitch)])
    if min_pitch is not None:
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
    local_vars = locals()
    # Let snack use its defaults if no value specified for the keywords.
    for v in ('frame_length', 'window_length', 'max_pitch', 'min_pitch'):
        if local_vars[v] is not None:
            cmd.extend(['-' + v.replace('_', '') + ' ' + str(local_vars[v])])
    tcl.eval('set data [{}]'.format(' '.join(cmd)))
    # XXX check for errors here and log and abort if there is one.  Result
    # string will start with ERROR:.
    num_frames = int(tcl.eval('llength $data'))
    F0, V = [], []
    # snack returns four values per frame, we only care about the first two.
    for i in range(num_frames):
        values = tcl.eval('lindex $data ' + str(i)).split()
        F0.append(float(values[0]))
        V.append(float(values[1]))
    return F0, V
