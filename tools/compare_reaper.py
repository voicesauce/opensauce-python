import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt

from subprocess import call
from scipy.io import wavfile
from pyreaper import reaper


def main(wav_dir, reaper_path):
    """Compare output from pyreaper with original REAPER
    """
    # Find all wavfiles
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))
    
    for fn in wav_files:
        # Run pyreaper on wavfile
        fs, y = wavfile.read(fn)
        pm_times, pm, F0_times, F0, corr = reaper(y, fs, minf0=40,
                                                  maxf0=500,
                                                  do_high_pass=True,
                                                  do_hilbert_transform=False,
                                                  inter_pulse=0.01,
                                                  frame_period=0.001)
        
        #np.savetxt('pyreaper-f0.txt', np.vstack([F0_times, F0]).T, fmt='%10.5f')
        
        # Run REAPER on wavfile
        
        # Output file names
        reaper_f0_fn = 'reaper-f0.txt'
        reaper_pitchmarks_fn = 'reaper-pitchmarks.txt'
        reaper_corr_fn = 'reaper-corr.txt'
        
        # Run REAPER command
        cmd = [reaper_path, '-i', fn]
        cmd.extend(['-f', reaper_f0_fn])
        cmd.extend(['-p', reaper_pitchmarks_fn])
        cmd.extend(['-c', reaper_corr_fn])
        cmd.extend(['-e', '0.001'])
        cmd.extend(['-x', '500.0'])
        cmd.extend(['-m', '40.0'])
        cmd.extend(['-u', '0.01'])
        cmd.extend(['-a'])
        
        return_code = call(cmd)
        
        rF0_times, x, rF0 = np.loadtxt(reaper_f0_fn, skiprows=7, unpack=True)
        rF0_found = x.astype(int)
        rpm_times, y, rpm = np.loadtxt(reaper_pitchmarks_fn, skiprows=7, unpack=True)
        rpm_found = y.astype(int)
        rcorr_times, z, rcorr = np.loadtxt(reaper_corr_fn, skiprows=7, unpack=True)
        rcorr_found = z.astype(int)
    
        bname = os.path.basename(fn)
        print('{}: pyreaper length {} ms, REAPER length {} ms'.format(bname, F0_times[-1]*1000, rF0_times[-1]*1000))
        
        plt.figure()
        plt.plot(rF0_times*1000, rF0, 'bo', markersize=6, fillstyle='none')
        plt.plot(F0_times*1000, F0, 'r+', markersize=2)
    #   plt.plot(rF0_times[rF0_found == 1]*1000, rF0[rF0_found == 1], 'bo', markersize=6, fillstyle='none')
    #   plt.plot(F0_times[F0 > 0]*1000, F0[F0 > 0], 'r+', markersize=2)
     
        plt.title(bname)
        plt.xlabel('Time (ms)')
        plt.ylabel('F0 (Hz)')
    #   plt.savefig(os.path.splitext(bname)[0] + '.png')
    
    plt.show()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
