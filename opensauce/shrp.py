from __future__ import division

import numpy as np
from scipy.fftpack import fft
from scipy.interpolate import interp1d

"""
SHRP - a pitch determination algorithm based on Subharmonic-to-Harmonic Ratio.

Based on the shrp.m from voicesauce v1.25.  Per that file, for details of the
algorithm, please see Sun, X.,"Pitch determination and voice quality analysis
using subharmonic-to-harmonic ratio" To appear in the Proc. of ICASSP2002,
Orlando, Florida, May 13 -17, 2002.  For update information, please check
http://mel.speech.nwu.edu/sunxj/pda.htm.

XXX: This is not a full re-implementation of shrp.m: it only implements those
functions actually used by the voicesauce func_GetSHRP function.

"""
# XXX This is a work in progress, working from the bottommost functions up.
# Function definitions are ordered the same as in the matlab source.
# Comments in quotes are copied from the matlab source.


# ---- GetLogSpectrum -----

def get_log_spectrum(segment, fftlen, limit, logf, interp_logf):
    spectra = fft(segment, fftlen)
    # "fftlen is always even here."
    amplitude = np.abs(spectra[0:fftlen/2+1])
    # "ignore the zero frequency component"
    amplitude = amplitude[1:limit+1]
    interp_amplitude = interp1d(logf, amplitude)(interp_logf)
    interp_amplitude = interp_amplitude - min(interp_amplitude)
    return interp_amplitude


# ---- ComputeSHR -----

def compute_shr(log_spectrum, min_bin, startpos, endpos, lowerbound, upperbound,
                n, shift_units, shr_threshold):
    """ "compute subharmonic-to-harmonic ratio for a short-term signal"

       returns peak_index = -1 if frame appears to be unvoiced.
    """
    len_spectrum = len(log_spectrum)
    total_len = shift_units + len_spectrum
    # "initialize the subharmonic shift matrix; each row corresponds to a shift
    # version"
    shshift = np.zeros((n, total_len))
    # "place the spectrum at the right end of the first row"
    shshift[0, total_len-len_spectrum:total_len] = log_spectrum
    # "note that here startpos and endpos has n-1 rows, so we start from 2"
    # "the first row in shshift is the original log spectrum"
    # Actually we start from 1 since python is zero-origined.
    for i in range(1, n):
        # "store each shifted sequence"
        shshift[i, startpos[i-1]:endpos[i-1]+1] = (
            log_spectrum[:endpos[i-1]-startpos[i-1]+1])
    # "we don't need the stuff smaller than shift_units"
    shshift = shshift[:, shift_units:total_len]
    # odd and even are reversed from matlab due to different origin
    shseven = sum(shshift[0:n:2, :], 0)
    shsodd = sum(shshift[1:n-1:2, :], 0)
    difference = shsodd - shseven
    # "peak picking process"
    shr = 0
    # "only find two maxima"
    mag, index = two_max(difference, lowerbound, upperbound, min_bin)
    # "first mag is always the maximum, the second, if there is, is the second
    # max"
    num_pitch_candidates = len(mag)
    if num_pitch_candidates == 1:
        # "this is possible, mainly due to we put a constraint on search region,
        # i.e., f0 range"
        if mag <= 0:
            # "this must be an unvoiced frame"
            peak_index = -1;
            return peak_index, shr, shshift, index
        peak_index = index
        shr = 0
    else:
        shr = (mag[1]-mag[2]) / (mag[1]+mag[2])
        if shr <= shr_threshold:
            # "subharmonic is weak, so favor the harmonic"
            peak_index = index[2]
        else:
            # "subharmonic is strong, so favor the subharmonic as F0"
            peak_index = index[1]
    return peak_index, shr, shshift, index


# ---- twomax -----

