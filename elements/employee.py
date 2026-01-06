from elements.skills import Skill


class Employee:
    """
    Representa un empleado con habilidades y costo por hora.
    
    Attributes:
        id: Identificador único del empleado.
        name: Nombre del empleado.
        salary_per_hour: Costo por hora del empleado.
        skills: Diccionario de habilidades con sus niveles (1-10).
    """
    
    def __init__(self, id: int, name: str, salary_per_hour: float, skills: dict[Skill, int]):
        self.id = id
        self.name = name
        self.salary_per_hour = salary_per_hour
        self.skills = skills
    
    def has_skill(self, skill: Skill, min_level: int = 1) -> bool:
        """Verifica si el empleado tiene una habilidad con nivel mínimo."""
        return skill in self.skills and self.skills[skill] >= min_level
    
    def covers_requirements(self, requirements: dict[Skill, int]) -> set[Skill]:
        """Retorna el conjunto de requerimientos que este empleado puede cubrir."""
        covered = set()
        for skill, level in requirements.items():
            if self.has_skill(skill, level):
                covered.add(skill)
        return covered
    
    def coverage_ratio(self, requirements: dict[Skill, int]) -> float:
        """Retorna la proporción de requerimientos que puede cubrir (0.0 a 1.0)."""
        if not requirements:
            return 0.0
        covered = self.covers_requirements(requirements)
        return len(covered) / len(requirements)
    
    def efficiency(self, requirements: dict[Skill, int]) -> float:
        """
        Calcula la eficiencia del empleado: requerimientos cubiertos / costo.
        Útil para algoritmos greedy.
        """
        covered = len(self.covers_requirements(requirements))
        if self.salary_per_hour == 0:
            return float('inf') if covered > 0 else 0
        return covered / self.salary_per_hour
    
    def __eq__(self, other):
        if not isinstance(other, Employee):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f"Employee({self.id}, '{self.name}', ${self.salary_per_hour}/h, {len(self.skills)} skills)"