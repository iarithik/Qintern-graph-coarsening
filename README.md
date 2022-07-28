**Project: Solving Vehicle Routing Problem and its variants using quantum computing (Group 2 - QAOA) **

**Mentor:** Paweł Gora

**Description:** Vehicle Routing Problem (VRP) is a combinatorial optimization problem important for real-world logistics and difficult (NP-hard) from a computational perspective. The goal is to find optimal routes of a fleet of vehicles aiming to visit some number of locations. There are different variants of VRP, e.g., with limited capacities of vehicles, time windows for visiting specific locations, multiple depots etc. All of them are interesting areas for applications of quantum computers.

To develop and compare current quantum optimisation methods in the VRP, this research group is completing work in three primary areas. This includes:

- Quantum Optimisation:
    - Variational Quantum Eigensolver
    - Quantum Annealing
    - Quantum Approximate Optimisation Algorithm

- Graph network representation and topology reduction:
    - Graph Coarsening

- Classical Optimisation:
    - VRP as a Mixed Integer Linear Program

Please read the Maintainers Guide on how to contribute to this repository

Example run scripts can be found in the 'Workspace' directory


**Adding your own solvers**

Please use the standard format of solvers to build future quantum solvers. See the Maintainers guide for more information on code workflow

For an example on how to use the codebase see: Workspace\ExampleRunFile\exampleRunFile.py

Implementation:
1. Write your solver class. Ideally this is a ‘standard solver’ that is a combination of an ‘encoder’ (i.e encode to QUBO formulation) and ‘solver backend’ (i.e Qiskit solver). The interface for these components can be found in the RouteSolvers.py file in src.
2. If you can’t separate this solver into an encoder and solver, a composite solver can be used. This solver is more general and can include more complex methods such as hybrid or cascaded optimization approaches. 
3. See RouteSolvers.py, StandardEncoder.py and SolverBackends.py for more information
4. Add your solver to the src\QuantumLogistics\__init__.py file so it’s recognized by the module
5. Add your solver to a run file to get the solved routes. 


 
