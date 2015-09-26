#!/bin/bash

if [ -z $VS_ROOT ]
then
    echo "set environment variable VS_ROOT first!"
else
    root=$VS_ROOT

    # path to an input directory of *.wav files
    inputDir="$root/defaults/sounds"
    
    # path to the directory where you want to store OpenSauce output
    outputDir="$root/output"
    mkdir -pv $outputDir # if the output dir already doesn't exist, create it

    # path to your settings file
    settings="$root/defaults/settings/default.csv"
    
    # path to the list of measurements you want to extract from the input
    params="$root/defaults/parameters/default.csv"

    python $root/opensauce/process.py -i $inputDir -o $outputDir -s $settings -p $params
fi
