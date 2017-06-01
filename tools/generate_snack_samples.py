import os
import glob
from opensauce.snack import snack_pitch
from test.support import save_sample_data

def main():

    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    wav_files = glob.glob(os.path.join(cur_dir, 'test', 'data', '*.wav'))

    method = 'tcl'
    for wav_file in wav_files:
        F0, V = snack_pitch(wav_file, method, frame_length=0.001, window_length=0.025, max_pitch=500, min_pitch=40)
        wav_basename = os.path.basename(wav_file)
        save_sample_data(F0, wav_basename, 'sF0', 'sf0', '1ms')
        save_sample_data(V, wav_basename, 'V', 'sf0', '1ms')

if __name__ == '__main__':
    main()
