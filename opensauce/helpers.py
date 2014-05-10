from __future__ import division
import scipy.io.wavfile as sio
import math

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
        Fs, data = sio.read(self.wavfile)
        self.samplerate = Fs
        self.data = data

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
