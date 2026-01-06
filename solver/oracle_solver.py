from itertools import combinations
from elements.employee import Employee
from solver.problem_solver import ProblemSolver


class OracleSolver(ProblemSolver):
    """
    Docstring for OracleSolver
    Class OracleSolver for simple testing
    """
    def solve(self) -> set[Employee]:
        employees = list(self.employees)
        best_cost = float("inf")
        best_solution = set()

        n = len(employees)

        for r in range(1, n + 1):
            for subset in combinations(employees, r):
                if self._covers_requirements(subset):
                    cost = sum(e.salary_per_hour for e in subset)
                    if cost < best_cost:
                        best_cost = cost
                        best_solution = set(subset)

        self.best_solution = best_solution
        return best_solution

    def _covers_requirements(self, subset):
        covered = {}
        for e in subset:
            for skill, lvl in e.skills.items():
                covered[skill] = max(covered.get(skill, 0), lvl)

        for skill, required in self.client.requirements.items():
            if covered.get(skill, 0) < required:
                return False
        return True
