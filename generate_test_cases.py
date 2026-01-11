#!/usr/bin/env python3
"""
Script para generar casos de prueba exhaustivos y guardarlos en JSON.

Genera instancias variadas:
- Número de empleados: 3-25
- Número de habilidades: 1-7
- Número de requisitos: 1-7
- Niveles de dominio variados
- Salarios variados

Usa OracleSolver para encontrar la solución óptima y guarda (input, output) en JSON.
Guardado INCREMENTAL: Guarda cada lote de casos apenas se generan.
"""

import json
import random
from typing import Any
from dataclasses import dataclass, asdict
from pathlib import Path

from elements.employee import Employee
from elements.client import Client
from elements.skills import Skill
from solver.oracle_solver import OracleSolver
from tester.instance_generator import InstanceGenerator


@dataclass
class TestCase:
    """Representa un caso de prueba."""
    case_id: int
    num_employees: int
    num_requirements: int
    employees_data: list[dict]  # Datos para recrear empleados
    requirements_data: dict[str, int]  # Requisitos (nombre skill -> nivel)
    optimal_cost: float
    optimal_solution_ids: list[int]


class TestCaseGenerator:
    """Genera casos de prueba variados para el problema de selección de talento."""
    
    def __init__(self, output_file: str = "test_data/test_cases.json"):
        self.output_file = output_file
        self.output_path = Path(output_file)
        self.case_counter = 0
        self.all_skills = Skill.all_skills()
        
        # Crear carpeta si no existe
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar JSON con estructura vacía
        self._initialize_json()
    
    def _initialize_json(self):
        """Inicializa el archivo JSON con estructura vacía."""
        data = {
            "metadata": {
                "total_cases": 0,
                "description": "Casos de prueba generados para validar solvers del problema de selección óptima de talento",
                "solver_used": "OracleSolver",
                "format": "Cada caso contiene employees_data, requirements_data, optimal_cost, optimal_solution_ids"
            },
            "test_cases": []
        }
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _append_cases_to_json(self, new_cases: list[TestCase], category_name: str):
        """Agrega casos al JSON de forma incremental."""
        # Leer JSON actual
        with open(self.output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convertir casos a dicts
        cases_dicts = [asdict(case) for case in new_cases]
        
        # Agregar casos
        data['test_cases'].extend(cases_dicts)
        data['metadata']['total_cases'] = len(data['test_cases'])
        
        # Escribir JSON actualizado
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_all_test_cases(self):
        """Genera todos los tipos de casos de prueba."""
        print("=" * 80)
        print("GENERADOR DE CASOS DE PRUEBA (GUARDADO INCREMENTAL)")
        print("=" * 80)
        
        # Casos simples: pocos empleados, pocos requisitos
        cases = self._generate_simple_cases()
        self._append_cases_to_json(cases, "Simples")
        print(f"✓ Casos simples guardados: {len(cases)} casos")
        
        # Casos medianos
        cases = self._generate_medium_cases()
        self._append_cases_to_json(cases, "Medianos")
        print(f"✓ Casos medianos guardados: {len(cases)} casos")
        
        # Casos complejos
        cases = self._generate_complex_cases()
        self._append_cases_to_json(cases, "Complejos")
        print(f"✓ Casos complejos guardados: {len(cases)} casos")
        
        # Casos edge (bordes)
        cases = self._generate_edge_cases()
        self._append_cases_to_json(cases, "Edge")
        print(f"✓ Casos edge guardados: {len(cases)} casos")
        
        # Casos con variaciones especiales
        cases = self._generate_special_cases()
        self._append_cases_to_json(cases, "Especiales")
        print(f"✓ Casos especiales guardados: {len(cases)} casos")
    
    def _generate_simple_cases(self) -> list[TestCase]:
        """Genera casos simples (3-8 empleados, 1-3 requisitos)."""
        generator = InstanceGenerator(seed=42)
        cases = []
        
        # Caso 1: Mínimo viable (3 empleados, 1 requisito)
        for seed_val in range(5):
            generator.reset_seed(seed_val)
            employees = generator.generate_employees(n=3, min_skills=1, max_skills=2)
            client = generator.generate_client(min_req=1, max_req=1, min_level=1, max_level=5)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 2: Pequeño (5 empleados, 2 requisitos)
        for seed_val in range(5):
            generator.reset_seed(seed_val + 100)
            employees = generator.generate_employees(n=5, min_skills=2, max_skills=3)
            client = generator.generate_client(min_req=2, max_req=2, min_level=1, max_level=6)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 3: Balance (8 empleados, 3 requisitos)
        for seed_val in range(5):
            generator.reset_seed(seed_val + 200)
            employees = generator.generate_employees(n=8, min_skills=2, max_skills=4)
            client = generator.generate_client(min_req=3, max_req=3, min_level=2, max_level=7)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        return cases
    
    def _generate_medium_cases(self) -> list[TestCase]:
        """Genera casos medianos (10-16 empleados, 2-5 requisitos)."""
        generator = InstanceGenerator(seed=300)
        cases = []
        
        # Caso 4: Mediano bajo
        for seed_val in range(5):
            generator.reset_seed(seed_val + 300)
            employees = generator.generate_employees(n=10, min_skills=2, max_skills=4)
            client = generator.generate_client(min_req=2, max_req=4, min_level=1, max_level=7)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 5: Mediano alto
        for seed_val in range(5):
            generator.reset_seed(seed_val + 400)
            employees = generator.generate_employees(n=13, min_skills=3, max_skills=5)
            client = generator.generate_client(min_req=3, max_req=5, min_level=2, max_level=8)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 6: Mediano grande
        for seed_val in range(5):
            generator.reset_seed(seed_val + 500)
            employees = generator.generate_employees(n=16, min_skills=3, max_skills=6)
            client = generator.generate_client(min_req=4, max_req=5, min_level=2, max_level=8)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        return cases
    
    def _generate_complex_cases(self) -> list[TestCase]:
        """Genera casos complejos (18-25 empleados, 4-7 requisitos)."""
        generator = InstanceGenerator(seed=600)
        cases = []
        
        # Caso 7: Complejo bajo
        for seed_val in range(4):
            generator.reset_seed(seed_val + 600)
            employees = generator.generate_employees(n=18, min_skills=3, max_skills=6)
            client = generator.generate_client(min_req=4, max_req=5, min_level=2, max_level=9)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 8: Complejo alto
        for seed_val in range(4):
            generator.reset_seed(seed_val + 700)
            employees = generator.generate_employees(n=22, min_skills=4, max_skills=7)
            client = generator.generate_client(min_req=5, max_req=7, min_level=3, max_level=9)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 9: Muy complejo
        for seed_val in range(3):
            generator.reset_seed(seed_val + 800)
            employees = generator.generate_employees(n=25, min_skills=5, max_skills=7)
            client = generator.generate_client(min_req=6, max_req=7, min_level=3, max_level=10)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        return cases
    
    def _generate_edge_cases(self) -> list[TestCase]:
        """Genera casos edge (bordes especiales)."""
        generator = InstanceGenerator(seed=900)
        cases = []
        
        # Caso 10: Todos tienen la misma habilidad requerida
        for seed_val in range(3):
            generator.reset_seed(seed_val + 900)
            employees = generator.generate_employees(n=7, min_skills=1, max_skills=1)
            client = generator.generate_client(min_req=1, max_req=1, min_level=5, max_level=5)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 11: Muchos requisitos, pocos empleados (sobredemanda)
        for seed_val in range(3):
            generator.reset_seed(seed_val + 950)
            employees = generator.generate_employees(n=5, min_skills=2, max_skills=3)
            client = generator.generate_client(min_req=6, max_req=7, min_level=1, max_level=10)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 12: Un solo empleado puede cumplir todo
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1000)
            employees = generator.generate_employees(n=8, min_skills=7, max_skills=7)  # Todos tienen todas
            client = generator.generate_client(min_req=3, max_req=5, min_level=1, max_level=5)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 13: Requisitos muy altos
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1050)
            employees = generator.generate_employees(n=12, min_skills=3, max_skills=6)
            client = generator.generate_client(min_req=3, max_req=5, min_level=8, max_level=10)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 14: Requisitos muy bajos
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1100)
            employees = generator.generate_employees(n=10, min_skills=2, max_skills=4)
            client = generator.generate_client(min_req=2, max_req=4, min_level=1, max_level=3)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        return cases
    
    def _generate_special_cases(self) -> list[TestCase]:
        """Genera casos especiales con características únicas."""
        generator = InstanceGenerator(seed=1200)
        cases = []
        
        # Caso 15: Salarios muy variados (algunos muy caros)
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1200)
            generator.min_salary = 5
            generator.max_salary = 200  # Gran diferencia
            employees = generator.generate_employees(n=10, min_skills=2, max_skills=5)
            client = generator.generate_client(min_req=2, max_req=4, min_level=1, max_level=7)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 16: Salarios muy uniformes
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1300)
            generator.min_salary = 50
            generator.max_salary = 55  # Muy similares
            employees = generator.generate_employees(n=10, min_skills=2, max_skills=5)
            client = generator.generate_client(min_req=2, max_req=4, min_level=1, max_level=7)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 17: Especialización: cada empleado tiene 1-2 habilidades únicas
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1400)
            generator.min_salary = 10
            generator.max_salary = 100
            employees = generator.generate_employees(n=12, min_skills=1, max_skills=2)
            client = generator.generate_client(min_req=4, max_req=6, min_level=1, max_level=8)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 18: Generalistas: todos tienen muchas habilidades
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1500)
            generator.min_salary = 10
            generator.max_salary = 100
            employees = generator.generate_employees(n=8, min_skills=5, max_skills=7)
            client = generator.generate_client(min_req=3, max_req=5, min_level=3, max_level=7)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        # Caso 19: Mix extremo - algunos expertos, otros principiantes
        for seed_val in range(3):
            generator.reset_seed(seed_val + 1600)
            generator.min_salary = 10
            generator.max_salary = 100
            # Generar mitad con niveles altos, mitad con bajos
            employees = set()
            
            generator.max_skill_level = 10
            emp_high = list(generator.generate_employees(n=6, min_skills=2, max_skills=4))
            for i, emp in enumerate(emp_high):
                emp.id = i + 1
                employees.add(emp)
            
            generator.max_skill_level = 3
            emp_low = list(generator.generate_employees(n=6, min_skills=2, max_skills=4))
            for i, emp in enumerate(emp_low):
                emp.id = len(employees) + i + 1
                employees.add(emp)
            
            generator.max_skill_level = 10  # Reset
            client = generator.generate_client(min_req=3, max_req=5, min_level=2, max_level=8)
            case = self._evaluate_and_store(employees, client)
            if case:
                cases.append(case)
        
        return cases
    
    def _evaluate_and_store(self, employees: set[Employee], client: Client) -> TestCase | None:
        """Evalúa un caso con OracleSolver y lo retorna."""
        try:
            # Resolver con Oracle
            oracle = OracleSolver(employees, client)
            solution = oracle.solve()
            
            # Preparar datos del input
            employees_data = []
            for emp in employees:
                emp_dict = {
                    "id": emp.id,
                    "name": emp.name,
                    "salary_per_hour": emp.salary_per_hour,
                    "skills": {skill.value: level for skill, level in emp.skills.items()}
                }
                employees_data.append(emp_dict)
            
            # Preparar datos de requisitos
            requirements_data = {skill.value: level for skill, level in client.requirements.items()}
            
            # Crear caso de prueba
            test_case = TestCase(
                case_id=self.case_counter,
                num_employees=len(employees),
                num_requirements=len(client.requirements),
                employees_data=employees_data,
                requirements_data=requirements_data,
                optimal_cost=sum([emp.salary_per_hour for emp in solution]),
                optimal_solution_ids=[emp.id for emp in solution],
            )
            
            self.case_counter += 1
            return test_case
            
        except Exception as e:
            print(f"⚠ Error al evaluar caso: {e}")
            return None
    
    def print_summary(self):
        """Imprime un resumen de los casos generados desde el JSON."""
        print("\n" + "=" * 80)
        print("RESUMEN DE CASOS GENERADOS")
        print("=" * 80)
        
        # Leer datos del JSON
        with open(self.output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data['test_cases']
        total = len(cases)
        print(f"Total de casos: {total}")
        
        valid_cases = sum(1 for case in cases if case['is_valid'])
        print(f"Casos válidos: {valid_cases}")
        print(f"Casos sin solución: {total - valid_cases}")
        
        # Estadísticas
        emp_counts = [case['num_employees'] for case in cases]
        req_counts = [case['num_requirements'] for case in cases]
        costs = [case['optimal_cost'] for case in cases if case['is_valid']]
        
        print(f"\nEmpleados por caso:")
        print(f"  Min: {min(emp_counts)}, Max: {max(emp_counts)}, Promedio: {sum(emp_counts)/len(emp_counts):.1f}")
        
        print(f"\nRequisitos por caso:")
        print(f"  Min: {min(req_counts)}, Max: {max(req_counts)}, Promedio: {sum(req_counts)/len(req_counts):.1f}")
        
        if costs:
            print(f"\nCostos óptimos:")
            print(f"  Min: ${min(costs):.2f}, Max: ${max(costs):.2f}, Promedio: ${sum(costs)/len(costs):.2f}")
        
        print("=" * 80)


def main():
    """Función principal."""
    print("\n🚀 Iniciando generación de casos de prueba (GUARDADO INCREMENTAL)...\n")
    
    generator = TestCaseGenerator(output_file="test_data/test_cases.json")
    
    # Generar todos los casos con guardado incremental
    generator.generate_all_test_cases()
    
    print(f"\n✓ Todos los casos han sido generados y guardados incrementalmente")
    print(f"✓ Archivo: {generator.output_path}")
    
    # Mostrar resumen
    generator.print_summary()
    
    print("\n✅ Proceso completado.")
    print("\nPuedes usar los casos de prueba para validar otros solvers con:")
    print("  from test_cases import load_test_cases")


if __name__ == "__main__":
    main()
