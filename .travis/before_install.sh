#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Mac OS X
    brew update
    brew install git-lfs
    git lfs install
    case "${TOXENV}" in
        py27)
        # Python 2
            brew install python2
            python2 -m pip install --upgrade setuptools
            python2 -m pip install --upgrade pip
            virtualenv venv -p python2
            ;;
        py36)
        # Python 3
            brew install python3
            python3 -m pip install --upgrade setuptools
            python3 -m pip install --upgrade pip
            virtualenv venv -p python3
            ;;
    esac
    source venv/bin/activate
fi
