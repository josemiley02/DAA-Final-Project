from solver.oracle_solver import OracleSolver
from solver.problem_solver import ProblemSolver
from tester.instance_generator import InstanceGenerator
from tester.metrics_collector import MetricsCollector


class ProblemTester:
    def __init__(
        self,
        solver_cls: ProblemSolver,
        generator: InstanceGenerator,
        metrics: MetricsCollector
    ):
        self.solver_cls = solver_cls
        self.generator = generator
        self.metrics = metrics

    def run_experiment(
        self,
        employee_sizes: list[int],
        repetitions: int = 5
    ):
        for n in employee_sizes:
            for _ in range(repetitions):
                employees = self.generator.generate_employees(n)
                client = self.generator.generate_client()

                solver = self.solver_cls(employees, client)
                oracle = OracleSolver(employees, client)
                result = self.metrics.evaluate_with_oracle(solver, oracle)


                result["employees"] = n
                self.metrics.results.append(result)
