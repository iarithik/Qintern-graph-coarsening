#!/usr/bin/env bash

# Create virutal environment
python3 -m venv .venv

# Activate Virtual environment
source ./.venv/bin/activate

# Change directory to coarsening package
cd ./src/

# Install coarsening package
pip3 install .

# Run tests
python3 -m pytest ./test/