from elements.client import Client
from elements.employee import Employee
from solver.problem_solver import ProblemSolver, Solution


class GreedySolver(ProblemSolver):
    """
    Resuelve el problema usando un algoritmo Greedy.
    
    Estrategia: En cada paso, selecciona el empleado con mejor relación
    costo-efectividad (más requerimientos cubiertos por unidad de costo).
    
    Complejidad temporal: O(n^2 * m) donde n = empleados, m = requerimientos.
    
    Nota: Este es un algoritmo de aproximación, NO garantiza la solución óptima.
    Para el Weighted Set Cover, el greedy tiene una garantía de aproximación
    de O(log n).
    """
    
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
    
    def solve(self) -> Solution:
        """
        Ejecuta el algoritmo greedy.
        
        Returns:
            Solution: Solución encontrada (válida o inválida según cobertura).
        """
        selected: set[Employee] = set()
        available = set(self.employees)
        uncovered = dict(self.client.requirements)
        total_cost = 0.0
        
        # Iterar mientras haya requerimientos no cubiertos y empleados disponibles
        while uncovered and available:
            # Encontrar el mejor empleado según costo-efectividad
            best_employee = self._select_best_employee(available, uncovered)
            
            if best_employee is None:
                # No hay empleado que cubra ningún requerimiento restante
                break
            
            # Agregar empleado a la solución
            selected.add(best_employee)
            available.remove(best_employee)
            total_cost += best_employee.salary_per_hour
            
            # Actualizar requerimientos no cubiertos
            covered_by_employee = best_employee.covers_requirements(uncovered)
            for skill in covered_by_employee:
                del uncovered[skill]
        
        # Construir solución
        is_valid = len(uncovered) == 0
        self.best_solution = Solution(selected, total_cost, is_valid)
        return self.best_solution
    
    def _select_best_employee(self, available: set[Employee], 
                               uncovered: dict) -> Employee | None:
        """
        Selecciona el empleado con mejor relación costo-efectividad.
        
        Métrica: (número de requerimientos no cubiertos que puede cubrir) / costo
        
        Esta métrica favorece empleados que cubren muchos requisitos a bajo costo.
        
        Args:
            available: Conjunto de empleados aún no seleccionados.
            uncovered: Diccionario de requerimientos no cubiertos.
            
        Returns:
            Employee: Mejor empleado según la métrica, o None si ninguno cubre requisitos.
        """
        best_employee = None
        best_efficiency = -1.0
        
        for employee in available:
            # Contar cuántos requerimientos no cubiertos puede cubrir
            new_coverage = len(employee.covers_requirements(uncovered))
            
            if new_coverage == 0:
                # Este empleado no cubre nada útil
                continue
            
            # Calcular eficiencia (más cobertura por menos costo = mejor)
            # Evitar división por cero (aunque salary > 0 en datos reales)
            efficiency = new_coverage / max(employee.salary_per_hour, 1.0)
            
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_employee = employee
        
        return best_employee
