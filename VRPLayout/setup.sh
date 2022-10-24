#!/usr/bin/env bash

# Create virutal environment
python3 -m venv .venv-vrp

# Activate Virtual environment
source ./.venv-vrp/bin/activate

# Upgrade pip and setuptools
pip3 install --upgrade pip setuptools

# Install packages
pip3 install -e ./src/VRPCO/
pip3 install -e ./src/VRPGraph/
pip3 install -e ./src/VRPQO/

# Run tests
python3 -m pytest ./test/