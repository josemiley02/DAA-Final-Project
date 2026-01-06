import time
<<<<<<< HEAD
from statistics import mean
from solver.problem_solver import ProblemSolver
from solver.oracle_solver import OracleSolver
from tester.correctness_evaluator import CorrectnessEvaluator
=======
from typing import Type
from solver.problem_solver import ProblemSolver, Solution
>>>>>>> 3e40ada (feat: Implement multiple solvers for employee selection problem - Enhanced Client and Employee classes with validation and utility methods -  Improved overall code structure and documentation for better maintainability.)


class MetricsCollector:
    """
    Recolector de métricas para evaluar el rendimiento de los solvers.
    
    Métricas recolectadas:
    - Tiempo de ejecución
    - Tamaño de la solución (número de empleados)
    - Costo total de la solución
    - Validez de la solución
    """
    
    def __init__(self):
        self.results: list[dict] = []

    # =========================
    # Evaluación básica
    # =========================
    def evaluate(self, solver: ProblemSolver) -> dict:
        """
        Evalúa un solver y retorna métricas de rendimiento.
        
        Args:
            solver: Instancia del solver ya configurado con empleados y cliente.
            
        Returns:
            dict: Métricas de la ejecución.
        """
        start = time.perf_counter()
        solution: Solution = solver.solve()
        end = time.perf_counter()

        duration = end - start
<<<<<<< HEAD
        cost = sum(e.salary_per_hour for e in solution)
        size = len(solution)
=======
>>>>>>> 3e40ada (feat: Implement multiple solvers for employee selection problem - Enhanced Client and Employee classes with validation and utility methods -  Improved overall code structure and documentation for better maintainability.)

        return {
            "algorithm": solver.algorithm_name,
            "time_seconds": duration,
            "time_formatted": self.format_duration(duration),
            "solution_size": len(solution.employees),
            "solution_cost": solution.total_cost,
            "is_valid": solution.is_valid,
            "employees_selected": [e.id for e in solution.employees]
        }
<<<<<<< HEAD

    # =========================
    # Evaluación con oráculo
    # =========================
    def evaluate_with_oracle(
        self,
        solver: ProblemSolver,
        oracle: OracleSolver
    ) -> dict:
        # Solver rápido
        solver_metrics = self.evaluate(solver)

        # Oráculo
        oracle.solve()

        correctness = CorrectnessEvaluator().evaluate(
            solver,
            oracle
        )

        result = {
            **solver_metrics,
            **correctness
        }

        self.results.append(result)
        return result

    # =========================
    # Estadísticas globales
    # =========================
    def summary(self) -> dict:
        if not self.results:
            return {}

        with_oracle = [r for r in self.results if "oracle_cost" in r]

        optimal_cases = [r for r in with_oracle if r["is_optimal"]]

        return {
            "total_tests": len(self.results),
            "oracle_tests": len(with_oracle),

            # Correctitud
            "optimal_ratio": len(optimal_cases) / len(with_oracle)
            if with_oracle else None,

            "avg_cost_ratio": mean(
                r["cost_ratio"] for r in with_oracle
            ) if with_oracle else None,

            "avg_size_diff": mean(
                r["size_diff"] for r in with_oracle
            ) if with_oracle else None,

            # Rendimiento
            "avg_time_seconds": mean(
                r["time_seconds"] for r in self.results
            ),

            "max_time_seconds": max(
                r["time_seconds"] for r in self.results
            ),

            "min_time_seconds": min(
                r["time_seconds"] for r in self.results
            )
        }

    # =========================
    # Utilidades
    # =========================
=======
    
    def compare_solvers(self, solvers: list[ProblemSolver]) -> list[dict]:
        """
        Compara múltiples solvers sobre la misma instancia del problema.
        
        Args:
            solvers: Lista de solvers configurados con la misma instancia.
            
        Returns:
            list[dict]: Lista de resultados para cada solver.
        """
        results = []
        for solver in solvers:
            result = self.evaluate(solver)
            results.append(result)
        return results
    
>>>>>>> 3e40ada (feat: Implement multiple solvers for employee selection problem - Enhanced Client and Employee classes with validation and utility methods -  Improved overall code structure and documentation for better maintainability.)
    def format_duration(self, seconds: float) -> str:
        """Formatea la duración en formato HH:MM:SS.mmm"""
        ms = int((seconds % 1) * 1000)
        total_seconds = int(seconds)

        s = total_seconds % 60
        total_minutes = total_seconds // 60
        m = total_minutes % 60
        h = total_minutes // 60

        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    
    def get_summary(self) -> dict:
        """
        Retorna un resumen de todos los resultados recolectados.
        
        Returns:
            dict: Estadísticas agregadas por algoritmo.
        """
        if not self.results:
            return {}
        
        summary = {}
        
        # Agrupar por algoritmo
        algorithms = set(r.get("algorithm", "unknown") for r in self.results)
        
        for algo in algorithms:
            if algo == "OracleSolver":
                continue
            algo_results = [r for r in self.results if r.get("algorithm") == algo]
            
            times = [r["time_seconds"] for r in algo_results]
            costs = [r["solution_cost"] for r in algo_results if r["is_valid"]]
            valid_count = sum(1 for r in algo_results if r["is_valid"])
            
            summary[algo] = {
                "total_runs": len(algo_results),
                "valid_solutions": valid_count,
                "avg_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0,
                "avg_cost": sum(costs) / len(costs) if costs else 0,
                "min_cost": min(costs) if costs else 0,
                "max_cost": max(costs) if costs else 0,
            }
        
        return summary
    
    def clear(self) -> None:
        """Limpia todos los resultados recolectados."""
        self.results.clear()
