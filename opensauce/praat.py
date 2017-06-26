"""Estimate F0 and formants using Praat
"""

from __future__ import division

import os
import numpy as np

from subprocess import call

from opensauce.helpers import round_half_away_from_zero, convert_boolean_for_praat

# Methods for performing Praat pitch analysis
# 'ac' is autocorrelation method
# 'cc' is cross-correlation method
valid_praat_f0_methods = ['ac', 'cc']

# Directory containing Praat scripts
praat_script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'praat-scripts')

# Praat will sometimes set numerical values to the string '--undefined--'
# But NumPy can't have a string in a float array, so we convert the
# '--undefined--' values to NaN
# Python 3 reads the undefined strings as byte literals, so we also have to
# check for the byte literal b'--undefined--'
undef = lambda x: np.nan if x =='--undefined--' or x == b'--undefined--' else x

def praat_pitch(wav_fn, data_len, praat_path, frame_shift=1, method='cc',
                frame_precision=1, min_pitch=40, max_pitch=500,
                silence_threshold=0.03, voice_threshold=0.45, octave_cost=0.01,
                octave_jumpcost=0.35, voiced_unvoiced_cost=0.14,
                kill_octave_jumps=False, interpolate=False, smooth=False,
                smooth_bandwidth=5):
    """Estimate F0 using Praat

    Args:
                      wav_fn - WAV file to be processed [string]
                    data_len - Length of measurement vector [integer]
                  praat_path - Path to Praat executable [string]
                 frame_shift - Length of each frame in ms [integer]
                               (default = 1)
                      method - Method for calculating Praat pitch, either
                               'ac' (autocorrelation) or 'cc'
                               (cross-correlation) [string]
                               (default = 'cc')
             frame_precision - Accuracy of F0 values in multiples of frame
                               length [integer]
                               (default = 1)
                   min_pitch - Minimum F0 considered in Hz [integer]
                               (default = 40)
                   max_pitch - Maximum F0 considered in Hz [integer]
                               (default = 500)
           silence_threshold - Relative amplitude below which a frame is
                               considered to be silent [float]
                               (default = 0.03)
             voice_threshold - Strength of the unvoiced candidate, relative to
                               the maximum possible autocorrelation [float]
                               (default = 0.45)
                 octave_cost - Degree of favouring of high-frequency
                               candidates, relative to the maximum possible
                               autocorrelation [float]
                               (default = 0.01)
             octave_jumpcost - Degree of disfavouring of pitch changes,
                               relative to the maximum possible autocorrelation
                               [float]
                               (default = 0.35)
        voiced_unvoiced_cost - Degree of disfavouring of voiced/unvoiced
                               transitions, relative to the maximum possible
                               autocorrelation [float]
                               (default = 0.14)
           kill_octave_jumps - Whether to try removing pitch halving and
                               doubling [Boolean]
                               (default = False)
                 interpolate - Whether to interpolate missing pitch values in
                               post-processing [Boolean]
                               (default = False)
                      smooth - Whether to smooth pitch in post-processing,
                               using bandwidth specified by smooth_bandwidth
                               [Boolean]
                               (default = False)
            smooth_bandwidth - Bandwidth in Hz to use for smoothing if
                               smooth is set to True [integer]
                               (default = 5)

    Returns:
        F0 - F0 estimates (NumPy vector)

    Raw Praat estimates are at time points that don't completely match the time
    points in our measurement vectors, so we need to interpolate.  We use a
    crude interpolation method, that has precision set by frame_precision.

    For more information, see the Praat manual pages:
        http://www.fon.hum.uva.nl/praat/manual/Sound__To_Pitch__ac____.html
        http://www.fon.hum.uva.nl/praat/manual/Sound__To_Pitch__cc____.html
    """
    # Compute raw Praat F0 estimates
    t_raw, F0_raw = praat_raw_pitch(wav_fn, praat_path, frame_shift, method,
                                    min_pitch, max_pitch, silence_threshold,
                                    voice_threshold, octave_cost,
                                    octave_jumpcost, voiced_unvoiced_cost,
                                    kill_octave_jumps, interpolate, smooth,
                                    smooth_bandwidth)

    # Initialize F0 measurement vector with NaN
    F0 = np.full(data_len, np.nan)
    # Convert time from seconds to nearest whole millisecond
    t_raw_ms = np.int_(round_half_away_from_zero(t_raw * 1000))

    # Raw Praat estimates are at time points that don't completely match
    # the time points in our measurement vectors, so we need to interpolate.
    # We use a crude interpolation method, that has precision set by
    # frame_precision.

    # Determine start and stop times
    start = 0
    if t_raw_ms[-1] % frame_shift == 0:
        stop = t_raw_ms[-1] + frame_shift
    else:
        stop = t_raw_ms[-1]
    # Iterate through timepoints corresponding to each frame in time range
    for idx_f, t_f in enumerate(range(start, stop, frame_shift)):
        # Find closest time point among calculated Praat values
        min_idx = np.argmin(np.abs(t_raw_ms - t_f))

        # If closest time point is too far away, skip
        if np.abs(t_raw_ms[min_idx] - t_f) > frame_precision * frame_shift:
             continue

        # If index is in range, set value of F0
        if (idx_f >= 0) and (idx_f < data_len):
            F0[idx_f] = F0_raw[min_idx]

    return F0

