Most of these input files and output files were supplied by Kristine.  They
were produced using VoiceSauce X.Y.Z.

Kristine's notes
----------------

Here are some output files I generated from running VoiceSauce at default
settings for the sample input files.

When I say using "XXX" for parameter estimation, where "XXX" might be Straight
f0, snack f0, praat f0, or SHR, that means which measurement of fundamental
frequency (f0) was used for downstream measurement algorithms that involved f0
(this is set in "Settings"). The parameters pF5, pF6, and pF7 were not
measured, and so in the output text file, all values for these parameters are 0
(this is something that can also be set in "Settings", under "Not a number"
label). In some use cases, even if the user decides to use one particular f0
measurement algorithm to calculate f0 for downstream measurement algorithms,
the user still might sometimes want to estimate f0 using the other algorithms
(although probably not usually! Straight f0 in particular takes a long time to
run, so if a user is using say praat f0 for downstream, they might not also
have straight f0 measured or other f0 measurements, and only select praat f0),
so I've included all f0 measurement algorithms in each run of the software,
even if only values calculated from only one of the f0 measurement algorithms
are used for downstream measurement algorithms.

I always used Snack for formant estimation for these calculations (using Praat
is another option--I could also generate output files for those later if
desired).

I also aways used TextGrid segmentation labels for the output. (Currently if
you uncheck that box in the GUI, the program crashes! We could imagine use
cases where a user has no TextGrid though, so it would be good to have that
option eventually as well, where the text file outputted would give all the
desired measurements measured at the specified frame shift (by default, 1 ms,
so there's one measurement estimated every 1 ms), in the audio file.)

    output-strf0-1ms.txt. Using Straight f0 for parameter estimation,
        outputting all parameters to text (except "Other" parameters), using
        TextGrid segmentation, but with no subsegments. This writes out all the
        data, one measurement for each parameter per millisecond (see column
        t_ms), starting with the first labeled interval in the TextGrid. The
        reason it's every one millisecond is because the frame shift in the
        "Settings" window was set to 1 ms.

    output-strf0-9seg.txt. Using Straight f0 for parameter estimation, using
        TextGrid segmentation, with 9 evenly spaced sub-intervals
        ("sub-segments") per labeled interval. Means are calculated over each
        of the 9 subsegments in a labeled interval, as well as a mean over the
        entire labeled interval.

    output-sf0-1ms.txt. Using snack f0 for parameter estimation, no subsegments.

    output-sf0-9seg.txt. Using snack f0 for parameter estimation, 9 subsegments.

    output-pf0-1ms.txt. Using praat f0 for parameter estimation, no subsegments.

    output-pf0-9seg.txt. Using praat f0 for parameter estimation, 9 subsegments.

    output-shrf0-1ms.txt. Using shr f0 for parameter estimation, no subsegments.

    output-shrf0-9seg.txt. Using shr f0 for parameter estimation, 9 subsegments.


Other files
-----------

cant_c5_19a.f0          File produced by snack, computing f0 on the wav file in
                        the default directory.

beijing_f3_50_a-y.mat   The y vector from octave's wavread function applied
                        to beijing_f3_50_a.wav, saved as a .mat file.