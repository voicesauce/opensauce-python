"""A sound file (a wav file) undergoing analysis.

Loads the data from the sound file on disk, and provides methods for accessing
the sound data and, if it exists, associated textgrid annotation information.

"""

from __future__ import division

import math
import os

from opensauce.helpers import wavread
from opensauce.textgrid import TextGrid

class SoundFile(object):

    def __init__(self, wavpath, tgdir=None, tgfn=None):
        """Load sound data from wavpath and TextGrid from tgdir+tgfn.

        If tgdir is not specified look for the TextGrid in the same directory
        as the sound file.  if tgfn is not specified, look for a file with
        the same name as the sound file and an extension of 'TextGrid'.

        The returned SoundFile object has the following useful attributes:

            wavpath                 The original path specified in the
                                        constructor.
            wavfn                   The filename component of wavpath.
            wavdata                 An ndarray of the wavfile samples
            fs                      The number of samples per second
            tgpath                  Full path to the textgrid file.
            textgrid                A TextGrid object loaded from tgpath if
                                        a file exists at tgpath, else None.
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
        self.wavfn = os.path.split(self.wavpath)[1]
        if tgfn is None:
            tgfn = os.path.splitext(os.path.basename(wavpath))[0] + '.TextGrid'
        if tgdir is None:
            tgdir = os.path.dirname(wavpath)
        self.tgpath = os.path.join(tgdir, tgfn)

    @property
    def wavdata(self):
        return self._wavdata()[0]

    @property
    def fs(self):
        return self._wavdata()[1]

    def _wavdata(self):
        data, fs = wavread(self.wavpath)
        self.__dict__['wavdata'], self.__dict__['fs'] = data, fs
        return data, fs

    @property
    def ms_len(self):
        ms_len = math.floor(len(self.wavdata) / self.fs * 1000)
        self.__dict__['ms_len'] = ms_len
        return ms_len

    @property
    def textgrid(self):
        if os.path.exists(self.tgpath):
            res = TextGrid.load(self.tgpath)
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
            if tier.classid.lower() != 'intervaltier':
                continue
            for start, stop, label in tier.simple_transcript:
                res.append((label, float(start), float(stop)))
        self.__dict__['textgrid_intervals'] = res
        return res
