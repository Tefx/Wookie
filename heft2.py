import itertools
import array


def calculate_rank_u(task, rank_u, type_info_ecu, task_base_time, task_seccs, comm_speeds, comm_sizes):

	n_tasks = len(type_info_ecu)
	n_types = len(task_base_time)

	average_comp_cost = lambda x: sum([task_base_time[x]/type_info_ecu[i] for i in type_info_ecu]) / n_types
	average_comm_cost = lambda x: sum([x/comm_speeds[i][j] for i, j in itertools.product(range(n_types), range(n_types))]) / (n_types * n_types) 

	if rank_u[task] >= 0:
		return rank_u[task]
	elif task == n_tasks -1:
		rank_u[task] = average_comp_cost(task)
		return rank_u[task]
	else:
		rank_u[task] = \
			average_comp_cost(task) + \
				max([
					average_comm_cost(comm_sizes[task][t]) + \
						calculate_rank_u(t, rank_u, type_info_ecu, task_base_time, task_seccs, comm_speeds, comm_sizes) \
					for t in task_seccs[task]
					])
		return rank_u[task]


def heft2(type_info_price,
		  type_info_ecu,
		  task_base_time,
		  task_preds,
		  comm_speeds,
		  comm_sizes,
		  task_seccs):

	n_tasks = len(task_base_time)
	n_types = len(type_info_ecu)

	rank_u = array.array("f", [0] * n_tasks)
	calculate_rank_u(0, rank_u, type_info_ecu, task_base_time, task_seccs, comm_speeds, comm_sizes)

	ts = sorted(range(n_tasks), key=lambda x:rank_u[x])

	aft = array.array("f", [0] * n_tasks)
	loc = array.array("i", [-1] * n_tasks)
	types = array.array("I", range(n_types))
	avail = array.array("I", range(n_types))
	avail_time = array.array("f", [-1] * n_types)

	while len(ts):
		task = ts.pop(0)
		eft_min = -1
		est_min = 0
		for node in avail:
			if task == 0:
				est = 0
			else:
				est = max([
					aft[t] + \
						comm_sizes[t][task] / comm_speeds[types[loc[t]]][types[node]] \
						for t in task_preds[task]
					])
			if est < avail_time[node]:
				est = avail_time[node]
			eft = est + task_base_time[task] / type_info_ecu[types[node]]
			if eft_min == -1 or eft_min > eft:
				est_min, eft_min = est, eft
				loc[task] = node
		aft[task] = eft_min
		chosen_node = loc[task]
		if avail_time[chosen_node] == -1:
			avail.append(len(avail))
			types.append(types[chosen_node])
			avail_time.append(-1)
		avail_time[chosen_node] = aft[task]

	return round(aft[n_tasks-1]), loc, types

def get_chromosome(loc, types):
	n_tasks = len(loc)
	for n in range(n_tasks):
		if loc[n] >= n_tasks:
			for t in range(len(types)):
				if t not in loc:
					types[t] = types[loc[n]]
					types[loc[n]] = 0
					loc[n] = t
					break
	if len(types) > n_tasks:
		types = types[:n_tasks]

	c = array.array("I", [])
	for l, t in itertools.izip_longest(loc, types, fillvalue=0):
		c.append(l)
		c.append(t)
	return c

if __name__ == '__main__':
	from sys import argv
	from workflow import Workflow
	from pool import AWS
	from emo_tool import get_info, evaluate
	from log import get_details
	from plot import stat, trans, show

	wf = Workflow(argv[1])
	pool = AWS("aws.info")
	info = get_info(wf, pool)

	_, loc, ts = heft2(*info[2:])
	c = get_chromosome(loc, ts)
	makespan, cost = evaluate(c, *info[2:-1], n_tasks=len(loc), n_nodes=len(loc), n_types=len(info[1]))
	scheme = get_details(c, *info[:-1],  n_tasks=len(loc), n_nodes=len(loc), n_types=len(info[1]))
	scheme = [(n,)+v for n,v in scheme.iteritems()]

	print "Makespan: %.0fs\tCost: $%.2f" % (makespan, cost)
	# stat(scheme)
	# show(*trans(scheme))