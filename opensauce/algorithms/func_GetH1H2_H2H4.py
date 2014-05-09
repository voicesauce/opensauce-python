from __future__ import division
import numpy, math

def getH1H2_H2H4(H1, H2, H4, Fs, F0, F1, F2, B1 = None, B2 = None):
    # [H1H2, H2H4] = func_GetH1H2_H2H4(H1, H2, H4, Fs, F0, F1, F2, B1, B2)
    # Input: H1, H2, H4, vectors
    # Fs - sampling frequency
    # F0 - vector of fundamental frequencies
    # Fx, Bx - vectors of formant frequencies and bandwidths
    # Output: H1A1, H1A2, H1A3 vectors
    # Notes: Function produces the corrected versions of the parameters. They
    # are stored as HxHx for compatibility reasons. Use func_buildMData.m to
    # recreate the mat data with the proper variable names.
    # Also note that the bandwidths from the formant trackers are not currently
    # used due to the variability of those measurements.
    #
    # Author: Yen-Liang Shue, Speech Processing and Auditory Perception Laboratory, UCLA
    # Copyright UCLA SPAPL 2009


    if B1 == None or B2 == None:
        #if either is undefined, get new for both
        B1 = func_getBWfromFMT(F1, F0, 'hm')
        B2 = func_getBWfromFMT(F2, F0, 'hm')


    H1_corr = H1 - func_correct_iseli_z(F0, F1, B1, Fs)
    H1_corr = H1_corr - func_correct_iseli_z(F0, F2, B2, Fs)
    H2_corr = H2 - func_correct_iseli_z(2*F0, F1, B1, Fs)
    H2_corr = H2_corr - func_correct_iseli_z(2*F0, F2, B2, Fs)
    H4_corr = H4 - func_correct_iseli_z(4*F0, F1, B1, Fs)
    H4_corr = H4_corr - func_correct_iseli_z(4*F0, F2, B2, Fs)

    H1H2 = H1_corr - H2_corr
    H2H4 = H2_corr - H4_corr
    return H1H2, H2H4
