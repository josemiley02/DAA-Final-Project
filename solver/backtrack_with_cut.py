from elements.client import Client
from elements.employee import Employee
from solver.problem_solver import ProblemSolver, Solution


class BacktrackSolver(ProblemSolver):
    """
    Resuelve el problema usando Backtracking con poda (Branch and Bound).
    
    Complejidad temporal: O(2^n) en el peor caso, donde n es el número de empleados.
    La poda reduce significativamente el espacio de búsqueda en la práctica.
    
    Estrategias de poda implementadas:
    1. Poda por costo: Si el costo actual >= mejor costo encontrado, se poda.
    2. Poda por factibilidad: Si no es posible cubrir todos los requerimientos
       con los empleados restantes, se poda.
    """
    
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
    
    def solve(self) -> Solution:
        """Ejecuta el algoritmo de backtracking con poda."""
        self._backtrack(0, set(), 0.0)
        return self.best_solution
    
    def _backtrack(self, pos: int, selected: set[Employee], current_cost: float) -> None:
        """
        Función recursiva de backtracking.
        
        Args:
            pos: Índice del empleado actual a considerar.
            selected: Conjunto de empleados seleccionados hasta ahora.
            current_cost: Costo acumulado de los empleados seleccionados.
        """
        # Poda por costo: si ya superamos el mejor costo, no continuar
        if current_cost >= self.best_solution.total_cost:
            return
        
        # Verificar si tenemos una solución válida
        if self.is_complete_cover(selected):
            self.best_solution = Solution(selected.copy(), current_cost, True)
            return
        
        # Caso base: no hay más empleados para considerar
        if pos >= len(self.employees_list):
            return
        
        # Poda por factibilidad: verificar si es posible cubrir los requerimientos restantes
        uncovered = self.get_uncovered_requirements(selected)
        if not self._can_potentially_cover(pos, uncovered):
            return
        
        employee = self.employees_list[pos]
        
        # Rama 1: Incluir al empleado (si aporta valor)
        if self.can_cover_any_requirement(employee, uncovered):
            selected.add(employee)
            self._backtrack(pos + 1, selected, current_cost + employee.salary_per_hour)
            selected.remove(employee)
        
        # Rama 2: Excluir al empleado
        self._backtrack(pos + 1, selected, current_cost)
    
    def _can_potentially_cover(self, from_pos: int, uncovered: dict) -> bool:
        """
        Verifica si los empleados restantes pueden potencialmente cubrir
        los requerimientos no cubiertos.
        """
        if not uncovered:
            return True
        
        coverable_skills = set()
        for i in range(from_pos, len(self.employees_list)):
            emp = self.employees_list[i]
            for skill, level in uncovered.items():
                if self.covers_requirement(emp, skill, level):
                    coverable_skills.add(skill)
        
        return coverable_skills == set(uncovered.keys())