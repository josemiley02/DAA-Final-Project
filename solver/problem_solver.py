from abc import ABC, abstractmethod
from dataclasses import dataclass
from elements.client import Client
from elements.employee import Employee
from elements.skills import Skill


@dataclass
class Solution:
    """Representa una solución al problema de selección de empleados."""
    employees: set[Employee]
    total_cost: float
    is_valid: bool
    
    @classmethod
    def empty(cls) -> 'Solution':
        return cls(set(), 0.0, False)
    
    @classmethod
    def invalid(cls) -> 'Solution':
        return cls(set(), float('inf'), False)
    
    def __lt__(self, other: 'Solution') -> bool:
        """Permite comparar soluciones por costo."""
        return self.total_cost < other.total_cost


class ProblemSolver(ABC):
    """
    Clase base abstracta para resolver el problema de selección óptima de empleados.
    
    Problema: Dado un conjunto de empleados con habilidades y salarios, y un cliente
    con requerimientos específicos (habilidades con niveles mínimos), encontrar el
    subconjunto de empleados de costo mínimo que cubra todos los requerimientos.
    
    Este es una variante del Weighted Set Cover Problem (NP-Hard).
    """
    
    def __init__(self, employees: set[Employee], client: Client):
        self.employees = employees
        self.employees_list = list(employees)  # Para acceso por índice
        self.client = client
        self.best_solution: Solution = Solution.invalid()
    
    @abstractmethod
    def solve(self) -> Solution:
        """
        Resuelve el problema y retorna la mejor solución encontrada.
        
        Returns:
            Solution: La solución óptima o mejor aproximación encontrada.
        """
        pass
    
    def covers_requirement(self, employee: Employee, skill: Skill, level: int) -> bool:
        """Verifica si un empleado cubre un requerimiento específico."""
        return skill in employee.skills and employee.skills[skill] >= level
    
    def get_covered_requirements(self, employees: set[Employee]) -> set[Skill]:
        """Retorna el conjunto de skills cubiertas por un grupo de empleados."""
        covered = set()
        for skill, level in self.client.requirements.items():
            for employee in employees:
                if self.covers_requirement(employee, skill, level):
                    covered.add(skill)
                    break
        return covered
    
    def is_complete_cover(self, employees: set[Employee]) -> bool:
        """Verifica si un conjunto de empleados cubre todos los requerimientos."""
        covered = self.get_covered_requirements(employees)
        return covered == set(self.client.requirements.keys())
    
    def calculate_cost(self, employees: set[Employee]) -> float:
        """Calcula el costo total de un conjunto de empleados."""
        return sum(emp.salary_per_hour for emp in employees)
    
    def build_solution(self, employees: set[Employee]) -> Solution:
        """Construye un objeto Solution a partir de un conjunto de empleados."""
        is_valid = self.is_complete_cover(employees)
        cost = self.calculate_cost(employees) if is_valid else float('inf')
        return Solution(employees.copy(), cost, is_valid)
    
    def get_uncovered_requirements(self, employees: set[Employee]) -> dict[Skill, int]:
        """Retorna los requerimientos que aún no están cubiertos."""
        covered = self.get_covered_requirements(employees)
        return {skill: level for skill, level in self.client.requirements.items() 
                if skill not in covered}
    
    def can_cover_any_requirement(self, employee: Employee, 
                                   uncovered: dict[Skill, int]) -> bool:
        """Verifica si un empleado puede cubrir algún requerimiento no cubierto."""
        for skill, level in uncovered.items():
            if self.covers_requirement(employee, skill, level):
                return True
        return False
    
    @property
    def algorithm_name(self) -> str:
        """Retorna el nombre del algoritmo para identificación."""
        return self.__class__.__name__