from __future__ import division
import numpy, math

def getH1A1_H1A2_H1A3(H1, A1, A2, A3, Fs, F0, F1, F2, F3, B1=None, B2=None, B3=None):
    # [H1A1, H1A2, H1A3] = func_GetH1A1_H1A2_H1A3(H1, A1, A2, A3, Fs, F0, F1, F2, F3, B1, B2, B3)
    # Input: H1, A1, A2, A3 vectors
    # Fs - sampling frequency
    # F0 - vector of fundamental frequencies
    # Fx, Bx - vectors of formant frequencies and bandwidths
    # Output: H1A1, H1A2, H1A3 vectors
    # Notes: Function produces the corrected versions of the parameters. They
    # are stored as HxAx for compatibility reasons. Use func_buildMData.m to
    # recreate the mat data with the proper variable names.
    # Also note that the bandwidths from the formant trackers are not currently
    # used due to the variability of those measurements.
    #
    # Author: Yen-Liang Shue, Speech Processing and Auditory Perception Laboratory, UCLA
    # Copyright UCLA SPAPL 2009

    if B1 == None or B2 == None or B3 == None:
        #If any of these are undefined, get new ones
        B1 = func_getBWfromFMT(F1, F0, 'hm')
        B2 = func_getBWfromFMT(F2, F0, 'hm')
        B3 = func_getBWfromFMT(F3, F0, 'hm')

    H1_corr = H1 - func_correct_iseli_z(F0, F1, B1, Fs)
    H1_corr = H1_corr - func_correct_iseli_z(F0, F2, B2, Fs)
    #H1_corr = H1_corr - func_correct_iseli_z(F0, F3, B3, Fs)

    A3_corr = A3 - func_correct_iseli_z(F3, F1, B1, Fs)
    A3_corr = A3_corr - func_correct_iseli_z(F3, F2, B2, Fs)
    A3_corr = A3_corr - func_correct_iseli_z(F3, F3, B3, Fs)

    A1_corr = A1 - func_correct_iseli_z(F1, F1, B1, Fs)
    A1_corr = A1_corr - func_correct_iseli_z(F1, F2, B2, Fs)

    A2_corr = A2 - func_correct_iseli_z(F2, F1, B1, Fs)
    A2_corr = A2_corr - func_correct_iseli_z(F2, F2, B2, Fs)

    H1A1 = H1_corr - A1_corr
    H1A2 = H1_corr - A2_corr
    H1A3 = H1_corr - A3_corr
    return H1A1, H1A2, H1A3

