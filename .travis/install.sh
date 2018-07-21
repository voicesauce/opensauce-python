#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
  # Mac OS X
  # Install Python Packages
  case "${TOXENV}" in
    osx_py2*)
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
    osx_py3*)
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
    conda*)
      if [[ $CONDA_PYTHON_VERSION == '2.7' ]]; then
        wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh -O miniconda.sh
      else
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh
      fi
      bash miniconda.sh -b -p $CONDA_HOME/miniconda
      export PATH="$CONDA_HOME/miniconda/bin:$PATH"
      hash -r
      conda config --set always_yes yes --set changeps1 no
      conda update -q conda
      # Useful for debugging any issues with conda
      conda info -a
      # Create virtual environment
      conda create -q -n test-environment python=$CONDA_PYTHON_VERSION
      source activate test-environment
      conda install git pip cython numpy scipy coverage
      pip install git+https://github.com/voicesauce/pyreaper
      conda install -c conda-forge codecov
      conda list
      ;;
  esac
  # Build and install Snack if necessary
  case "${TRAVIS_OSX_IMAGE}" in
    xcode9*)
      if [[ $TCL_BINARY == 'no' ]]; then
        curl -O http://www.speech.kth.se/snack/dist/snack2.2.10.tar.gz
        tar -xzf snack2.2.10.tar.gz
        cd snack2.2.10/unix
        ./configure --with-tcl=/System/Library/Frameworks/Tcl.framework --with-tk=/System/Library/Frameworks/Tk.framework
        sed -e '3s~.*~TCL_INCPATH = /System/Library/Frameworks/Tcl.framework/Headers~' -i '' Makefile
        sed -e '7s~.*~TK_INCPATH = /System/Library/Frameworks/Tk.framework/Headers~' -i '' Makefile
        export LC_CTYPE=C && export LANG=C && export LC_ALL=C && make
        make DESTDIR=/Users/travis install
        cd
      else
        curl -LO https://github.com/voicesauce/opensauce-python/raw/master/opensauce/mac/snack-tcl85.zip
        mkdir /Users/travis/lib
        unzip snack-tcl85.zip -d /Users/travis/lib
      fi
      ;;
  esac
  # Install Praat
  curl http://www.fon.hum.uva.nl/praat/praat6040_mac64.dmg -o praat6040_mac64.dmg
  hdiutil attach praat6040_mac64.dmg
  cp -R /Volumes/Praat64_6040/Praat.app /Applications
  # Download and build REAPER
  git clone https://github.com/google/REAPER.git /tmp/REAPER
  mkdir /tmp/REAPER/build
  cd /tmp/REAPER/build
  cmake ..
  make
elif [[ $TRAVIS_OS_NAME == 'linux' ]]; then
  # Linux
  # Install Python packages
  case "${TOXENV}" in
    conda*)
      # Linux Anaconda
      sudo apt-get -qq update
      if [[ $CONDA_PYTHON_VERSION == '2.7' ]]; then
        wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
      else
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
      fi
      bash miniconda.sh -b -p $CONDA_HOME/miniconda
      export PATH="$CONDA_HOME/miniconda/bin:$PATH"
      hash -r
      conda config --set always_yes yes --set changeps1 no
      conda update -q conda
      # Useful for debugging any issues with conda
      conda info -a
      # Create virtual environment
      conda create -q -n test-environment python=$CONDA_PYTHON_VERSION
      source activate test-environment
      conda install git pip cython numpy scipy coverage
      pip install git+https://github.com/voicesauce/pyreaper
      conda install -c conda-forge codecov
      conda list
      ;;
    ubuntu*)
      pip install --upgrade pip setuptools wheel
      pip install --only-binary=numpy,scipy numpy scipy
      pip install cython
      pip install git+https://github.com/voicesauce/pyreaper
      pip install coverage codecov
      ;;
  esac
  sudo apt-get -qq update
  # Install Snack
  sudo apt-get install -y tk8.4 tcl8.4 tcl-snack
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
fi
