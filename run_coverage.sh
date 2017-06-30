#!/bin/bash

# This is a bash script for running coverage and generating a report for
# the core OpenSauce code.  It should work on both Linux and Mac OS X.

coverage run --source=opensauce -m unittest test
coverage report -m
