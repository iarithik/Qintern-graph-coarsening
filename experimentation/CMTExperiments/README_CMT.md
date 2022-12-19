
**To Run CMT_Experiements**
1. Run setup.sh script in root directory to install module.
2. Run CMT_Exepriement.py. Note this currently uses uses an ILP solver with the MTZ VRP formulation. This requires either PuLP CBC or Gurobi. Most larger networks will require Gurobi for solution.
3. All experiment settings are at the bottom of CMT_Experiment.py. These include:
    - CMTDetails - which CMT instances will be tested
    - plotoutputs - whether the experiement will actively plot the outputs (note plots are automatically saved regardless)
    - encoder - how the route object will be encoded into a mathematical problem
    - solver - which solver is being used to solve the encoded problem
    - solverConfig - any settings associated with the general solver
    - coarseningRates - coarsening settings to be tested through the experiement


**Adding your own solvers**

Please use the standard format of solvers to build future quantum solvers. See the *Maintainers guide* (root directory) for more information on code workflow and solver types.

All solvers interface with the Logistics Route object. This class stores all information about the graph and the route (i.e final path). 

Implementation:
1. Write your solver class. Ideally this is a ‘standard solver’ that is a combination of an ‘encoder’ (i.e encode to QUBO formulation) and ‘solver backend’ (i.e Qiskit solver). The interface for these components can be found in the RouteSolvers.py file in src.
2. If you can’t separate this solver into an encoder and solver, a composite solver can be used. This solver is more general and can include more complex methods such as hybrid or cascaded optimization approaches. 
3. See RouteSolvers.py, StandardEncoder.py and SolverBackends.py for more information
4. Add your solver to the src\QuantumLogistics\__init__.py file so it’s recognized by the module
5. Add your solver to a run file to get the solved routes. 


For quantum solver there are two primary choices: 
1. Inherit from Composite route solver - this if a more general option. It requires you to define the solve algorithm (converting from the route object to a solution vector) and the extraction method (converting the solution vector into a set of paths within the route object)
2. Inherit from the StandardSolver - this enforces a standard encode-solve-decode method into the solution architecture. This requires an encoder object (for instance to encode to a standard QUBO formulation and then extract the solution vector to the QUBO back to the route object) and a solver object (to solve the QUBO)


 