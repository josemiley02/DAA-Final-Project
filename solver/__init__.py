"""
Módulo de solvers para el problema de selección óptima de empleados.

Algoritmos disponibles:
- BacktrackSolver: Solución exacta usando backtracking con poda (Branch & Bound)
- GreedySolver: Aproximación usando algoritmo greedy
- DPSolver: Solución exacta usando Programación Dinámica con Bitmask
- DPSolverOptimized: DP con eliminación de empleados dominados

Para agregar un nuevo solver:
1. Crear una clase que herede de ProblemSolver
2. Implementar el método solve() -> Solution
3. Usar los métodos auxiliares de la clase base para verificar cobertura
"""

from solver.problem_solver import ProblemSolver, Solution
from solver.backtrack_with_cut import BacktrackSolver
from solver.greedy_solver import GreedySolver
from solver.dp_solver import DPSolver, DPSolverOptimized

__all__ = [
    'ProblemSolver',
    'Solution', 
    'BacktrackSolver',
    'GreedySolver',
    'DPSolver',
    'DPSolverOptimized'
]
