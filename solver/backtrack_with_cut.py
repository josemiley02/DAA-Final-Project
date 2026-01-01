from elements.client import Client
from elements.employee import Employee
from solver.problem_solver import ProblemSolver


class BackatrackSolver(ProblemSolver):
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
        self.best_solution: set[Employee] = set()
        self.best_cost: float = float('inf')

    def solve(self) -> set[Employee]:
        return self._solve(0, set(), 0)
    
    def _solve(self, total_cost: float, selected_employees: set[Employee], pos: int):
        if total_cost >= self.best_cost:
            return
        if self._cover(selected_employees):
            self.best_cost = total_cost
            self.best_solution = selected_employees.copy()
            return
        if pos >= len(self.employees):
            return
        employee: Employee = list(self.employees)[pos]
        # Include the employee
        selected_employees.add(employee)
        self._solve(total_cost + employee.salary_per_hour, selected_employees, pos + 1)

        #Exclude the employee
        selected_employees.remove(employee)
        self._solve(total_cost, selected_employees, pos + 1)
    
    def _cover(self, selected_employees: set[Employee]) -> bool:
        count_covered_skills: int = 0
        for employee in selected_employees:
            for skill, level in self.client.requirements.items():
                if skill in employee.skills and employee.skills[skill] >= level:
                    count_covered_skills += 1
        return count_covered_skills == len(self.client.requirements)