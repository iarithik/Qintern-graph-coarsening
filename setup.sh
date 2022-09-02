#!/usr/bin/env bash

# Create virutal environment
python3 -m venv .venv

# Activate Virtual environment
source ./.venv/bin/activate

# Install coarsening package
pip3 install -e ./src/

# Run tests
python3 -m pytest ./src/test/