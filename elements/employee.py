from elements.skills import Skill


class Employee:
    def __init__(self, id: int, name: str, salary_per_hour: float, skills: dict[Skill, int]):
        self.id = id
        self.name = name
        self.salary_per_hour = salary_per_hour
        self.skills = skills
    
    def __eq__(self, value):
        return self.id == value.id
    
    def __hash__(self):
        return self.id