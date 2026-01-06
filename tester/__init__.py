"""
Módulo de testing para el problema de selección óptima de empleados.

Componentes:
- InstanceGenerator: Genera instancias aleatorias del problema
- MetricsCollector: Recolecta métricas de rendimiento de los solvers
- ProblemTester: Ejecuta experimentos comparativos entre solvers
"""

from tester.instance_generator import InstanceGenerator
from tester.metrics_collector import MetricsCollector
from tester.problem_tester import ProblemTester

__all__ = [
    'InstanceGenerator',
    'MetricsCollector', 
    'ProblemTester'
]
