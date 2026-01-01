from abc import ABC, abstractmethod
from elements.client import Client
from elements.employee import Employee


class ProblemSolver(ABC):
    def __init__(self, employees: set[Employee], client: Client):
        self.employees = employees
        self.client = client
        self.best_solution: set[Employee] = set()
    
    @abstractmethod
    def solve(self) -> set[Employee]:
        pass