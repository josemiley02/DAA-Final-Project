from solver.problem_solver import ProblemSolver
from solver.oracle_solver import OracleSolver


class CorrectnessEvaluator:
    def evaluate(
        self,
        solver: ProblemSolver,
        oracle: OracleSolver
    ) -> dict:
        solver_solution = solver.best_solution
        oracle_solution = oracle.best_solution

        solver_cost = sum(e.salary_per_hour for e in solver_solution)
        oracle_cost = sum(e.salary_per_hour for e in oracle_solution)

        return {
            "solver_cost": solver_cost,
            "oracle_cost": oracle_cost,
            "is_optimal": solver_cost == oracle_cost,
            "cost_ratio": solver_cost / oracle_cost if oracle_cost > 0 else 1.0,
            "solver_size": len(solver_solution),
            "oracle_size": len(oracle_solution),
            "size_diff": len(solver_solution) - len(oracle_solution)
        }
