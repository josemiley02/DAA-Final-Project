from solver.backtrack_with_cut import BackatrackSolver
from tester.instance_generator import InstanceGenerator
from tester.metrics_collector import MetricsCollector
from tester.problem_tester import ProblemTester


pt = ProblemTester(solver_cls=BackatrackSolver, 
                   generator=InstanceGenerator(), 
                   metrics=MetricsCollector())

pt.run_experiment(employee_sizes=[10], repetitions=10)
for result in pt.metrics.results:
    print(result)