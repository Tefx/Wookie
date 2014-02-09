import random
import array
from deap import creator, base, algorithms, tools
from emo_tool import get_info, evaluate, cross_tool, mutate_tool, generate
import multiprocessing

def nsga_2(task_names,
		   type_names, 
		   type_info_price,
		   type_info_ecu,
		   task_base_time,
		   task_preds,
		   comm_speeds,
		   comm_sizes):
	
	n_tasks = len(task_names)
	n_nodes = n_tasks
	n_types = len(type_names)

	creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
	creator.create("Individual", array.array, typecode='I', fitness=creator.FitnessMulti)

	toolbox = base.Toolbox()
	toolbox.register("task2node", random.randint, 0, n_tasks-1)
	toolbox.register("node2type", random.randint, 0, n_types-1)
	toolbox.register("individual", tools.initCycle, creator.Individual, 
					 (toolbox.task2node, toolbox.node2type), n=n_tasks)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("evaluate", evaluate, type_info_price=type_info_price, 
										   type_info_ecu=type_info_ecu,
										   task_base_time=task_base_time,
										   task_preds=task_preds,
										   comm_speeds=comm_speeds,
										   comm_sizes=comm_sizes,
										   n_tasks=n_tasks,
										   n_nodes=n_nodes,
										   n_types=n_types)
	toolbox.register("mate", cross_tool, n_tasks=n_tasks, inplace=True)
	toolbox.register("mutate", mutate_tool, n_tasks=n_tasks, n_types=n_types, multi=True)
	toolbox.register("select", tools.selNSGA2)

	# pool = multiprocessing.Pool()
	# toolbox.register("map", pool.map)

	pop = toolbox.population(10)
	# hof = tools.ParetoFront()
	# hof.update(pop)

	fits = toolbox.map(toolbox.evaluate, pop)
	for fit, ind in zip(fits, pop):
		ind.fitness.values = fit

	for gen in range(100*n_tasks):
		offspring = tools.selTournament(pop, 10, 2)
		offspring = toolbox.map(toolbox.clone, offspring)

		for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
			# if random.random() <= 0.5:
			toolbox.mate(ind1, ind2)
			del ind1.fitness.values, ind2.fitness.values

		for ind in offspring:
			if random.random() <= 0.5:
				toolbox.mutate(ind)
				del ind.fitness.values

		invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
		fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
		for ind, fit in zip(invalid_ind, fitnesses):
			ind.fitness.values = fit

		pop = toolbox.select(pop + offspring, 10)
		# hof.update(offspring)
		# pop = hof

	s = set()
	ar = []
	for i in pop:
		if tuple(i.fitness.values) not in s:
			s.add(tuple(i.fitness.values))
			ar.append(i)
	return ar

if __name__ == '__main__':
	from sys import argv
	from workflow import Workflow
	from pool import AWS

	wf = Workflow(argv[1])
	pool = AWS("aws.info")


	ar = nsga_2(*get_info(wf, pool))
	ar.sort(key=lambda x: x.fitness.values[0])

	for i in range(len(ar)):
		print "[%d]: Makespan: %.0fs\tCost: $%.2f" % (i, ar[i].fitness.values[0], ar[i].fitness.values[1])