#!/bin/bash

if [ -z $VS_ROOT ]
then
    echo "set environment variable VS_ROOT first!"
else
    root=$VS_ROOT
    inputDir="$root/defaults/sounds"
    outputDir="$root/output"
    mkdir -pv $outputDir
    settings="$root/defaults/settings/default.csv"
    params="$root/defaults/parameters/default.csv"
    echo "input: $inputDir, output: $outputDir, settings: $settings, params: $params"
    python $root/opensauce/process.py -i $inputDir -o $outputDir -s $settings -p $params
fi
