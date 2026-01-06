import time
from typing import Type
from solver.problem_solver import ProblemSolver, Solution


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

        return {
            "algorithm": solver.algorithm_name,
            "time_seconds": duration,
            "time_formatted": self.format_duration(duration),
            "solution_size": len(solution.employees),
            "solution_cost": solution.total_cost,
            "is_valid": solution.is_valid,
            "employees_selected": [e.id for e in solution.employees]
        }
    
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
