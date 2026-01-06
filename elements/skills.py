from enum import Enum
import random


class Skill(Enum):
    """
    Enumeración de habilidades disponibles en el sistema.
    Los niveles de habilidad van de 1 (básico) a 10 (experto).
    """
    JAVA_SCRIPT = "JavaScript"
    PYTHON = "Python"
    JAVA = "Java"
    CSHARP = "C#"
    CPLUSPLUS = "C++"
    UIUX = "UI/UX Design"
    DATA_SCIENCE = "Data Science"
    
    @classmethod
    def all_skills(cls) -> list['Skill']:
        """Retorna lista de todas las habilidades disponibles."""
        return list(cls)
    
    @classmethod
    def random_skill(cls) -> 'Skill':
        """Retorna una habilidad aleatoria."""
        return random.choice(cls.all_skills())
    
    @classmethod
    def random_skills(cls, count: int) -> list['Skill']:
        """Retorna un subconjunto aleatorio de habilidades."""
        count = min(count, len(cls))
        return random.sample(cls.all_skills(), count)
    
    @classmethod
    def count(cls) -> int:
        """Retorna el número total de habilidades."""
        return len(cls)