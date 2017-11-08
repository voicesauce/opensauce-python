Soundfile data files
====================

## TextGrid files
The `.TextGrid` files in the directory `textgrid` are for testing the TextGrid
parser `opensauce/textgrid.py`.

`beijing_f3_50_a.TextGrid` is the original TextGrid file corresponding to the
wav file `beijing_f3_50_a.wav`.

`beijing_f3_50_a-texttier.TextGrid` is the same as `beijing_f3_50_a.TextGrid`,
except it has has a dummy TextTier item added, to check that tiers which are
not of the IntervalTier class are skipped when the sound file's TextGrid is
processed.

Both `beijing_f3_50_a.TextGrid` and `beijing_f3_50_a-texttier.TextGrid` are
ASCII encoded.

`beijing_f3_50_a-utf8.TextGrid` is UTF-8 encoded and contains non-ASCII text
labels in the TextGrid tiers.  `beijing_f3_50_a-utf16.TextGrid` is UTF-16
encoded and contains non-ASCII text labels in the TextGrid tiers.

We test UTF-8 and UTF-16 encoded TextGrid files to make sure that we can
handle non-ASCII characters in the TextGrid files.

## Resampled data files

The files corresponding to resampled data are in the `resample` directory.

The `*-matlab-resample.json` files contain the data for each wav file after
resampling in Matlab at 16 kHz.  The Matlab command used is
`y = resample(y, 16000, Fs)` where `y` is the original data and `Fs` is the
sampling frequency for the original data.  These data are for comparing against
SciPy's resample function.

The `*-raw-resample-16kHz.txt` files contain the raw data from resampling the
data read in from the corresponding `.wav` file.  Resampling was done at
16kHz on Manjaro Linux.

The `*-resample-16kHz.wav` files are the wav files created from the resampled
data in `*-raw-resample-16kHz.txt` on Manjaro Linux.  Resampling was done at
16kHz.

Note that in order for the tests that use resampled data to pass, you need
SciPy version 1.0+.  The resampled test data was generated using SciPy 1.0,
and previous versions of SciPy generate different resampled values.
