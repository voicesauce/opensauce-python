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


class SoundFile:
    def __init__(self, settings, wavfile):
        self.settings = settings
        self.wavfile = wavfile # path to wavfile
        self.matfile = None
        self.y = None
        self.Fs = None # corresponds to Fs in opensauce
        self.data_len = None
        self.f0 = None
        self.measurements = {}
        self.build()

    def build(self):
        self.get_matfile()
        self.read_in()
        self.calc_data_len()

    def get_matfile(self):
        return self.wavfile[:-3]+"mat"

    def read_in(self):
        y, Fs = wavread(self.wavfile)
        self.samplerate = Fs
        self.data = y

    def calc_data_len(self):
        self.data_len = math.floor(len(self.data) / self.samplerate * 1000 / int(self.settings['frameshift']))

def get_parameters(parameter_file):
    '''
    Read in parameters file
    :rtype : list
    '''
    on = []
    with open(parameter_file, "r") as f:
        for line in f.readlines():
            line = line.split("|")
            line = [i.strip() for i in line]
            if line[1] == '1':
                p = line[0].strip()
                on.append(p)
    return on

def get_settings(settings_file):
    '''
     Reads in settings file.
     TODO parse each setting and convert to int/floats where appropriate
     :rtype : dict
    '''
    settings = {}
    with open(settings_file, "r") as f:
        for line in f.readlines():
            line = line.split(",")
            settings[line[0]] = line[1]
    return settings
