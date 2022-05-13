# Create virutal environment
python3 -m venv .venv

# Activate Virtual environment
source ./.venv/bin/activate

cd src\VRPCO
pip install -e .

cd ..\
cd VRPGraph
pip install -e .

cd ..\
cd VRPQO
pip install -e .
