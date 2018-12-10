"""A sound file (a wav file) undergoing analysis.

Loads the data from the sound file on disk, and provides methods for accessing
the sound data and, if it exists, associated textgrid annotation information.

"""

# Licensed under Apache v2 (see LICENSE)

from __future__ import division

import math
import os
import numpy as np

from scipy.signal import resample
from scipy.io import wavfile

from opensauce.helpers import wavread
from opensauce.textgrid import TextGrid, IntervalTier


class SoundFile(object):

    def __init__(self, wavpath, tgdir=None, tgfn=None, resample_freq=None):
        """Load sound data from wavpath and TextGrid from tgdir+tgfn.  If
        resample_freq is specified, then also resample the sound data and
        save the resampled data, in addition to the original data.

        Assume that input wav files are 16-bit PCM (integers between -32767
        and 32767).  Output resampled wav files are also written as 16-bit
        PCM.

        If tgdir is not specified look for the TextGrid in the same directory
        as the sound file.  if tgfn is not specified, look for a file with
        the same name as the sound file and an extension of 'TextGrid'.

        The returned SoundFile object has the following useful attributes:

            wavpath                 The original path specified in the
                                    constructor.
            wavfn                   The filename component of wavpath.
            wavdata                 An ndarray of wavfile samples (float)
            wavdata_int             An ndarray of wavfile sample (16-bit int)
            fs                      The number of samples per second
            ns                      Total number of samples
            wavpath_rs              Path for wav file corresponding to
                                    resampled data
            wavdata_rs              An ndarray of wavfile float samples after
                                    resampling (None if resample_freq = None)
            wavdata_rs_int          An ndarray of wavfile 16-bit int samples after
                                    resampling (None if resample_freq = None)
            fs_rs                   The number of samples per second after
                                    resampling (None if resample_freq = None)
            ns_rs                   Total number of samples after resampling
                                    (None if resample_freq = None)
            tgpath                  Full path to the textgrid file.
            textgrid                A TextGrid object loaded from tgpath if a
                                    file exists at tgpath, else None.
            textgrid_intervals      A list of three tuples of the form
                                    (label, start, stop), where label is a
                                    text interval label and start and stop
                                    are floating point numbers of seconds
                                    from the start of the file of the
                                    beginning and end of the interval.  The
                                    list is a concatenation of all TextGrid
                                    tiers of type 'intervaltier', in the
                                    order they occur in the TextGrid.

            The textgrid_intervals attribute exists if and only if the TextGrid
            file exists.

        """
        open(wavpath).close()   # Generate an error if the file doesn't exist.
        self.wavpath = wavpath
        self.wavfn = os.path.basename(self.wavpath)
        if tgfn is None:
            tgfn = os.path.splitext(os.path.basename(wavpath))[0] + '.TextGrid'
        if tgdir is None:
            tgdir = os.path.dirname(wavpath)
        self.tgpath = os.path.join(tgdir, tgfn)
        # Check that resample_freq has valid value
        if resample_freq is not None:
            if not isinstance(resample_freq, int):
                raise ValueError('Resample frequency must be an integer')
            if resample_freq <= 0:
                raise ValueError('Resample frequency must be positive')
        self.fs_rs = resample_freq

    @property
    def wavdata(self):
        return self._wavdata()[0]

    @property
    def wavdata_int(self):
        return self._wavdata()[1]

    @property
    def fs(self):
        return self._wavdata()[2]

    @property
    def ns(self):
        return len(self.wavdata)

    def _wavdata(self):
        data, data_int, fs = wavread(self.wavpath)
        self.__dict__['wavdata'], self.__dict__['fs'] = data, fs
        return data, data_int, fs

    @property
    def wavpath_rs(self):
        return self._wavdata_rs()[0]

    @property
    def wavdata_rs(self):
        return self._wavdata_rs()[1]

    @property
    def wavdata_rs_int(self):
        return self._wavdata_rs()[2]

    @property
    def ns_rs(self):
        return self._wavdata_rs()[3]

    def _wavdata_rs(self):
        if self.fs_rs is not None:
            # Number of points in resample
            ns_rs = np.int_(np.ceil(self.ns * self.fs_rs / self.fs))
            # Do resample
            # XXX: Tried using a Hamming window as a low pass filter, but it
            #      didn't seem to make a big difference, so it's not used
            #      here.
            data_rs = resample(self.wavdata, ns_rs)
            wavpath_rs = self.wavpath.split('.')[0] + '-resample-' + str(self.fs_rs) + 'Hz.wav'
            # Write resampled data to wav file
            # Convert data from 32-bit floating point to 16-bit PCM
            data_rs_int = np.int16(data_rs * 32768)
            wavfile.write(wavpath_rs, self.fs_rs, data_rs_int)
            # XXX: Was worried that Python might continue executing code
            #      before the file write is finished, but it seems like it's
            #      not an issue.
            return wavpath_rs, data_rs, data_rs_int, ns_rs
        else:
            return None, None, None, None

    @property
    def ms_len(self):
        ms_len = int(math.floor(len(self.wavdata) / self.fs * 1000))
        self.__dict__['ms_len'] = ms_len
        return ms_len

    @property
    def textgrid(self):
        if os.path.exists(self.tgpath):
            res = TextGrid.fromFile(self.tgpath)
        else:
            res = None
        self.__dict__['textgrid'] = res
        return res

    @property
    def textgrid_intervals(self):
        if self.textgrid is None:
            raise ValueError("Textgrid file {!r} not found".format(self.tgpath))
        res = []
        for tier in self.textgrid.tiers:
            if tier.__class__ != IntervalTier:
                continue
            for i in tier.intervals:
                res.append((i.mark, float(i.minTime), float(i.maxTime)))
        self.__dict__['textgrid_intervals'] = res
        return res
