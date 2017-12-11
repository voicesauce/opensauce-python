"""F0 estimation using REAPER: Robust Epoch And Pitch EstimatoR
"""

# Licensed under Apache v2 (see LICENSE)

from __future__ import division

import os
import subprocess
import numpy as np


def reaper_pitch(soundfile, data_len, use_pyreaper=True,
                 reaper_path='not-specified', frame_shift=1, max_pitch=500,
                 min_pitch=40, high_pass=True, hilbert_transform=False,
                 inter_mark=10):
    """Return F0 vector estimated by REAPER

    Args:
        soundfile         - SoundFile corresponding to voice recording [object]
        data_len          - Length of measurement vector [integer]
        reaper_path       - Path to REAPER executable [string]
        frame_shift       - Length of each frame in ms [integer]
                            (default = 1)
        max_pitch         - Maximum valid F0 allowed in Hz [integer]
                            (default = 500)
        min_pitch         - Minimum valid F0 allowed in Hz [integer]
                            (default = 40)
        high_pass         - Whether to apply high pass filter (80 Hz) to input
                            [Boolean] (default = True)
        hilbert_transform - Whether to apply Hilbert transform that may reduce
                            phase distortion [Boolean] (default = False)
        inter_mark        - Regular inter-mark interval to use in unvoiced
                            pitchmark regions given in milliseconds [integer]
                            (default = 10)
    Returns:
        F0                - F0 estimates [NumPy vector]
    """
    if soundfile.fs_rs is None:
        # Use values from original WAV file
        fs = soundfile.fs
        wavpath = soundfile.wavpath
        wavdata_int = soundfile.wavdata_int
    else:
        # Use values from resampled WAV file
        fs = soundfile.fs_rs
        wavpath = soundfile.wavpath_rs
        wavdata_int = soundfile.wavdata_rs_int

    if use_pyreaper:
        # Try running reaper from pyreaper package
        t_raw, F0_raw = pyreaper_pitch(wavdata_int, fs, frame_shift, max_pitch,
                                       min_pitch, high_pass, hilbert_transform,
                                       inter_mark)
    else:
        # Run original Google REAPER as system call
        t_raw, F0_raw = creaper_pitch(wavpath, reaper_path,
                                      frame_shift, max_pitch, min_pitch,
                                      high_pass, hilbert_transform, inter_mark)

    # Fill F0 vector with NaN
    F0 = np.full(data_len, np.nan)
    # Raw F0 output from reaper always starts at time = 0 and
    # is equally spaced at intervals corresponding to frame_shift
    F0[:len(F0_raw)] = F0_raw

    return F0

def pyreaper_pitch(wavdata_int, fs, frame_shift, max_pitch, min_pitch,
                   high_pass, hilbert_transform, inter_mark):
    """Return F0 vector estimated by pyreaper (Python package) along with
       corresponding times

    Args:
        wavdata_int       - 16-bit integer data from WAV file [NumPy array]
        fs                - Sampling frequency in Hz [integer]
        frame_shift       - Length of each frame in ms [integer]
        max_pitch         - Maximum valid F0 allowed in Hz [integer]
        min_pitch         - Minimum valid F0 allowed in Hz [integer]
        high_pass         - Whether to apply high pass filter (80 Hz) to input
                            [Boolean]
        hilbert_transform - Whether to apply Hilbert transform that may reduce
                            phase distortion [Boolean]
        inter_mark        - Regular inter-mark interval to use in unvoiced
                            pitchmark regions given in milliseconds [integer]
    Returns:
        F0_times          - Times corresponding to F0 estimates [NumPy vector]
        F0                - F0 estimates [NumPy vector]
    """
    try:
        from pyreaper import reaper
        pm_times, pm, F0_times, F0, corr = reaper(wavdata_int, fs, minf0=min_pitch,
                                                  maxf0=max_pitch,
                                                  do_high_pass=high_pass,
                                                  do_hilbert_transform=hilbert_transform,
                                                  inter_pulse=inter_mark / 1000.0,
                                                  frame_period=frame_shift / 1000.0)
    except ImportError: # pragma: no cover
        print("Need Python library pyreaper.  Is it installed?")

    # Replace invalid measurements with NaN
    F0[F0 < 0] = np.nan

    return F0_times, F0

def creaper_pitch(wav_fn, reaper_path, frame_shift, max_pitch, min_pitch,
                  high_pass, hilbert_transform, inter_mark):
    """Return F0 vector estimated by REAPER (compiled C code) along with
       corresponding times

    Args:
        wav_fn            - WAV filename [string]
        reaper_path       - Path to REAPER executable [string]
        frame_shift       - Length of each frame in ms [integer]
        max_pitch         - Maximum valid F0 allowed in Hz [integer]
        min_pitch         - Minimum valid F0 allowed in Hz [integer]
        high_pass         - Whether to apply high pass filter (80 Hz) to input
                            [Boolean]
        hilbert_transform - Whether to apply Hilbert transform that may reduce
                            phase distortion [Boolean]
        inter_mark        - Regular inter-mark interval to use in unvoiced
                            pitchmark regions given in milliseconds [integer]
    Returns:
        F0_times          - Times corresponding to F0 estimates [NumPy vector]
        F0                - F0 estimates [NumPy vector]
    """
    # Output file names
    wav_dir = os.path.dirname(wav_fn)
    reaper_f0_fn = os.path.join(wav_dir, 'reaper-f0.txt')
    # XXX: We aren't using the output of these files for now
    #      But they may be useful in the future
    reaper_pitchmarks_fn = os.path.join(wav_dir, 'reaper-pitchmarks.txt')
    reaper_corr_fn = os.path.join(wav_dir, 'reaper-corr.txt')

    # Run REAPER command
    cmd = [reaper_path, '-i', wav_fn]
    cmd.extend(['-f', reaper_f0_fn])
    cmd.extend(['-p', reaper_pitchmarks_fn])
    cmd.extend(['-c', reaper_corr_fn])
    if hilbert_transform:
        cmd.extend(['-t'])
    if not high_pass:
        cmd.extend(['-s'])
    cmd.extend(['-e', str(frame_shift / 1000.0)])
    cmd.extend(['-x', str(max_pitch)])
    cmd.extend(['-m', str(min_pitch)])
    cmd.extend(['-u', str(inter_mark / 1000.0)])
    cmd.extend(['-a'])

    try:
        return_code = subprocess.call(cmd, stdout=subprocess.PIPE)
    except OSError:
        raise OSError('Error while attempting to call REAPER.  Is REAPER path {} correct?'.format(reaper_path))
    else:
        if return_code != 0: # pragma: no cover
            raise OSError('Error when trying to call REAPER')

    # XXX: I think flag is 1 when the measurement is in a voiced region,
    #      and flag is 0 when the measurement is an unvoiced region
    F0_times, flag, F0 = np.loadtxt(reaper_f0_fn, skiprows=7, unpack=True)

    # Replace valid measurements with NaN
    F0[F0 < 0] = np.nan

    os.remove(reaper_f0_fn)
    os.remove(reaper_pitchmarks_fn)
    os.remove(reaper_corr_fn)

    return F0_times, F0
