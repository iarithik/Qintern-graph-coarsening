from recordclass import recordclass

Route = recordclass('Route', 'vehicle cities distance')

VRPSolution = recordclass('VRPSolution', 'objective routes')
