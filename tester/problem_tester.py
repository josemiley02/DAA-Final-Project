from typing import Type
from elements.client import Client
from elements.employee import Employee
from solver.problem_solver import ProblemSolver, Solution
from tester.instance_generator import InstanceGenerator
from tester.metrics_collector import MetricsCollector


class ProblemTester:
    """
    Clase para ejecutar experimentos comparativos entre diferentes solvers.
    
    Permite:
    - Ejecutar un solver sobre múltiples tamaños de instancia
    - Comparar múltiples solvers sobre las mismas instancias
    - Recolectar métricas de rendimiento
    """
    
    def __init__(
        self,
        generator: InstanceGenerator,
        metrics: MetricsCollector | None = None
    ):
        self.generator = generator
        self.metrics = metrics or MetricsCollector()
        self.solver_classes: list[Type[ProblemSolver]] = []
    
    def add_solver(self, solver_cls: Type[ProblemSolver]) -> 'ProblemTester':
        """
        Agrega un solver para comparación.
        
        Args:
            solver_cls: Clase del solver (no instancia).
            
        Returns:
            self: Para encadenamiento de métodos.
        """
        self.solver_classes.append(solver_cls)
        return self
    
    def add_solvers(self, *solver_classes: Type[ProblemSolver]) -> 'ProblemTester':
        """
        Agrega múltiples solvers para comparación.
        
        Args:
            *solver_classes: Clases de solvers.
            
        Returns:
            self: Para encadenamiento de métodos.
        """
        self.solver_classes.extend(solver_classes)
        return self

    def run_experiment(
        self,
        employee_sizes: list[int],
        repetitions: int = 5,
        min_requirements: int = 1,
        max_requirements: int = 4,
        verbose: bool = False
    ) -> list[dict]:
        """
        Ejecuta experimentos para todos los solvers registrados.
        
        Args:
            employee_sizes: Lista de tamaños de empleados a probar.
            repetitions: Número de repeticiones por tamaño.
            min_requirements: Mínimo de requerimientos del cliente.
            max_requirements: Máximo de requerimientos del cliente.
            verbose: Si es True, imprime progreso.
            
        Returns:
            list[dict]: Todos los resultados recolectados.
        """
        if not self.solver_classes:
            raise ValueError("No hay solvers registrados. Use add_solver() primero.")
        
        total_experiments = len(employee_sizes) * repetitions * len(self.solver_classes)
        current = 0
        
        for n in employee_sizes:
            for rep in range(repetitions):
                # Generar instancia común para todos los solvers
                employees = self.generator.generate_employees(n)
                client = self.generator.generate_client(min_requirements, max_requirements)
                
                for solver_cls in self.solver_classes:
                    current += 1
                    
                    if verbose:
                        print(f"[{current}/{total_experiments}] "
                              f"{solver_cls.__name__} - n={n}, rep={rep+1}")
                    
                    try:
                        solver = solver_cls(employees, client)
                        result = self.metrics.evaluate(solver)
                        result["num_employees"] = n
                        result["num_requirements"] = len(client.requirements)
                        result["repetition"] = rep + 1
                        result["error"] = None
                        self.metrics.results.append(result)
                        
                    except Exception as e:
                        # Capturar errores (ej: DP con muchos requerimientos)
                        self.metrics.results.append({
                            "algorithm": solver_cls.__name__,
                            "num_employees": n,
                            "num_requirements": len(client.requirements),
                            "repetition": rep + 1,
                            "error": str(e),
                            "is_valid": False
                        })
        
        return self.metrics.results
    
    def run_single_comparison(
        self,
        employees: set[Employee],
        client: Client,
        verbose: bool = False
    ) -> list[dict]:
        """
        Compara todos los solvers sobre una única instancia específica.
        
        Args:
            employees: Conjunto de empleados.
            client: Cliente con requerimientos.
            verbose: Si es True, imprime resultados.
            
        Returns:
            list[dict]: Resultados de cada solver.
        """
        results = []
        
        for solver_cls in self.solver_classes:
            try:
                solver = solver_cls(employees, client)
                result = self.metrics.evaluate(solver)
                result["error"] = None
                results.append(result)
                
                if verbose:
                    status = "✓" if result["is_valid"] else "✗"
                    print(f"{status} {result['algorithm']}: "
                          f"costo={result['solution_cost']:.2f}, "
                          f"tiempo={result['time_formatted']}")
                    
            except Exception as e:
                results.append({
                    "algorithm": solver_cls.__name__,
                    "error": str(e),
                    "is_valid": False
                })
                if verbose:
                    print(f"✗ {solver_cls.__name__}: ERROR - {e}")
        
        return results
    
    def print_summary(self) -> None:
        """Imprime un resumen de los resultados recolectados."""
        summary = self.metrics.get_summary()
        
        if not summary:
            print("No hay resultados para mostrar.")
            return
        
        print("\n" + "="*60)
        print("RESUMEN DE EXPERIMENTOS")
        print("="*60)
        
        for algo, stats in summary.items():
            print(f"\n{algo}:")
            print(f"  Ejecuciones: {stats['total_runs']}")
            print(f"  Soluciones válidas: {stats['valid_solutions']}")
            print(f"  Tiempo promedio: {stats['avg_time']*1000:.2f} ms")
            print(f"  Tiempo (min/max): {stats['min_time']*1000:.2f} / {stats['max_time']*1000:.2f} ms")
            if stats['valid_solutions'] > 0:
                print(f"  Costo promedio: {stats['avg_cost']:.2f}")
                print(f"  Costo (min/max): {stats['min_cost']:.2f} / {stats['max_cost']:.2f}")
        
        print("\n" + "="*60)
