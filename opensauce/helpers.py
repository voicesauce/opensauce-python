from __future__ import division

import math

import numpy
from scipy.io import wavfile


def wavread(fn):
    """Emulate the parts of the matlab wavread function that we need.

        y, Fs = wavread(fn)

    y is the vector of audio samples, Fs is the frame rate.

    Matlab's wavread is used by voicesauce to read in the wav files for
    processing.  As a consequence, all the translated algorithms assume the
    data from the wav file is in matlab form, which in this case means a double
    precision float between -1 and 1.  The corresponding scipy function returns
    the actual integer PCM values from the file, which range between -32768 and
    32767.  (matlab's wavread *can* return the integers, but does not by
    default and voicesauce uses the default).  Consequently, after reading the
    data using scipy's io.wavfile, we convert to float by dividing each integer
    by 32768.

    """
    # For reference, I figured this out from:
    # http://mirlab.org/jang/books/audiosignalprocessing/matlab4waveRead.asp?title=4-2%20Reading%20Wave%20Files
    # XXX: if we need to handle 8 bit files we'll need to detect them and
    # special case them here.
    Fs, y = wavfile.read(fn)
    return y/numpy.float64(32768.0), Fs
