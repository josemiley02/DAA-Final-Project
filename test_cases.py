"""
Módulo para cargar y trabajar con casos de prueba generados.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from elements.employee import Employee
from elements.client import Client
from elements.skills import Skill


class TestCaseLoader:
    """Carga y gestiona casos de prueba desde JSON."""
    
    @staticmethod
    def load_test_cases(filepath: str = "test_data/test_cases.json") -> Tuple[List[Dict], Dict]:
        """
        Carga casos de prueba desde JSON.
        
        Args:
            filepath: Ruta al archivo JSON
            
        Returns:
            Tupla (test_cases, metadata)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('test_cases', []), data.get('metadata', {})
    
    @staticmethod
    def case_to_problem(case: Dict) -> Tuple[set[Employee], Client]:
        """
        Convierte un caso de prueba a instancias de Employee y Client.
        
        Args:
            case: Diccionario con los datos del caso
            
        Returns:
            Tupla (employees, client)
        """
        # Recrear empleados
        employees = set()
        for emp_data in case['employees_data']:
            skills_dict = {}
            for skill_name, level in emp_data['skills'].items():
                # Encontrar el enum correspondiente
                for skill in Skill.all_skills():
                    if skill.value == skill_name:
                        skills_dict[skill] = level
                        break
            
            employee = Employee(
                id=emp_data['id'],
                name=emp_data['name'],
                salary_per_hour=emp_data['salary_per_hour'],
                skills=skills_dict
            )
            employees.add(employee)
        
        # Recrear cliente
        requirements_dict = {}
        for skill_name, level in case['requirements_data'].items():
            for skill in Skill.all_skills():
                if skill.value == skill_name:
                    requirements_dict[skill] = level
                    break
        
        client = Client(requirements_dict)
        
        return employees, client
    
    @staticmethod
    def get_expected_solution(case: Dict) -> Tuple[float, set[int]]:
        """
        Obtiene la solución esperada de un caso.
        
        Args:
            case: Diccionario con los datos del caso
            
        Returns:
            Tupla (optimal_cost, optimal_solution_ids)
        """
        return case['optimal_cost'], set(case['optimal_solution_ids'])
    
    @staticmethod
    def print_case_summary(case: Dict):
        """Imprime un resumen de un caso de prueba."""
        print(f"\nCaso #{case['case_id']}:")
        print(f"  Empleados: {case['num_employees']}")
        print(f"  Requisitos: {case['num_requirements']}")
        print(f"  Solución óptima: ${case['optimal_cost']:.2f}")
        print(f"  Empleados seleccionados: {len(case['optimal_solution_ids'])}")
        print(f"  Válido: {case['is_valid']}")


def load_test_cases(filepath: str = "test_data/test_cases.json") -> List[Dict]:
    """Función de conveniencia para cargar casos."""
    cases, _ = TestCaseLoader.load_test_cases(filepath)
    return cases


if __name__ == "__main__":
    # Ejemplo de uso
    cases, metadata = TestCaseLoader.load_test_cases()
    print(f"Casos cargados: {metadata['total_cases']}")
    
    for i, case in enumerate(cases[:3]):
        TestCaseLoader.print_case_summary(case)
