All projects require the following deliverables:

1. Working code
2. Paper illustrating algorithm use case and demonstrating knowledge of how the algorithm works (you have to read the primary sources associated with each algorithm).
3. Final project presentation

Assignees:
Lizzy - Cepstral Peak Prominence(CPP)
Luke - Harmonics (GetH1_H2_H4)
Helene - Harmonics to noise ratio (HNR)

## f0 tracking: Port subharmonic-to-harmonic ratio algorithm
Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetSHRP.m
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/shrp.m

Coding difficulty: medium/challenge

Phonetics difficulty: medium/challenge

Fun: extreme

## f0 tracking: Port Praat f0 algorithm from Praat source code
Praat source code: http://www.fon.hum.uva.nl/praat/download_sources.html

Coding difficulty: challenge (should have familiarity with C++)

Phonetics difficulty: medium

Fun: depends on how much you like C++ (if you do I think you'll enjoy reading Boersma's code)

## f0 tracking: Port Praat f0 algorithm by calling Praat directly
Porting the Praat f0 algorithm this way is "cheating" (but this is the way it's done in Voicesauce) so you'll have to place more emphasis on demonstrating an understanding of how the Praat pitch tracking algorithm actually works than you would if you were porting it directly from the Praat source code.

Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_PraatPitch.m

Coding difficulty: medium (you might have to learn a little about Praat scripting)

Phonetics difficulty: medium/challenge

Fun: medium


## Cepstrum: Port Cepstral Peak Prominence algorithm
Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetCPP.m
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_pickpeaks.m

Coding difficulty: medium (requires either writing code or finding existing Python packages to do peak finding/optimization, e.g. Scipy.optimize)

Phonetics difficulty: medium (we've talked about the cepstrum in class)

Fun: definitely

## Energy: Port acoustic energy algorithm
Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetEnergy.m

Coding difficulty: easy

Phonetics difficulty: medium

Fun: probably


## Harmonics: Port harmonics calculation algorithms (can be broken up into multiple projects)
Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetH1_H2_H4.m
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetH1H2_H2H4.m
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetH1A1_H1A2_H1A3.m
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetA1A2A3.m

Coding difficulty: medium/challenge -- these different measurements can be broken down into multiple projects.

Phonetics difficulty: medium

Fun: probably

## Harmonics to noise ratio
Octave code:
* https://github.com/voicesauce/opensauce/blob/master/algos/functions/func_GetHNR.m

Coding difficulty: medium

Phonetics difficulty: medium

Fun: probably

## Visualizations
Write code to generate visualizations of audio recordings and measurements, e.g. waveform, spectral slice, full spectrogram, cepstrum, etc. Check out tools like scipy, matplotlib, pylab, and pandas.

## Extra credit: Propose and/or implement improvements to interactive elements of the software (e.g. graphical user interface, ease of use, documentation)

## Blue sky: Add a new measurement algorithm



