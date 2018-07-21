#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Mac OS X
    brew update
    brew install git-lfs
    git lfs install
    case "${TOXENV}" in
        osx_py2)
        # Python 2
            brew upgrade python # Python 3, needed to fix linking issues
            brew install python@2
            pip2 install --upgrade setuptools
            pip2 install --upgrade pip
            pip2 install --upgrade wheel
            pip2 install --upgrade virtualenv
            virtualenv venv -p python2
            source venv/bin/activate
            ;;
        osx_py3)
        # Python 3
            brew upgrade python
            brew install python@2 # Need Python 2 for dependencies
            pip3 install --upgrade setuptools
            pip3 install --upgrade pip
            pip2 install --upgrade wheel
            pip3 install --upgrade virtualenv
            virtualenv venv -p python3
            source venv/bin/activate
            ;;
    esac
fi
