#############################
#
#  This script makes measurements of the formant frequencies and bandwidths
#  of the first four formants for the specified wav file.
#  
#  Currently, only *.wav files are read.  Textgrids are ignored.
#
#  Input parameters include (in this order):
#  Input file, Time step, Window length, Maximum formant frequency
#
#  For each file, it creates a tab delimited text file with
#  measurement results in the same folder, saved as a *.pfmt file.
#
#  Result files contain the Measurement Time, Number of Formants, 
#  F1, B1, F2, B2, F3, B3, F4, B4.
#
#############################



form Measure F1, F2, F3, F4, F5, F6, F7
   comment See header of script for details. 

   comment Directory of input sound files
   text wavfile C:\temp.wav

#   sentence Sound_file_extension .wav
#   comment Directory of TextGrid files
#   text textGrid_directory C:\temp\
#   sentence TextGrid_file_extension .TextGrid
#   comment Full path of the resulting text file:
#   text resultfile C:\temp\results.txt

   comment Formant Measurement Parameters
   positive time_step 0.005
   positive window_length 0.025
   positive num_formants 4
   integer maximum_formant_frequency 5500
endform

# A sound file is opened
Read from file... 'wavfile$'
soundname$ = selected$ ("Sound", 1)

To Formant (burg)... 'time_step' 'num_formants' 'maximum_formant_frequency' 'window_length' 50

Down to Table... no yes 6 no 3 yes 3 yes

resultfile$ = "'wavfile$'.pfmt"

# Check if the result file exists:
if fileReadable (resultfile$)
	filedelete 'resultfile$'
endif

Write to table file... 'resultfile$'
