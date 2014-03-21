__author__ = 'kate'
import sys
import os
import scipy.io.wavfile as sio
import math

class Instance:
    def __init__(self, wavfile, matfile, data, samplerate, data_len):
        self.wavfile = wavfile
        self.matfile = matfile
        self.data = data
        self.samplerate = samplerate
        self.data_len = data_len

def get_params(parameter_file):
    return None

def get_settings(settings_file):
    return None

def dummy(instance):
    print "hi from dummy"

# dict of pointers to functions that call the measurement functions
measurements = {
    "dummy": dummy
}



def start():
    usage = "usage: python runner [input directory] [output directory]"
    print "starting OpenSauce..."
    if len(sys.argv) != 3:
        print usage
    indir = sys.argv[1]
    outdir = sys.argv[2]
    process(indir, outdir)

def init(indir, outdir):
    return None

def process(indir, outdir):
    print "processing..."
    # TODO getSettings
    # TODO getParamlist
    params = ['dummy']
    # params = get_params(parameter_file)
    # settings = get_settings(settings_file)
    frameshift = 1
    print indir
    print outdir
    # make a list of wav files
    # TODO fix this so it uses absolute file paths (os.getenv)
    if indir[-1] != '/':
        indir = indir + '/'
    filelist = [indir+f for f in os.listdir(indir) if f.endswith('.wav')]
    print filelist
    for wav in filelist:
        print "Processing ", wav
        matfile = wav[:-3]+"mat"
        # TODO TextGrid stuff
        # read in wave file
        # Fs = sample rate, data = channel data
        Fs, data = sio.read(wav)
        data_len = math.floor(len(data) / Fs * 1000 / frameshift)
        instance = Instance(wav, matfile, data, Fs, data_len)
        # TODO paramlist
        # TODO doFunction
        for param in params:
            measurements[param](instance)
    print "Done processing."






if __name__ == "__main__":
    start()