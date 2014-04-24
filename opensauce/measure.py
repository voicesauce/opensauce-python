import scipy.io.wavfile as sio
import math
import helpers
<<<<<<< HEAD
import hnr
=======
import snack_ks
# import algorithms.H1H2H4
# import algorithms.func_GetA1A2A4
>>>>>>> 2b46bda491c8c60cb4ceeecda0690af100579aa2

def dummy(soundfile):
    #print soundfile.wavfile
    print "hi from dummy"

def f0_snack(soundfile):
    '''
    Measures f0 using the Snack algorithm.
    '''
<<<<<<< HEAD
    print "Not yet implemented: Snack F0"
    return []
    
def do_hnr(soundfile):
    y = soundfile.data
    Fs = soundfile.samplerate
    F0 = f0_snack(soundfile)
    settings = soundfile.settings
    hnr.run(y, Fs, F0, settings)
=======
    f0 = snack_ks.get_snack_f0(soundfile)
    if not soundfile.measurements.has_key("F0 (Snack)"):
        soundfile.measurements["F0 (Snack)"] = f0
    else:
        print "Already calculated Snack F0 ?"
    return f0



# def a1_a2_a4(soundfile):
#     y = soundfile.y
#     func_GetA1A2A4(y)

# def hnr(soundfile):
#     y = soundfile.data
#     Fs = soundfile.samplerate
#     f0 = f0_snack(soundfile)
#     settings = soundfile.settings
#     hnr.run(y, Fs, f0, settings)



>>>>>>> 2b46bda491c8c60cb4ceeecda0690af100579aa2

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
    'H1, H2, H4': None, # LP
    'A1, A2, A3': None, # LP
    'H1*-H2*, H2*-H4*': None, # LP
    'H1*-A1*, H1*-A2*, H1*-A3*': None, # LP
    'Energy': None,
<<<<<<< HEAD
    'CPP': None,
    'Harmonic to Noise Ratios - HNR': do_hnr,
=======
    'CPP': None, # LS
    'Harmonic to Noise Ratios - HNR': None, # HG
>>>>>>> 2b46bda491c8c60cb4ceeecda0690af100579aa2
    'Subharmonic to Harmonic Ratio - SHR': None
}

def generate_test_file(wavfile):
    '''
    Generates a file from a wave file in defaults/sounds to use for testing purposes
    '''
    global tester
    sf = "defaults/settings/default.csv"
    pf = "defaults/parameters/default.csv"
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
<<<<<<< HEAD
    testfile = generate_test_file("../defaults/sounds/cant_c5_19a.wav")
    #print testfile.settings
    return measurements[param_label](testfile)

test('Harmonic to Noise Ratios - HNR')
=======
    testfile = generate_test_file("defaults/sounds/cant_c5_19a.wav")
    return measurements[param_label](testfile)

# print test("F0 (Snack)")
# test('Harmonic to Noise Ratios - HNR')
# test('A1, A2, A3')

>>>>>>> 2b46bda491c8c60cb4ceeecda0690af100579aa2

