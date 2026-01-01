import time
from solver.problem_solver import ProblemSolver


class MetricsCollector:
    def __init__(self):
        self.results = []

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

    
    def format_duration(self, seconds: float) -> str:
        ms = int((seconds % 1) * 1000)
        total_seconds = int(seconds)

        s = total_seconds % 60
        total_minutes = total_seconds // 60
        m = total_minutes % 60
        h = total_minutes // 60

        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
