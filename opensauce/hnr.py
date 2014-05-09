# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 21:51:49 2014

@author: Helene
"""
import numpy as np

def run(y, Fs, F0, variables):
    """
    INPUT
    y, FS - fr wav-read
    F0 - vector of fundamental frequency
    variables - global settings
    
    OUTPUT
    N vectors
    
    NOTES
    Calculates the harmonic to noise ration based on the method described in de 
    Krom, 1993 - A cepstrum-based technique for determining a harmonic-to-noise 
    ratio in speech signals, JSHR.
    
    AUTHOR
    Yen-Liang Shue, Speech Processing and Auditory Perception Laboratory, UCLA
    Copyright UCLA SPAPL 2009
    """
    N_periods = int(variables['Nperiods_EC'])
    sampleshift = (Fs / (1000 * int(variables['frameshift'])))
           
    HNR05 = np.zeros(len(F0)) * None
    HNR15 = np.zeros(len(F0)) * None
    HNR25 = np.zeros(len(F0)) * None
    HNR35 = np.zeros(len(F0)) * None
    
    print 'reached the first for loop'
    for k in range(1, len(F0)): #check this with the k multiplcation stuff below
        print 'loop!'
        ks = round(k * sampleshift)
        
        if ks <= 0 or ks > len(y):
            continue
        
        F0_curr = F0[k]
        
        if F0_curr == 0:
            continue
        
        N0_curr = 1/(F0_curr * Fs)
        
        if not F0_curr:
            continue
        
        ystart = round(ks - N_periods/2*N0_curr)
        yend = round(ks + N_periods/2*N0_curr)-1
        
        if (yend-ystart + 1) % 2 == 0:
            yend -= 1
            
        if ystart <= 0 or yend > len(y):
            continue
        
        yseg = y[ystart:yend]
        
        hnr = getHNR(yseg, Fs, F0_curr, [500, 1500, 2500, 3500])
        
        HNR05[k] = hnr[0]
        HNR15[k] = hnr[1]
        HNR25[k] = hnr[2]
        HNR35[k] = hnr[3]
    
    return [HNR05, HNR15, HNR25, HNR35]

def getHNR(y, Fs, F0, Nfreqs):
    print 'holla'
    NBins = len(y)
    N0 = round(Fs/F0)
    N0_delta = round(N0 * 0.1)
    
    y = [x*z for x,z in zip(np.hamming(len(y)),y)]
    fftY = np.fft(y, NBins)
    aY = np.log10(abs(fftY))
    ay = np.ifft(aY)
    
    peakinx = np.zeros(np.floor(len(y))/2/N0)
    for k in range(1, len(peakinx)):
        ayseg = ay[k*N0 - N0_delta : k*N0 + N0_delta]
        val, inx = max(abs(ayseg)) #MAX does not behave the same - doesn't return inx??
        peakinx[k] = inx + (k * N0) - N0_delta - 1
        
        s_ayseg = np.sign(np.diff(ayseg))
        
        l_inx = inx - np.find((np.sign(s_ayseg[inx-1:-1:1]) != np.sign(inx)))[0] + 1
        r_inx = inx + np.find(np.sign(s_ayseg[inx+1:]) == np.sign(inx))[0]
        
        l_inx = l_inx + k*N0 - N0_delta - 1
        r_inx = r_inx + k*N0 - N0_delta - 1
        
        for num in range(l_inx, r_inx):
            ay[num] = 0
        
    midL = round(len(y)/2)+1
    ay[midL:] = ay[midL-1: -1 : midL-1-(len(ay)-midL)]
    
    Nap = np.real(np.fft(ay))
    N = Nap #???? why?
    Ha = aY - Nap #change these names ffs
    
    Hdelta = F0/Fs * len(y)
    for f in [num+0.0001 for num in range(Hdelta, round(len(y)/2), Hdelta)]:
        fstart = np.ceil(f - Hdelta)
        Bdf = abs(min(Ha[fstart:round(f)]))
        N[fstart:round(f)] = N[fstart:round(f)] - Bdf
        
    H = aY - N
    n = np.zeros(len(Nfreqs))
    
    for k in range(1, len(Nfreqs)):
        Ef = round(Nfreqs[k] / Fs * len(y))
        n[k] = (20 * np.mean(H[1:Ef])) - (20 * np.mean(N[1:Ef]))
        
    return n