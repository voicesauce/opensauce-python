Soundfile data files
--------------------

The `.TextGrid` files in this directory are for testing the TextGrid parser
`opensauce/textgrid.py`.

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