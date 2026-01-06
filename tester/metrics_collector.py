import time
from statistics import mean
from solver.problem_solver import ProblemSolver
from solver.oracle_solver import OracleSolver
from tester.correctness_evaluator import CorrectnessEvaluator


class MetricsCollector:
    def __init__(self):
        self.results = []

    # =========================
    # Evaluación básica
    # =========================
    def evaluate(self, solver: ProblemSolver) -> dict:
        start = time.perf_counter()
        solver.solve()
        solution = solver.best_solution
        end = time.perf_counter()

        duration = end - start
        cost = sum(e.salary_per_hour for e in solution)
        size = len(solution)

        return {
            "time_seconds": duration,
            "time_formatted": self.format_duration(duration),
            "solution_size": size,
            "solution_cost": cost
        }

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
    def format_duration(self, seconds: float) -> str:
        ms = int((seconds % 1) * 1000)
        total_seconds = int(seconds)

        s = total_seconds % 60
        total_minutes = total_seconds // 60
        m = total_minutes % 60
        h = total_minutes // 60

        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