def two_max(x, lowerbound, upperbound, unit_len):
    """Return up to two successive maximum peaks and their indices in x.

    Return the magnitudes of the peaks and the indices as two lists.
    If the first maximum is less than zero, just return it.  Otherwise
    look to the right of the first maximum, and if there is a second
    maximum that is greater than zero, add that to the returned lists.

    """
    # XXX The above description is not completely accurate: there's a window to
    # the search for the second peak, but I don't understand the goal well
    # enough to describe it better, and the original comments are less precise.
    max_index = min(upperbound, len(x)-1)
    # "find the maximum value"
    mag = np.array([np.amax(x[lowerbound:upperbound])])
    index = np.where(x == mag)[0]
    if mag < 0:
        return mag, index
    harmonics=2
    limit=0.0625; # "1/8 octave"
    startpos = index[0] + round(np.log2(harmonics-limit)/unit_len)
    if startpos <= max_index:
        # "for example, 100hz-200hz is one octave, 200hz-250hz is 1/4octave"
        endpos = index[0] + round(np.log2(harmonics + limit)/unit_len)
        endpos = min(max_index, endpos)
        # "find the maximum value at right side of last maximum"
        mag2 = np.amax(x[startpos:endpos+1])
        index2 = np.where(x[startpos:] == mag2)[0][0] + startpos
        if mag2 > 0:
            mag = np.append(mag, mag2)
            index = np.append(index, index2)
    return mag, index


# ---- vda -----
# func_Get_SHRP does not use this, because CHECK_VOICING is always 0
def vda(x, segmentdur, noisefloor, minzcr):
    raise NotImplementedError


# ---- ethreshold -----
# Although present in the matlab source this function is not used.

def ethreshold(frames):
    """Determine energy threshold for silence."""
    raise NotImplementedError


# ---- toframes ----

def toframes(samples, curpos, segmentlen, window_type):
    last_index = len(samples) - 1
    num_frames = len(curpos)
    start = curpos - int(round(segmentlen/2))
    offset = np.arange(segmentlen)
    index_start = np.nonzero(start < 1)[0]
    start[index_start] = 0
    endpos = start + segmentlen - 1
    index = np.nonzero(endpos > last_index)[0]
    endpos[index] = last_index
    start[index] = last_index + 1 - segmentlen
    frames = samples[
        (np.tile(np.expand_dims(start, 1), (1, segmentlen))
         + np.tile(offset, (num_frames, 1)))]
    window_vector = np.tile(window(segmentlen, window_type), (num_frames, 1))
    return np.multiply(frames, window_vector)


# ---- voicing ----
# func_Get_SHRP does not use these, because CHECK_VOICING is always 0

def postvda(segment, curf0, Fs, r_threshold):
    raise NotImplementedError

def zcr(x, dur):
    raise NotImplementedError

# ---- window -----
def _pi_arange(width):
    return 2*np.pi*np.arange(width)/(width-1)

def _not_implemented():
    raise NotImplementedError

def _triangular(n):
    m = (n-1)/2
    res = np.arange(np.floor(m+1))/m
    return np.append(res, res[np.ceil(m)-1::-1])

window_funcs = dict(
    rect = lambda n: np.ones(n),
    tria = _triangular,
    hann = lambda n: 0.5*(1 - np.cos(_pi_arange(n))),
    hamm = lambda n: 0.54 - 0.46*np.cos(_pi_arange(n)),
    blac = lambda n: (0.42 - 0.5*np.cos(_pi_arange(n))
                      + 0.08*np.cos(2*_pi_arange(n))),
    kais = lambda n: _not_implemented(),
    )

def window(width, window_type, beta=None):
    """Generate a window function (1 dim ndarray) of length width.

    Given a window_type from the list 'rectangular', 'triangular', 'hanning',
    'hamming', 'blackman', 'kaiser', or at least the first four characters of
    one of those strings, return a 1 dimensional ndarray of floats expressing a
    window function of length 'width' using the 'window_type'.  'beta' is an
    additional input for the kaiser algorithm.  (XXX: kaiser is not currently
    implemented.)

    """
    algo = window_funcs.get(window_type[:4])
    if algo is None:
        raise ValueError(
            "Unknown window algorithm type {!r}".format(window_type))
    return algo(width)