def praat_raw_pitch(wav_fn, praat_path, frame_shift=1, method='cc',
                    min_pitch=40, max_pitch=500, silence_threshold=0.03,
                    voice_threshold=0.45, octave_cost=0.01,
                    octave_jumpcost=0.35, voiced_unvoiced_cost=0.14,
                    kill_octave_jumps=False, interpolate=False, smooth=False,
                    smooth_bandwidth=5):
    """Return raw estimated F0 and corresponding time points using Praat

    Args:
        See praat_pitch() documentation.
        praat_raw_pitch() doesn't have the data_len and frame_precision
        arguments.

    Returns:
        t_raw  - times corresponding to raw F0 [NumPy Vector]
        F0_raw - raw F0 estimates [NumPy vector]
    """
    # Determine extension of Praat output file
    if method == 'ac':
        ext = '.praatac'
    elif method == 'cc':
        ext = '.praatcc'
    else:
        raise ValueError('Invalid Praat F0 method. Choices are {}'.format(valid_praat_f0_methods))

    # Convert Boolean variables to Praat values
    kill_octave_jumps = convert_boolean_for_praat(kill_octave_jumps)
    interpolate = convert_boolean_for_praat(interpolate)
    smooth = convert_boolean_for_praat(smooth)

    # Setup command to call Praat F0 script
    praat_cmd = [praat_path, '--run']
    praat_cmd.append(os.path.join(praat_script_dir, 'praatF0.praat'))
    praat_cmd.extend([os.path.abspath(wav_fn), os.path.splitext(wav_fn)[1]])
    praat_cmd.extend([str(frame_shift / 1000), str(min_pitch), str(max_pitch)])
    praat_cmd.extend([str(silence_threshold), str(voice_threshold)])
    praat_cmd.extend([str(octave_cost), str(octave_jumpcost)])
    praat_cmd.extend([str(voiced_unvoiced_cost), kill_octave_jumps])
    praat_cmd.extend([smooth, str(smooth_bandwidth)])
    praat_cmd.extend([interpolate, str(method)])

    # Run Praat F0 script
    return_code = call(praat_cmd)

    if return_code != 0:
        raise OSError('Praat error')

    # Path for Praat F0 output file corresponding to wav_fn
    f0_fn = wav_fn.split('.')[0] + ext
    # Load data from f0 file
    if os.path.isfile(f0_fn):
        # Check if file is empty
        if os.stat(f0_fn).st_size == 0:
            os.remove(f0_fn)
            raise OSError('Praat error -- pitch calculation failed, check input parameters')
        t_raw, F0_raw = np.loadtxt(f0_fn, unpack=True, converters={0: undef, 1: undef})
        # Cleanup and remove f0 file
        os.remove(f0_fn)
    else:
        raise OSError('Praat error -- unable to locate {} file'.format(ext))

    return t_raw, F0_raw

