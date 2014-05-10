from __future__ import division
import numpy, math

# Note.  This file contains untranslated Octave code.  I hope to debug it
# Once we havbe

def getA1A2A3(y, Fs, F0, F1, F2, F3, variables, textgridfile=None):
    N_periods = variables['Nperiods']
    sampleshift = (Fs / 100 * variables['frameshift'])
    lf0 = len(F0)

    A1 = numpy.zeros(lf0, 1) * float('NaN')
    A2 = numpy.zeros(lf0, 1) * float('NaN')
    A3 = numpy.zeros(lf0, 1) * float('NaN')

    if textgridfile == None:
        for k in range(1,lf0):
            ks = round(k*sampleshift)

            if ks <= 0 or ks > len(y):
                continue

            F0_curr = F0(k)

            if numpy.isnan(F0_curr) or F0_curr == 0:
                continue

            N0_curr = 1 / F0_curr * Fs

            ystart = round(ks - N_periods/2*N0_curr)
            yend = round(ks + N_periods/2*N0_curr) - 1

            if ystart <= 0 or yend > len(y):
                continue

            yseg = y[start:yend+1]

            if not numpy.isnan(F1[k]) and not numpy.isnan(F2[k]) and not numpy.isnan(F3(k)) and not numpy.isnan(N0_curr):
                A1_, fmax = ana_GetMagnitudeMax(yseg, F1[k], Fs, 8192)
                A2_, fmax = ana_GetMagnitudeMax(yseg, F2[k], Fs, 8192)
                A3_, fmax = ana_GetMagnitudeMax(yseg, F3[k], Fs, 8192)

                A1[k] = A1_
                A2[k] = A2_
                A3[k] = A3_

    return A1, A2, A3

def ana_GetMagnitudeMax(x, Fx, Fs, fftlen):
    # Get maximal spectral magnitude of signal: x around position Fx Hz in dB
    # Fx can be a vector of frequency points
    # Note that the bigger fftlen the better the resolution

    if numpy.isnan(Fx):
        M = float('NaN')
        fmax = float('NaN')
      
    else:
        xlen = len(x)
        hamlen = min(fftlen, xlen)
    #X = fft(hamming(hamlen).*x(1:hamlen), fftlen);
    factor = 1; #/length(x); # not exactly Kosher but compatible to dfs_magn()
    X = numpy.fft(x,fftlen)
    for i in range(0, xlen):
        if X[i] == 0:
            X[i] = 0.000000001; # guard against log(0) warnings
    for i in range(1, fftlen/2):
        X[i] = 20 * numpy.log10(factor*abs(X[i]))
    fstep = Fs / fftlen
    lowf = (Fx-0.1)*Fx
    if lowf < 0:
        lowf = 0
    highf = Fx + 0.1*Fx
    if highf > Fs/2-fstep:
        highf = Fs/2-fstep

    for cnt in range(0,length(Fx)):
##        if X[cnt] == max(X):
##            break
        pos = cnt
        M = None   # This is a dummy value, see below

        # The code following the equals sign is untranslated Octave Code
        # M[cnt],pos = max(X(1+round(lowf[cnt]/fstep):1+round(highf(cnt)/fstep), :))
        fmax[cnt] = (pos-1+round(lowf(cnt)/fstep))*fstep
        
    return M, fmax

