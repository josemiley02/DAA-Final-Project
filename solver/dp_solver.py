from elements.client import Client
from elements.employee import Employee
from elements.skills import Skill
from solver.problem_solver import ProblemSolver, Solution


class DPSolver(ProblemSolver):
    """
    Resuelve el problema usando Programación Dinámica con Bitmask.
    
    Este enfoque modela el problema como una variante del Weighted Set Cover
    usando representación de estados mediante máscaras de bits.
    
    Algoritmo (patrón 0/1 knapsack):
        - Para cada empleado e, iterar S desde FULL_MASK hasta 0
        - Transición: dp[S | M_e] = min(dp[S | M_e], dp[S] + c_e)
        - Reconstrucción mediante array parent
    
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
        self._dp: list[float] = []
        self._parent: list[tuple[Employee, int] | None] = []
    
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
        
        # Filtrar empleados que no aportan nada (máscara != 0)
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
        self._employee_masks.clear()
        
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
            int: Bitmask donde bit j = 1 si el empleado cubre el requerimiento j.
        """
        mask = 0
        for skill, required_level in self.client.requirements.items():
            if employee.has_skill(skill, required_level):
                bit_position = self._skill_to_bit[skill]
                mask |= (1 << bit_position)
        return mask
    
    def _get_useful_employees(self) -> list[tuple[Employee, int]]:
        """
        Filtra empleados que cubren al menos un requerimiento (máscara != 0).
        
        Returns:
            Lista de tuplas (empleado, máscara).
        """
        useful = []
        
        for employee in self.employees:
            mask = self._get_employee_mask(employee)
            if mask > 0:  # El empleado cubre al menos un requerimiento
                self._employee_masks[employee] = mask
                useful.append((employee, mask))
        
        return useful
    
    def _run_dp(self, employees: list[tuple[Employee, int]]) -> None:
        """
        Ejecuta el algoritmo de programación dinámica con patrón 0/1.
        
        Implementación según el informe:
        - Para cada empleado, iterar S desde FULL_MASK hasta 0
        - Esto garantiza que cada empleado se usa a lo sumo una vez
        
        Args:
            employees: Lista de (empleado, máscara) a considerar.
        """
        INF = float('inf')
        
        # Inicialización de la tabla DP
        # dp[S] = costo mínimo para cubrir al menos los requerimientos en S
        self._dp = [INF] * (self._full_mask + 1)
        self._parent = [None] * (self._full_mask + 1)
        self._dp[0] = 0.0  # Estado inicial: costo 0 para cubrir nada
        
        # Procesamiento de cada empleado (patrón 0/1 knapsack)
        for employee, emp_mask in employees:
            cost_e = employee.salary_per_hour
            
            # Iteramos en orden inverso para usar cada empleado a lo sumo una vez
            for S in range(self._full_mask, -1, -1):
                if self._dp[S] < INF:
                    next_S = S | emp_mask
                    new_cost = self._dp[S] + cost_e
                    
                    if new_cost < self._dp[next_S]:
                        self._dp[next_S] = new_cost
                        self._parent[next_S] = (employee, S)
    
    def _extract_solution(self) -> Solution:
        """
        Extrae la mejor solución reconstruyendo desde el estado final.
        
        Returns:
            Solution: La solución óptima o inválida si no existe.
        """
        # Verificar si existe solución
        if self._dp[self._full_mask] == float('inf'):
            self.best_solution = Solution.invalid()
            return self.best_solution
        
        # Reconstruir solución siguiendo la cadena de parent
        selected: set[Employee] = set()
        S = self._full_mask
        
        while S != 0 and self._parent[S] is not None:
            employee, prev_S = self._parent[S]
            selected.add(employee)
            S = prev_S
        
        cost = self._dp[self._full_mask]
        self.best_solution = Solution(selected, cost, True)
        return self.best_solution
    
    def get_dp_stats(self) -> dict:
        """
        Retorna estadísticas de la ejecución de la DP.
        Útil para análisis y debugging.
        
        Returns:
            dict: Estadísticas incluyendo estados visitados, espacio total, etc.
        """
        total_states = 1 << len(self.client.requirements)
        visited_states = sum(1 for x in self._dp if x < float('inf'))
        
        return {
            "total_possible_states": total_states,
            "visited_states": visited_states,
            "coverage_ratio": visited_states / total_states if total_states > 0 else 0,
            "num_requirements": len(self.client.requirements),
            "num_employees": len(self.employees),
            "useful_employees": len(self._employee_masks),
            "solution_found": self._dp[self._full_mask] < float('inf') if self._dp else False
        }


class DPSolverOptimized(DPSolver):
    """
    Versión optimizada del DP Solver con técnicas adicionales de poda.
    
    Optimizaciones:
    1. Eliminación de empleados dominados
    2. Combinación de empleados con misma máscara (quedarse con el más barato)
    """
    
    def __init__(self, employees: set[Employee], client: Client):
        super().__init__(employees, client)
    
    def _get_useful_employees(self) -> list[tuple[Employee, int]]:
        """
        Versión optimizada que:
        1. Combina empleados con misma máscara (conserva el más barato)
        2. Elimina empleados dominados
        
        Un empleado A está dominado por B si:
        - B cubre todo lo que A cubre (y posiblemente más)
        - B cuesta igual o menos que A
        - B es estrictamente mejor (cubre más o cuesta menos)
        """
        # Obtener todos los empleados útiles (máscara != 0)
        all_useful = []
        for employee in self.employees:
            mask = self._get_employee_mask(employee)
            if mask > 0:
                self._employee_masks[employee] = mask
                all_useful.append((employee, mask))
        
        if len(all_useful) <= 1:
            return all_useful
        
        # Paso 1: Combinar empleados con misma máscara (quedarse con el más barato)
        mask_to_best: dict[int, Employee] = {}
        for employee, mask in all_useful:
            if mask not in mask_to_best:
                mask_to_best[mask] = employee
            elif employee.salary_per_hour < mask_to_best[mask].salary_per_hour:
                mask_to_best[mask] = employee
        
        combined = [(emp, mask) for mask, emp in mask_to_best.items()]
        
        if len(combined) <= 1:
            return combined
        
        # Paso 2: Eliminar empleados dominados
        non_dominated = []
        
        for i, (emp_a, mask_a) in enumerate(combined):
            is_dominated = False
            
            for j, (emp_b, mask_b) in enumerate(combined):
                if i == j:
                    continue
                
                # B domina a A si:
                # 1. B cubre todo lo que A cubre: (mask_a & mask_b) == mask_a
                # 2. B cuesta igual o menos
                # 3. B es estrictamente mejor (cubre más O cuesta menos)
                covers_all_of_a = (mask_a & mask_b) == mask_a
                costs_same_or_less = emp_b.salary_per_hour <= emp_a.salary_per_hour
                strictly_better = (mask_b != mask_a) or (emp_b.salary_per_hour < emp_a.salary_per_hour)
                
                if covers_all_of_a and costs_same_or_less and strictly_better:
                    is_dominated = True
                    break
            
            if not is_dominated:
                non_dominated.append((emp_a, mask_a))
        
        return non_dominated
