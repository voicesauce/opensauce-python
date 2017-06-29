#!/bin/bash

coverage run -m unittest test
coverage report -m --include=opensauce/*
