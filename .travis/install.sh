#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Mac OS X
    case "${TOXENV}" in
        py27)
        # Python 2
            pip2 install numpy scipy
            pip2 install --upgrade numpy
            pip2 install --upgrade scipy
            # Install pyreaper
            pip2 install cython
            pip2 install git+https://github.com/voicesauce/pyreaper
            # Install coverage
            pip2 install coverage codecov
            ;;
        py36)
        # Python 3
            pip3 install numpy scipy
            pip3 install --upgrade numpy
            pip3 install --upgrade scipy
            # Install pyreaper
            pip3 install cython
            pip3 install git+https://github.com/voicesauce/pyreaper
            # Install coverage
            pip3 install coverage codecov
            ;;
    esac
    # Download and build REAPER
    git clone https://github.com/google/REAPER.git /tmp/REAPER
    mkdir /tmp/REAPER/build
    cd /tmp/REAPER/build
    cmake ..
    make
    # Install Praat
    curl http://www.fon.hum.uva.nl/praat/praat6040_mac64.dmg -o praat6040_mac64.dmg
    hdiutil attach praat6040_mac64.dmg
    cp -R /Volumes/Praat64_6040/Praat.app /Applications
    ls /Applications/Praat.app
else
    # Ubuntu
    sudo apt-get -qq update
    sudo apt-get install -y tk8.4 tcl-snack git
    # Install Praat
    wget http://www.fon.hum.uva.nl/praat/praat6040_linux64barren.tar.gz -O /tmp/praat.tar.gz
    tar -xzvf /tmp/praat.tar.gz
    sudo cp praat_barren /usr/bin/praat
    # Download and build REAPER
    git clone https://github.com/google/REAPER.git /tmp/REAPER
    mkdir /tmp/REAPER/build
    cd /tmp/REAPER/build
    cmake ..
    make
    sudo cp /tmp/REAPER/build/reaper /usr/bin/reaper
    cd
    # Install Python packages
    pip install --upgrade pip setuptools wheel
    pip install --only-binary=numpy,scipy numpy scipy
    pip install cython
    pip install git+https://github.com/voicesauce/pyreaper
    pip install coverage codecov
fi
