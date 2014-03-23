__author__ = 'kate'
import sys
import os
import argparse
import measure
import helpers

measurements = measure.measurements

def process(indir, outdir, settingsfile, paramfile):
    '''
    Main sound file processing procedure. Finds all wave files in 'indir', reads them in one by one, and applies functions corresponding to each parameter in the parameters file. If no parameters file is specified, the default is "defaults/parameters/default.csv". If no settings file is specified, the default is "defaults/settings/default.csv" 
    '''
    params = helpers.get_parameters(paramfile)
    settings = helpers.get_settings(settingsfile)

    frameshift = int(settings['frameshift'])
    print indir, outdir

    # make a list of wav files
    # TODO fix this so it uses absolute file paths (os.getenv)
    if indir[-1] != '/':
        indir = indir + '/'
    filelist = [indir+f for f in os.listdir(indir) if f.endswith('.wav')]

    for wav in filelist:
        print "Processing ", wav
        matfile = wav[:-3]+"mat"
        # TODO TextGrid stuff

        # build SoundFile object
        soundfile = helpers.SoundFile(settings, wav)

        # run the measurements
        for param in params:
            soundfile.measurements[param] = measurements[param](soundfile) # it is what it is...

    print "Done processing."

def start():
    ''' Parses command line arguments and passes them to process() '''
    settings = "defaults/settings/default.csv"
    params = "defaults/parameters/default.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="input soundfile directory")
    parser.add_argument("outdir", help="directory where output should be stored")
    parser.add_argument("-s", "--settings", help="settings file")
    parser.add_argument("-p", "--parameters", help="parameters file")
    args = parser.parse_args()
    indir = args.indir
    outdir = args.outdir
    if args.settings:
        settings = args.settings
    if args.parameters:
        params = args.parameters
    print "args: ", indir, outdir, settings, params
    process(indir, outdir, settings, params)

if __name__ == "__main__":
    start()