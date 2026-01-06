from elements.client import Client
from elements.employee import Employee
from elements.skills import Skill
from solver.problem_solver import ProblemSolver, Solution


class DPSolver(ProblemSolver):
    """
    Resuelve el problema usando Programación Dinámica con Bitmask.
    
    Este enfoque modela el problema como una variante del Weighted Set Cover
    usando representación de estados mediante máscaras de bits.
    
    Estado DP:
        dp[mask] = (costo_mínimo, conjunto_empleados) para cubrir los 
                   requerimientos representados por el bitmask 'mask'
    
    Transición:
        Para cada empleado e con máscara de cobertura 'emp_mask':
        dp[mask | emp_mask] = min(dp[mask | emp_mask], dp[mask] + costo(e))
    
    Complejidad:
        - Temporal: O(n * 2^m) donde n = empleados, m = requerimientos
        - Espacial: O(2^m)
    
    Limitación: Práctico solo cuando m <= 20 requerimientos aproximadamente.
    
    Garantía: Encuentra la solución ÓPTIMA (exacta).
    """
    
    # Límite práctico de requerimientos para evitar explosión de memoria
    MAX_REQUIREMENTS = 20
    
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
        self._skill_to_bit: dict[Skill, int] = {}
        self._employee_masks: dict[Employee, int] = {}
        self._full_mask: int = 0
        self._dp: dict[int, tuple[float, set[Employee]]] = {}
    
    def solve(self) -> Solution:
        """
        Ejecuta el algoritmo de programación dinámica.
        
        Returns:
            Solution: La solución óptima encontrada.
        
        Raises:
            ValueError: Si hay demasiados requerimientos para el enfoque DP.
        """
        num_requirements = len(self.client.requirements)
        
        # Validar que el problema es tratable con DP
        if num_requirements > self.MAX_REQUIREMENTS:
            raise ValueError(
                f"DP Solver soporta máximo {self.MAX_REQUIREMENTS} requerimientos, "
                f"pero se recibieron {num_requirements}. "
                f"Considere usar otro solver (Greedy, Backtrack)."
            )
        
        # Caso trivial: sin requerimientos
        if num_requirements == 0:
            self.best_solution = Solution(set(), 0.0, True)
            return self.best_solution
        
        # Inicializar estructuras
        self._initialize_bitmasks()
        
        # Filtrar empleados que no aportan nada
        useful_employees = self._get_useful_employees()
        
        if not useful_employees:
            # No hay empleados que cubran ningún requerimiento
            self.best_solution = Solution.invalid()
            return self.best_solution
        
        # Ejecutar DP
        self._run_dp(useful_employees)
        
        # Extraer mejor solución
        return self._extract_solution()
    
    def _initialize_bitmasks(self) -> None:
        """
        Inicializa el mapeo de skills a bits y calcula la máscara objetivo.
        
        Cada skill requerida se mapea a un bit único en la máscara.
        La máscara completa (full_mask) tiene todos los bits en 1.
        """
        self._skill_to_bit.clear()
        
        for i, skill in enumerate(self.client.requirements.keys()):
            self._skill_to_bit[skill] = i
        
        num_requirements = len(self.client.requirements)
        self._full_mask = (1 << num_requirements) - 1  # Todos los bits en 1
    
    def _get_employee_mask(self, employee: Employee) -> int:
        """
        Calcula la máscara de bits que representa qué requerimientos
        puede cubrir un empleado.
        
        Args:
            employee: El empleado a evaluar.
            
        Returns:
            int: Bitmask donde bit i = 1 si el empleado cubre el requerimiento i.
        """
        mask = 0
        for skill, required_level in self.client.requirements.items():
            if employee.has_skill(skill, required_level):
                bit_position = self._skill_to_bit[skill]
                mask |= (1 << bit_position)
        return mask
    
    def _get_useful_employees(self) -> list[tuple[Employee, int]]:
        """
        Filtra y prepara los empleados que cubren al menos un requerimiento.
        
        Returns:
            Lista de tuplas (empleado, máscara) ordenada por eficiencia.
        """
        useful = []
        
        for employee in self.employees:
            mask = self._get_employee_mask(employee)
            if mask > 0:  # El empleado cubre al menos un requerimiento
                self._employee_masks[employee] = mask
                useful.append((employee, mask))
        
        # Ordenar por eficiencia (más cobertura por menos costo primero)
        # Esto puede mejorar la poda en algunos casos
        useful.sort(key=lambda x: -bin(x[1]).count('1') / x[0].salary_per_hour)
        
        return useful
    
    def _run_dp(self, employees: list[tuple[Employee, int]]) -> None:
        """
        Ejecuta el algoritmo de programación dinámica bottom-up.
        
        Usa un enfoque iterativo para evitar límites de recursión.
        
        Args:
            employees: Lista de (empleado, máscara) a considerar.
        """
        # Estado inicial: sin cobertura, costo 0, sin empleados
        # dp[mask] = (costo_mínimo, conjunto_empleados)
        self._dp = {0: (0.0, set())}
        
        # Para cada estado actual, intentar agregar cada empleado
        for mask in range(self._full_mask + 1):
            if mask not in self._dp:
                continue
            
            current_cost, current_employees = self._dp[mask]
            
            # Poda: si ya encontramos solución completa más barata, saltar
            if self._full_mask in self._dp:
                best_complete_cost = self._dp[self._full_mask][0]
                if current_cost >= best_complete_cost:
                    continue
            
            for employee, emp_mask in employees:
                # Saltar si el empleado ya está seleccionado
                if employee in current_employees:
                    continue
                
                # Calcular nuevo estado
                new_mask = mask | emp_mask
                new_cost = current_cost + employee.salary_per_hour
                
                # Poda: no expandir si el nuevo costo ya supera la mejor solución
                if self._full_mask in self._dp:
                    if new_cost >= self._dp[self._full_mask][0]:
                        continue
                
                # Actualizar si encontramos mejor camino a new_mask
                if new_mask not in self._dp or new_cost < self._dp[new_mask][0]:
                    new_employees = current_employees | {employee}
                    self._dp[new_mask] = (new_cost, new_employees)
    
    def _extract_solution(self) -> Solution:
        """
        Extrae la mejor solución del estado final de la DP.
        
        Returns:
            Solution: La solución óptima o inválida si no existe.
        """
        if self._full_mask not in self._dp:
            # No se puede cubrir todos los requerimientos
            self.best_solution = Solution.invalid()
            return self.best_solution
        
        cost, employees = self._dp[self._full_mask]
        self.best_solution = Solution(employees, cost, True)
        return self.best_solution
    
    def get_dp_stats(self) -> dict:
        """
        Retorna estadísticas de la ejecución de la DP.
        Útil para análisis y debugging.
        
        Returns:
            dict: Estadísticas incluyendo estados visitados, espacio total, etc.
        """
        total_states = 1 << len(self.client.requirements)
        visited_states = len(self._dp)
        
        return {
            "total_possible_states": total_states,
            "visited_states": visited_states,
            "coverage_ratio": visited_states / total_states if total_states > 0 else 0,
            "num_requirements": len(self.client.requirements),
            "num_employees": len(self.employees),
            "useful_employees": len(self._employee_masks),
            "solution_found": self._full_mask in self._dp
        }


