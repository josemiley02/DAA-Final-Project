from solver.backtrack_with_cut import BacktrackSolver
from tester.instance_generator import InstanceGenerator
from tester.metrics_collector import MetricsCollector
from tester.problem_tester import ProblemTester


pt = ProblemTester(generator=InstanceGenerator(), 
                   metrics=MetricsCollector())

pt.add_solver(BacktrackSolver)

pt.run_experiment(employee_sizes=[5,10,15], repetitions=10)
for result in pt.metrics.results:
    print(result)

print(pt.metrics.get_summary())