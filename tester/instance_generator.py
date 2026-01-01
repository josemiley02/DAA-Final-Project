import random

from elements.client import Client
from elements.employee import Employee
from elements.skills import Skill


class InstanceGenerator:
    def __init__(self, seed: int = 42, max_skill_level: int = 5):
        random.seed(seed)
        self.max_skill_level = max_skill_level
        self.skills = list(Skill)
    
    def generate_employees(self, n: int) -> set[Employee]:
        employees = set()
        for i in range(n):
            skills_list = self.skills[:]
            random.shuffle(skills_list)

            k = random.randint(1, len(skills_list))  # número de habilidades del empleado

            selected_skills = skills_list[:k]

            skill_levels = {
                skill: random.randint(1, self.max_skill_level)
                for skill in selected_skills
            }

            employee = Employee(
                id=i + 1,
                name=f"Employee_{i + 1}",
                salary_per_hour=random.randint(5, 20),
                skills=skill_levels
            )

            employees.add(employee)

        return employees

    
    def generate_client(self, min_req=1, max_req=4) -> Client:
        req_count = random.randint(min_req, max_req)
        skills = random.sample(self.skills, req_count)
        requirements = {
            skill: random.randint(1, self.max_skill_level)
            for skill in skills
        }
        return Client(requirements)