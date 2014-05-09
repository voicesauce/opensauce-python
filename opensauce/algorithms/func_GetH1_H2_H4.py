from __future__ import division
import numpy, math

def getH1_H2_H4(y, Fs, F0, variables, textgridfile=None):
# Input: y, Fs - from wavread
        # F0 - vector of fundamental frequencies
        # variables - global settings
        # textgridfile - this is optional
        # Output: H1, H2, H4 vectors
        # isComplete - flag to indicate if the process was allowed to
        # finish
        # Notes: Function is quite slow! Use textgrid segmentation to speed up the
        # process.
        #
        # Author: Yen-Liang Shue, Speech Processing and Auditory Perception Laboratory, UCLA
        # Copyright UCLA SPAPL 2009

        # Modified by KS 2013-08-05

    N_periods = variables['Nperiods']
    sampleshift = (Fs / 1000 * variables['frameshift'])

    H1 = numpy.zeros(len(F0), 1) * float('NaN')
    H2 = numpy.zeros(len(F0), 1) * float('NaN')
    H4 = numpy.zeros(len(F0), 1) * float('NaN')

    isComplete = 0

    if textgridfile == None: # don't use Textgrid
        for k in range(1, length(F0)):
            ks = round(k * sampleshift) 
            if ks <= 0 or ks > length(y):
                continue
            
            F0_curr = F0(k)
            if numpy.isnan(F0_curr) or F0_curr == 0:
                continue

            N0_curr = 1 / F0_curr * Fs
                            
            ystart = round(ks - N_periods/2*N0_curr)
            yend = round(ks + N_periods/2*N0_curr) - 1
            
            if ystart <= 0:
                continue

            if yend > length(y):
                continue

            yseg = y[ystart:yend+1]
            
            # what are f0, dummy for? FIXME?
            h1, f0  = func_GetHarmonics(yseg, F0_curr, Fs)
            h2, dummy = func_GetHarmonics(yseg, 2*F0_curr, Fs)
            h4, dummy = func_GetHarmonics(yseg, 4*F0_curr, Fs)

            H1[k] = h1
            H2[k] = h2
            H4[k] = h4

    isComplete = 1

    return H1, H2, H4, isComplete

# # this function is used from 1/8/09 onwards - optimization used
# #--------------------------------------------------------------------------
# function [h,fh]=func_GetHarmonics(data,f_est,Fs)
# see func_GetHarmonics.m

# This function was used up to 1/8/09
# #--------------------------------------------------------------------------
# function [h,f]=func_GetHarmonics_old(x,f_est,Fs,df_range)
# # find harmonic magnitudes in dB of time signal x
# # around a frequency estimate f_est
# # Fs, sampling rate
# # x, input row vector (is truncated to the first 25ms)
# # df_range, optional, default +-5# of f_est

# df = 0.1; # search around f_est in steps of df (in Hz)
# if nargin<4
# df_range = round(f_est*0.1); # search range (in Hz)
# end
# f = f_est-df_range:df:f_est+df_range;
# f = f(:); # make column vector

# #x = x(1:round(Fs*0.025)); # analyze 25ms
# #x = hamming(length(x)).*x;
# n = 0:length(x)-1;
# v = exp(-i*2*pi*f*n/Fs);
# h = 20*log10(abs(x' * v.' ));
# #figure; plot(f,h);
# [h,inx]=max(h);
# f=f(inx);
