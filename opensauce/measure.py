import scipy.io.wavfile as sio
import math
import helpers
import hnr

def dummy(soundfile):
    #print soundfile.wavfile
    print "hi from dummy"

def f0_snack(soundfile):
    '''
    Measures f0 using the Snack algorithm.
    dependencies:
    '''
    print "Not yet implemented: Snack F0"
    return []
    
def do_hnr(soundfile):
    y = soundfile.data
    Fs = soundfile.samplerate
    F0 = f0_snack(soundfile)
    settings = soundfile.settings
    hnr.run(y, Fs, F0, settings)

# dict of pointers to functions that call the measurement functions
measurements = {
    'dummy': dummy,
    'F0 (Straight)': None,
    'F0 (Snack)': f0_snack,
    'F0 (Praat)': None,
    'F0 (SHR)': None,
    'F0 (Other)': None,
    'F1, F2, F3, F4 (Snack)': None,
    'F1, F2, F3, F4 (Praat)': None,
    'F1, F2, F3, F4 (Other)': None,
    'H1, H2, H4': None,
    'A1, A2, A3': None,
    'H1*-H2*, H2*-H4*': None,
    'H1*-A1*, H1*-A2*, H1*-A3*': None,
    'Energy': None,
    'CPP': None,
    'Harmonic to Noise Ratios - HNR': do_hnr,
    'Subharmonic to Harmonic Ratio - SHR': None
}

def generate_test_file(wavfile):
    '''
    Generates a file from a wave file in defaults/sounds to use for testing purposes
    '''
    global tester
    sf = "../defaults/settings/default.csv"
    pf = "../defaults/parameters/default.csv"
    settings = helpers.get_settings(sf)
    params = helpers.get_parameters(pf)
    Fs, data = sio.read(wavfile)
    data_len = math.floor(len(data) / Fs * 1000 / int(settings['frameshift']))
    soundfile = helpers.SoundFile(settings, wavfile)
    return soundfile

def test(param_label):
    '''
    Test a measurement function.
    Example usage: test('F0 (Snack)')
    '''
    testfile = generate_test_file("../defaults/sounds/cant_c5_19a.wav")
    #print testfile.settings
    return measurements[param_label](testfile)

test('Harmonic to Noise Ratios - HNR')

