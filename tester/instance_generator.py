import random
from typing import Tuple

from elements.client import Client
from elements.employee import Employee
from elements.skills import Skill


class InstanceGenerator:
    """
    Generador de instancias para el problema de selección de empleados.
    
    Permite generar empleados con habilidades aleatorias y clientes
    con requerimientos específicos para pruebas y experimentos.
    """
    
    def __init__(
        self, 
        seed: int | None = 42, 
        max_skill_level: int = 10,
        min_salary: int = 10,
        max_salary: int = 100
    ):
        """
        Inicializa el generador.
        
        Args:
            seed: Semilla para reproducibilidad. None para aleatorio.
            max_skill_level: Nivel máximo de habilidad (1 a max_skill_level).
            min_salary: Salario mínimo por hora.
            max_salary: Salario máximo por hora.
        """
        if seed is not None:
            random.seed(seed)
        self.max_skill_level = max_skill_level
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.skills = Skill.all_skills()
        self._employee_counter = 0
    
    def reset_seed(self, seed: int) -> None:
        """Reinicia la semilla del generador."""
        random.seed(seed)
        self._employee_counter = 0
    
    def generate_employees(
        self, 
        n: int,
        min_skills: int = 1,
        max_skills: int | None = None
    ) -> set[Employee]:
        """
        Genera un conjunto de empleados con habilidades aleatorias.
        
        Args:
            n: Número de empleados a generar.
            min_skills: Mínimo de habilidades por empleado.
            max_skills: Máximo de habilidades por empleado (None = todas).
            
        Returns:
            set[Employee]: Conjunto de empleados generados.
        """
        if max_skills is None:
            max_skills = len(self.skills)
        
        max_skills = min(max_skills, len(self.skills))
        min_skills = max(1, min(min_skills, max_skills))
        
        employees = set()
        
        for i in range(n):
            self._employee_counter += 1
            
            # Número de habilidades para este empleado
            num_skills = random.randint(min_skills, max_skills)
            selected_skills = random.sample(self.skills, num_skills)
            
            # Asignar niveles aleatorios
            skill_levels = {
                skill: random.randint(1, self.max_skill_level)
                for skill in selected_skills
            }
            
            employee = Employee(
                id=self._employee_counter,
                name=f"Employee_{self._employee_counter}",
                salary_per_hour=random.randint(self.min_salary, self.max_salary),
                skills=skill_levels
            )
            
            employees.add(employee)
        
        return employees
    
    def generate_client(
        self, 
        min_req: int = 1, 
        max_req: int = 4,
        min_level: int = 1,
        max_level: int | None = None
    ) -> Client:
        """
        Genera un cliente con requerimientos aleatorios.
        
        Args:
            min_req: Mínimo de requerimientos.
            max_req: Máximo de requerimientos.
            min_level: Nivel mínimo requerido.
            max_level: Nivel máximo requerido (None = max_skill_level).
            
        Returns:
            Client: Cliente con requerimientos generados.
        """
        if max_level is None:
            max_level = self.max_skill_level
        
        max_req = min(max_req, len(self.skills))
        min_req = max(1, min(min_req, max_req))
        
        req_count = random.randint(min_req, max_req)
        selected_skills = random.sample(self.skills, req_count)
        
        requirements = {
            skill: random.randint(min_level, max_level)
            for skill in selected_skills
        }
        
        return Client(requirements)
    
    def generate_instance(
        self,
        num_employees: int,
        num_requirements: int | None = None,
        **kwargs
    ) -> Tuple[set[Employee], Client]:
        """
        Genera una instancia completa del problema.
        
        Args:
            num_employees: Número de empleados.
            num_requirements: Número exacto de requerimientos (None = aleatorio).
            **kwargs: Argumentos adicionales para generate_employees.
            
        Returns:
            Tuple[set[Employee], Client]: Empleados y cliente generados.
        """
        employees = self.generate_employees(num_employees, **kwargs)
        
        if num_requirements is not None:
            client = self.generate_client(num_requirements, num_requirements)
        else:
            client = self.generate_client()
        
        return employees, client
    
    def generate_feasible_instance(
        self,
        num_employees: int,
        num_requirements: int = 3,
        max_attempts: int = 100
    ) -> Tuple[set[Employee], Client] | None:
        """
        Genera una instancia garantizada de tener solución factible.
        
        Intenta generar instancias hasta encontrar una donde los empleados
        puedan cubrir todos los requerimientos.
        
        Args:
            num_employees: Número de empleados.
            num_requirements: Número de requerimientos.
            max_attempts: Máximo de intentos.
            
        Returns:
            Tuple o None: Instancia factible o None si no se encuentra.
        """
        for _ in range(max_attempts):
            employees, client = self.generate_instance(num_employees, num_requirements)
            
            # Verificar factibilidad
            covered = set()
            for emp in employees:
                for skill, level in client.requirements.items():
                    if emp.has_skill(skill, level):
                        covered.add(skill)
            
            if covered == client.required_skills:
                return employees, client
        
        return None