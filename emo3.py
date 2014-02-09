import random
import time
import inspyred
from emo_tool import get_info, evaluate, cross_tool, mutate_tool, generate

@inspyred.ec.evaluators.evaluator
def evaluator(candidate, args):
	type_info_price = args.get("type_info_price")
	type_info_ecu = args.get("type_info_ecu")
	task_base_time = args.get("task_base_time")
	task_preds = args.get("task_preds")
	comm_speeds = args.get("comm_speeds")
	comm_sizes = args.get("comm_sizes")
	n_tasks = args.get("n_tasks")
	n_nodes = args.get("n_tasks")
	n_types = args.get("n_types")

	fitness = evaluate(candidate, type_info_price,
		               type_info_ecu,
		               task_base_time,
		               task_preds,
		               comm_speeds,
		               comm_sizes,
		               n_tasks,
		               n_nodes,
		               n_types)
	return inspyred.ec.emo.Pareto(fitness)

def generator(random, args):
	n_tasks = args.get("n_tasks")
	n_types = args.get("n_types")
	return generate(random, n_tasks, n_types)

@inspyred.ec.variators.crossover
def cross(random, mom, dad, args):
	n_tasks = args.get("n_tasks")
	return cross_tool(random, mom, dad, n_tasks)

@inspyred.ec.variators.mutator
def mutate(random, candidate, args):
	n_tasks = args.get("n_tasks")
	n_types = args.get("n_types")
	return mutate_tool(random, candidate, n_tasks, n_types)

def nsga_2(task_names,
		   type_names, 
		   type_info_price,
		   type_info_ecu,
		   task_base_time,
		   task_preds,
		   comm_speeds,
		   comm_sizes):

	prng = random.Random()
	prng.seed(time.time())

	ea = inspyred.ec.emo.NSGA2(prng)
	ea.variator = [cross, mutate]
	ea.terminator = inspyred.ec.terminators.generation_termination	
	final_pop = ea.evolve(generator=generator,
						  evaluator=evaluator,
						  # evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,
						  # mp_evaluator=evaluator,
						  # pp_dependencies=(evaluate,),
						  # pp_modules=("emo_tool",),
						  pop_size=100,
						  maximize=False,
						  max_generations=100,
						  n_types=len(type_names),
						  n_tasks=len(task_names),
						  task_names=task_names,
						  type_names=type_names, 
						  type_info_price=type_info_price,
						  type_info_ecu=type_info_ecu,
						  task_base_time=task_base_time,
						  task_preds=task_preds,
						  comm_speeds=comm_speeds,
						  comm_sizes=comm_sizes)

	s = set()
	ar = []
	for i in ea.archive:
		if tuple(i.fitness) not in s:
			s.add(tuple(i.fitness))
			ar.append(i)
	return ar

if __name__ == '__main__':
	from sys import argv
	from workflow import Workflow
	from pool import AWS
	import hotshot, hotshot.stats

	wf = Workflow(argv[1])
	pool = AWS("aws.info")


	ar = nsga_2(*get_info(wf, pool))

	# prof = hotshot.Profile("emo3.prof")
	# archive = prof.runcall(nsga_2, *get_info(wf, pool))
	# prof.close()
	# prof.close()
	# stats = hotshot.stats.load("emo3.prof")
	# stats.strip_dirs()
	# stats.sort_stats('time', 'calls')
	# stats.print_stats()
	ar.sort(key=lambda x: x.fitness[0])

	for i in range(len(ar)):
		print "[%d]: Makespan: %.0fs\tCost: $%.2f" % (i, ar[i].fitness[0], ar[i].fitness[1])
	

