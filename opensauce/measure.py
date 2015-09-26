import scipy.io.wavfile as sio
import math
import helpers
import snack_ks
import hnr
from algorithms import func_GetH1_H2_H4

def dummy(soundfile):
    #print soundfile.wavfile
    print "hi from dummy"

def f0_snack(soundfile):
    '''
    Measures f0 using the Snack algorithm.
    '''
    f0 = snack_ks.get_snack_f0(soundfile)
    if not soundfile.measurements.has_key("F0 (Snack)"):
        soundfile.measurements["F0 (Snack)"] = f0
    else:
        print "Already calculated Snack F0 ?"
    return f0


# def a1_a2_a4(soundfile):
# y = soundfile.y
# func_GetA1A2A4(y)

def do_hnr(soundfile):
    y = soundfile.data
    Fs = soundfile.Fs
    soundfile.f0 = f0_snack(soundfile)
    settings = soundfile.settings
    hnr.run(y, Fs, soundfile.f0, settings)

def A1A2A3(soundfile):
    y = soundfile.y
    Fs = soundfile.Fs
    F0 = soundfile.f0
    F1 = soundfile.F1
    F2 = soundfile.F2
    F3 = soundfile.F3
    variables = soundfile.settings
    func_GetA1A2A3.getA1A2A3(y, Fs, F0, F1, F2, F3, variables)

def H1H2H4(soundfile):
    y = soundfile.y
    Fs = soundfile.Fs
    F0 = soundfile.f0
    variables = soundfile.settings
    func_GetH1_H2_H4.getH1_H2_H4(y, Fs, F0, variables)

def H1H2_H2H4(soundfile):
    y = soundfile.y
    Fs = soundfile.Fs
    F0 = soundfile.f0
    F1 = soundfile.F1
    F2 = soundfile.F2
    variables = soundfile.settings
    func_GetH1H2_H2H4.getH1H2_H2H4(H1, H2, H4, Fs, F0, F1, F2)

def H1A1_H1A2_H1A3(soundfile):
    y = soundfile.y
    Fs = soundfile.Fs
    F0 = soundfile.f0
    F1 = soundfile.F1
    F2 = soundfile.F2
    F3 = soundfile.F3
    variables = soundfile.settings
    func_GetH1A1_H1A2_H1A3.getH1A1_H1A2_H1A3(H1, A1, A2, A3, Fs, F0, F1, F2, F3)
    


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
    'H1, H2, H4': H1H2H4,
    'A1, A2, A3': A1A2A3,
    'H1*-H2*, H2*-H4*': H1H2_H2H4,
    'H1*-A1*, H1*-A2*, H1*-A3*': H1A1_H1A2_H1A3,
    'Energy': None,
    'CPP': None,
    'Harmonic to Noise Ratios - HNR': do_hnr, # HG
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
    return measurements[param_label](testfile)


# test('H1, H2, H4')
