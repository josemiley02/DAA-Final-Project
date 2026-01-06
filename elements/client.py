from elements.skills import Skill


class Client:
    """
    Representa un cliente con requerimientos de habilidades para un proyecto.
    
    Attributes:
        requirements: Diccionario de habilidades requeridas con niveles mínimos (1-10).
    """
    
    def __init__(self, requirements: dict[Skill, int]):
        self._validate_requirements(requirements)
        self.requirements = requirements
    
    @staticmethod
    def _validate_requirements(requirements: dict[Skill, int]) -> None:
        """Valida que los requerimientos sean válidos."""
        for skill, level in requirements.items():
            if not isinstance(skill, Skill):
                raise ValueError(f"Skill inválido: {skill}")
            if not 1 <= level <= 10:
                raise ValueError(f"Nivel debe estar entre 1 y 10, recibido: {level}")
    
    @property
    def num_requirements(self) -> int:
        """Retorna el número de requerimientos."""
        return len(self.requirements)
    
    @property
    def required_skills(self) -> set[Skill]:
        """Retorna el conjunto de habilidades requeridas."""
        return set(self.requirements.keys())
    
    def get_level(self, skill: Skill) -> int:
        """Retorna el nivel requerido para una habilidad, 0 si no es requerida."""
        return self.requirements.get(skill, 0)
    
    def __repr__(self):
        return f"Client({self.num_requirements} requirements: {list(self.requirements.keys())})"