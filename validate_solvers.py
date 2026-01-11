#!/usr/bin/env python3
"""
Script para validar y analizar todos los solvers implementados usando casos de prueba.

Carga casos de prueba generados con OracleSolver (solución óptima)
y prueba:
1. BacktrackSolver
2. GreedySolver
3. DPSolver
4. OracleSolver (referencia)

Analiza:
- % Correctitud (soluciones encontradas vs totales)
- % Optimalidad (costo vs óptimo)
- Tiempo de ejecución
- Gráficos comparativos
"""

import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

from elements.employee import Employee
from elements.client import Client
from elements.skills import Skill
from solver.backtrack_with_cut import BacktrackSolver
from solver.greedy_solver import GreedySolver
from solver.dp_solver import DPSolver
from solver.oracle_solver import OracleSolver
from test_cases import TestCaseLoader


@dataclass
class SolverResult:
    """Representa el resultado de probar un solver en un caso."""
    case_id: int
    num_employees: int
    num_requirements: int
    solver_name: str
    solution_found: bool
    solution_valid: bool
    solution_cost: float
    optimal_cost: float
    execution_time: float
    cost_error_percent: float  # |solver_cost - optimal| / optimal * 100
    error_message: str | None


class SolverValidator:
    """Valida todos los solvers contra casos de prueba."""
    
    def __init__(self, test_cases_file: str = "test_data/test_cases.json"):
        self.test_cases_file = test_cases_file
        self.test_cases, self.metadata = TestCaseLoader.load_test_cases(test_cases_file)
        self.results: List[SolverResult] = []
        
        self.solvers = {
            'BacktrackSolver': BacktrackSolver,
            'GreedySolver': GreedySolver,
            'DPSolver': DPSolver,
            'OracleSolver': OracleSolver
        }
    
    def validate_all_solvers(self, verbose: bool = True) -> List[SolverResult]:
        """Valida todos los solvers en todos los casos de prueba."""
        total_cases = len(self.test_cases)
        total_evals = total_cases * len(self.solvers)
        current = 0
        
        print("\n" + "=" * 80)
        print("VALIDACIÓN DE SOLVERS")
        print("=" * 80)
        print(f"Casos de prueba: {total_cases}")
        print(f"Solvers: {len(self.solvers)}")
        print(f"Total evaluaciones: {total_evals}\n")
        
        for case_idx, case in enumerate(self.test_cases):
            # Recrear problema desde caso
            try:
                employees, client = TestCaseLoader.case_to_problem(case)
            except Exception as e:
                print(f"⚠ Error recreando caso {case['case_id']}: {e}")
                continue
            
            # Obtener solución óptima esperada
            optimal_cost = case['optimal_cost']
            optimal_ids = set(case['optimal_solution_ids'])
            
            # Probar cada solver
            for solver_name, solver_class in self.solvers.items():
                current += 1
                
                if verbose and current % 10 == 0:
                    print(f"[{current}/{total_evals}] Evaluando caso {case_idx+1}/{total_cases} con {solver_name}...")
                
                result = self._test_solver(
                    case_idx=case['case_id'],
                    case=case,
                    employees=employees,
                    client=client,
                    solver_class=solver_class,
                    solver_name=solver_name,
                    optimal_cost=optimal_cost
                )
                
                self.results.append(result)
        
        print(f"\n✓ Validación completada: {len(self.results)} evaluaciones")
        return self.results
    
    def _test_solver(self, case_idx: int, case: Dict, employees: set[Employee],
                     client: Client, solver_class, solver_name: str,
                     optimal_cost: float) -> SolverResult:
        """Prueba un solver individual."""
        try:
            # Ejecutar solver con cronómetro
            start_time = time.perf_counter()
            solver = solver_class(employees, client)
            solution = solver.solve()
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            solution_found = solution.is_valid
            solution_cost = solution.total_cost if solution_found else float('inf')
            
            # Calcular error de costo
            if solution_found and optimal_cost > 0:
                cost_error_percent = ((solution_cost - optimal_cost) / optimal_cost) * 100
            else:
                cost_error_percent = float('inf') if not solution_found else 0
            
            return SolverResult(
                case_id=case_idx,
                num_employees=case['num_employees'],
                num_requirements=case['num_requirements'],
                solver_name=solver_name,
                solution_found=True,
                solution_valid=solution_found,
                solution_cost=solution_cost,
                optimal_cost=optimal_cost,
                execution_time=execution_time,
                cost_error_percent=cost_error_percent,
                error_message=None
            )
            
        except Exception as e:
            return SolverResult(
                case_id=case_idx,
                num_employees=case['num_employees'],
                num_requirements=case['num_requirements'],
                solver_name=solver_name,
                solution_found=False,
                solution_valid=False,
                solution_cost=float('inf'),
                optimal_cost=optimal_cost,
                execution_time=0.0,
                cost_error_percent=float('inf'),
                error_message=str(e)
            )
    
    def generate_report(self) -> pd.DataFrame:
        """Genera DataFrame con todos los resultados."""
        data = []
        for result in self.results:
            data.append({
                'case_id': result.case_id,
                'num_employees': result.num_employees,
                'num_requirements': result.num_requirements,
                'solver': result.solver_name,
                'solution_valid': result.solution_valid,
                'solution_cost': result.solution_cost,
                'optimal_cost': result.optimal_cost,
                'cost_error_percent': result.cost_error_percent,
                'execution_time_ms': result.execution_time * 1000,
                'error': result.error_message
            })
        
        return pd.DataFrame(data)
    
    def print_summary_stats(self):
        """Imprime estadísticas resumen."""
        df = self.generate_report()
        
        print("\n" + "=" * 100)
        print("RESUMEN POR SOLVER")
        print("=" * 100)
        
        for solver in df['solver'].unique():
            solver_data = df[df['solver'] == solver]
            valid_solutions = solver_data['solution_valid'].sum()
            total_solutions = len(solver_data)
            correctitud = (valid_solutions / total_solutions) * 100 if total_solutions > 0 else 0
            
            avg_time = solver_data['execution_time_ms'].mean()
            
            # Calcular optimalidad solo para soluciones válidas
            valid_data = solver_data[solver_data['solution_valid']]
            if len(valid_data) > 0:
                avg_cost_error = valid_data['cost_error_percent'].mean()
                max_cost_error = valid_data['cost_error_percent'].max()
            else:
                avg_cost_error = float('inf')
                max_cost_error = float('inf')
            
            print(f"\n{solver}:")
            print(f"  • Correctitud: {valid_solutions}/{total_solutions} ({correctitud:.1f}%)")
            print(f"  • Tiempo promedio: {avg_time:.2f} ms")
            if avg_cost_error != float('inf'):
                print(f"  • Error costo promedio: {avg_cost_error:+.2f}%")
                print(f"  • Error costo máximo: {max_cost_error:+.2f}%")
        
        print("\n" + "=" * 100)
    
    def plot_correctitud(self, output_file: str | None = None):
        """Gráfico de % correctitud por solver."""
        df = self.generate_report()
        
        correctitud_data = []
        for solver in df['solver'].unique():
            solver_data = df[df['solver'] == solver]
            valid = solver_data['solution_valid'].sum()
            total = len(solver_data)
            correctitud = (valid / total) * 100
            correctitud_data.append({'solver': solver, 'correctitud': correctitud})
        
        correctitud_df = pd.DataFrame(correctitud_data).sort_values('correctitud', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ca02c' if x == 100 else '#ff7f0e' if x >= 80 else '#d62728' for x in correctitud_df['correctitud']]
        bars = ax.bar(correctitud_df['solver'], correctitud_df['correctitud'], color=colors, edgecolor='black', alpha=0.7)
        
        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_ylabel('Correctitud (%)', fontsize=12, fontweight='bold')
        ax.set_title('Correctitud de Solvers (% Soluciones Válidas)', fontsize=13, fontweight='bold')
        ax.set_ylim([0, 110])
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_tiempos(self, output_file: str | None = None):
        """Gráficos de tiempo de ejecución."""
        df = self.generate_report()
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Boxplot de tiempos
        import seaborn as sns
        sns.boxplot(data=df[df['execution_time_ms'] < 1000],  # Filtrar outliers extremos
                   x='solver', y='execution_time_ms', ax=axes[0], palette='Set2')
        axes[0].set_ylabel('Tiempo (ms)', fontsize=11, fontweight='bold')
        axes[0].set_title('Distribución de Tiempos de Ejecución', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # 2. Tiempo promedio por solver
        tiempo_promedio = df.groupby('solver')['execution_time_ms'].mean().sort_values(ascending=False)
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        axes[1].bar(tiempo_promedio.index, tiempo_promedio.values, color=colors[:len(tiempo_promedio)], 
                   edgecolor='black', alpha=0.7)
        axes[1].set_ylabel('Tiempo Promedio (ms)', fontsize=11, fontweight='bold')
        axes[1].set_title('Tiempo Promedio de Ejecución', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_optimalidad(self, output_file: str | None = None):
        """Gráficos de optimalidad (error de costo)."""
        df = self.generate_report()
        df_valid = df[df['solution_valid'] & (df['cost_error_percent'] != float('inf'))]
        
        if len(df_valid) == 0:
            print("No hay datos válidos para graficar optimalidad")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Boxplot de errores de costo
        df_plot = df_valid[df_valid['cost_error_percent'] < 1000].copy()  # Filtrar outliers
        sns.boxplot(data=df_plot, x='solver', y='cost_error_percent', ax=axes[0], palette='Set2')
        axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2, label='Óptimo')
        axes[0].set_ylabel('Error de Costo (%)', fontsize=11, fontweight='bold')
        axes[0].set_title('Distribución del Error de Costo', fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # 2. Error promedio por solver
        error_promedio = df_valid.groupby('solver')['cost_error_percent'].mean().sort_values()
        colors = ['#2ca02c' if x <= 0.1 else '#ff7f0e' if x <= 10 else '#d62728' for x in error_promedio.values]
        axes[1].bar(error_promedio.index, error_promedio.values, color=colors, edgecolor='black', alpha=0.7)
        axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
        axes[1].set_ylabel('Error Promedio (%)', fontsize=11, fontweight='bold')
        axes[1].set_title('Error de Costo Promedio', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_correctitud_vs_tiempo(self, output_file: str | None = None):
        """Scatter plot: correctitud vs tiempo."""
        df = self.generate_report()
        
        stats_por_solver = []
        for solver in df['solver'].unique():
            solver_data = df[df['solver'] == solver]
            correctitud = (solver_data['solution_valid'].sum() / len(solver_data)) * 100
            tiempo_promedio = solver_data['execution_time_ms'].mean()
            stats_por_solver.append({
                'solver': solver,
                'correctitud': correctitud,
                'tiempo': tiempo_promedio
            })
        
        stats_df = pd.DataFrame(stats_por_solver)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, row in stats_df.iterrows():
            ax.scatter(row['tiempo'], row['correctitud'], s=500, alpha=0.6, label=row['solver'])
            ax.annotate(row['solver'], (row['tiempo'], row['correctitud']),
                       xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Tiempo Promedio (ms)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Correctitud (%)', fontsize=12, fontweight='bold')
        ax.set_title('Correctitud vs Tiempo de Ejecución', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 110])
        
        plt.tight_layout()
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_detailed_report(self, output_file: str = "validation_report.csv"):
        """Guarda reporte detallado en CSV."""
        df = self.generate_report()
        df.to_csv(output_file, index=False)
        print(f"✓ Reporte detallado guardado en: {output_file}")


def main():
    """Función principal."""
    print("\n" + "=" * 80)
    print("VALIDACIÓN Y ANÁLISIS DE SOLVERS")
    print("=" * 80)
    
    # Crear validador
    validator = SolverValidator(test_cases_file="test_data/test_cases.json")
    
    # Validar todos los solvers
    results = validator.validate_all_solvers(verbose=True)
    
    # Imprimir resumen
    validator.print_summary_stats()
    
    # Generar gráficos
    print("\n" + "=" * 80)
    print("GENERANDO GRÁFICOS")
    print("=" * 80)
    
    print("\n1. Gráfico de Correctitud...")
    validator.plot_correctitud(output_file="reports/correctitud.png")
    
    print("2. Gráficos de Tiempos...")
    validator.plot_tiempos(output_file="reports/tiempos.png")
    
    print("3. Gráficos de Optimalidad...")
    validator.plot_optimalidad(output_file="reports/optimalidad.png")
    
    print("4. Gráfico Correctitud vs Tiempo...")
    validator.plot_correctitud_vs_tiempo(output_file="reports/correctitud_vs_tiempo.png")
    
    # Guardar reporte detallado
    print("\n5. Generando reporte detallado...")
    Path("reports").mkdir(exist_ok=True)
    validator.save_detailed_report(output_file="reports/validation_report.csv")
    
    print("\n✅ Análisis completado.")
    print("\nArchivos generados:")
    print("  - reports/correctitud.png")
    print("  - reports/tiempos.png")
    print("  - reports/optimalidad.png")
    print("  - reports/correctitud_vs_tiempo.png")
    print("  - reports/validation_report.csv")


if __name__ == "__main__":
    main()