class DPSolverOptimized(DPSolver):
    """
    Versión optimizada del DP Solver con técnicas adicionales de poda.
    
    Optimizaciones:
    1. Eliminación de empleados dominados
    2. Pre-ordenamiento por eficiencia
    3. Poda temprana más agresiva
    4. Uso de diccionario sparse en lugar de array denso
    """
    
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
    
    def _get_useful_employees(self) -> list[tuple[Employee, int]]:
        """
        Versión optimizada que elimina empleados dominados.
        
        Un empleado A está dominado por B si:
        - B cubre todo lo que A cubre (y posiblemente más)
        - B cuesta igual o menos que A
        """
        # Primero obtener todos los empleados útiles
        useful = super()._get_useful_employees()
        
        if len(useful) <= 1:
            return useful
        
        # Eliminar empleados dominados
        non_dominated = []
        
        for i, (emp_a, mask_a) in enumerate(useful):
            is_dominated = False
            
            for j, (emp_b, mask_b) in enumerate(useful):
                if i == j:
                    continue
                
                # B domina a A si:
                # 1. B cubre todo lo que A cubre: (mask_a & mask_b) == mask_a
                # 2. B cuesta igual o menos: emp_b.salary <= emp_a.salary
                # 3. B cubre más o cuesta menos (no son idénticos)
                covers_same_or_more = (mask_a & mask_b) == mask_a
                costs_same_or_less = emp_b.salary_per_hour <= emp_a.salary_per_hour
                strictly_better = (mask_b > mask_a) or (emp_b.salary_per_hour < emp_a.salary_per_hour)
                
                if covers_same_or_more and costs_same_or_less and strictly_better:
                    is_dominated = True
                    break
            
            if not is_dominated:
                non_dominated.append((emp_a, mask_a))
        
        return non_dominated
