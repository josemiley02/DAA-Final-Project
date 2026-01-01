from elements.skills import Skill


class Client:
    def __init__(self, requirements: dict[Skill, int]):
        self.requirements = requirements