def praat_formants(wav_fn, data_len, praat_path, frame_shift=1, window_size=25,
                   frame_precision=1, num_formants=4, max_formant_freq=6000):
    """Estimate formants and bandwidths using Praat

    Args:
                      wav_fn - WAV file to be processed [string]
                    data_len - Length of measurement vector [integer]
                  praat_path - Path to Praat executable [string]
                 frame_shift - Length of each frame in ms [integer]
                               (default = 1)
                window_size  - Length of analysis window in ms [integer]
                               (default = 25)
             frame_precision - Accuracy of F0 values in multiples of frame
                               length [integer]
                               (default = 1)
                num_formants - Number of formants to extract,
                               usually an integer but half-integer values are
                               allowed [float]
                               (default = 4)
            max_formant_freq - Maximum allowed frequency for formant search
                               range in Hz [integer]
                               (default = 6000)

    Returns:
        estimates - Formant and bandwidth vectors [dictionary of NumPy vectors]

    The estimates dictionary uses keys like
    'pF1', 'pF2', 'pF3', 'pF4', 'pB1', 'pB2', 'pB3', 'pB4'
    ('pF1' is the first Snack Formant, 'pB2' is the second Snack bandwidth
    vector, etc.) and each entry is a NumPy vector of length data_len.  The
    number of keys corresponds with the number of formants specified.

    Raw Praat estimates are at time points that don't completely match the time
    points in our measurement vectors, so we need to interpolate.  We use a
    crude interpolation method, that has precision set by frame_precision.

    For more information, see the Praat manual page:
        http://www.fon.hum.uva.nl/praat/manual/Sound__To_Formant__burg____.html
    """
    # Compute raw Praat formant estimates
    estimates_raw = praat_raw_formants(wav_fn, praat_path, frame_shift,
                                       window_size, num_formants,
                                       max_formant_freq)

    # Initialize measurement vectors with NaN
    estimates = {}
    for k in estimates_raw:
        if k != 'ptFormants':
            estimates[k] = np.full(data_len, np.nan)

    # Raw Praat estimates are at time points that don't completely match
    # the time points in our measurement vectors, so we need to interpolate.
    # We use a crude interpolation method, that has precision set by
    # frame_precision.

    # Convert time from seconds to nearest whole millisecond
    t_raw_ms = np.int_(round_half_away_from_zero(estimates_raw['ptFormants'] * 1000))

    # Determine start and stop times
    start = 0
    if t_raw_ms[-1] % frame_shift == 0:
        stop = t_raw_ms[-1] + frame_shift
    else:
        stop = t_raw_ms[-1]
    # Iterate through timepoints corresponding to each frame in time range
    for idx_f, t_f in enumerate(range(start, stop, frame_shift)):
        # Find closest time point among calculated Praat values
        min_idx = np.argmin(np.abs(t_raw_ms - t_f))

        # If closest time point is too far away, skip
        if np.abs(t_raw_ms[min_idx] - t_f) > frame_precision * frame_shift:
             continue

        # If index is in range, set measurement value
        if (idx_f >= 0) and (idx_f < data_len):
            for k in estimates_raw:
                if k != 'ptFormants':
                    estimates[k][idx_f] = estimates_raw[k][min_idx]

    return estimates

def praat_raw_formants(wav_fn, praat_path, frame_shift=1, window_size=25, num_formants=4, max_formant_freq=6000):
    """Return raw estimated formants and corresponding time points using Praat

    Args:
        See praat_formants() documentation.
        praat_raw_formants() doesn't have the data_len and frame_precision
        arguments.

    Returns:
        estimates_raw - raw formant and bandwidth estimates plus corresponding
                        time points [dictionary of NumPy vectors]

    The estimates_raw dictionary uses keys like
    'pF1', 'pF2', 'pF3', 'pF4', 'pB1', 'pB2', 'pB3', 'pB4'
    ('pF1' is the first Snack Formant, 'pB2' is the second Snack bandwidth
    vector, etc.) and each entry is a NumPy vector of length data_len.  The
    number of keys corresponds with the number of formants specified.  There
    is always a key 'ptFormants' which corresponds to the vector of time
    points matching the estimated formant and bandwidth vectors.
    """
    # Setup command to call Praat F0 script
    praat_cmd = [praat_path, '--run']
    praat_cmd.append(os.path.join(praat_script_dir, 'praatformants.praat'))
    praat_cmd.extend([os.path.abspath(wav_fn), os.path.splitext(wav_fn)[1]])
    praat_cmd.extend([str(frame_shift / 1000), str(window_size / 1000)])
    praat_cmd.extend([str(num_formants), str(max_formant_freq)])

    # Run Praat F0 script
    return_code = call(praat_cmd)

    if return_code != 0:
        raise OSError('Praat error')

    # Path for Praat output file corresponding to wav_fn
    fmt_fn = wav_fn.split('.')[0] + '.pfmt'
    # Load results from Praat file
    if os.path.isfile(fmt_fn):
        # Praat allows half integer values for num_formants
        # So we round up to get total number of formant columns
        num_cols = 2 + round_half_away_from_zero(num_formants) * 2
        # Define dictionary that uses undef for all columns
        undef_dict = {i: undef for i in range(num_cols)}
        data_raw = np.loadtxt(fmt_fn, dtype=float, skiprows=1, converters=undef_dict)
        # Cleanup and remove Praat file
        os.remove(fmt_fn)
    else:
        raise OSError('Praat error -- unable to locate .pfmt file')

    # Put results into dictionary
    estimates_raw = {}
    estimates_raw['ptFormants'] = data_raw[:, 0]
    for i in range(1, round_half_away_from_zero(num_formants) + 1):
        estimates_raw['pF' + str(i)] = data_raw[:, 2*i]
        estimates_raw['pB' + str(i)] = data_raw[:, 2*i+1]

    return estimates_raw
