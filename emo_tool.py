import math
import copy
import array
import itertools


def get_info(wf, pool):
	n_tasks = len(wf)
	n_types = len(pool.info)
	type_names = pool.info.keys()
	task_names = wf.topological_sort()
	type_info_price = array.array('f', [pool.info[type_names[i]]["price"] for i in range(n_types)])
	type_info_ecu = array.array('f', [pool.info[type_names[i]]["ecu"] for i in range(n_types)])
	task_base_time = array.array('f', [wf.get_cost(t) for t in task_names])
	task_preds = tuple((tuple(array.array('I', [task_names.index(t) for t in wf.pred(t0)])) for t0 in task_names))
	comm_speeds = tuple((tuple((min([pool.info[t0]["net"], pool.info[t1]["net"]])) for t1 in type_names) for t0 in type_names))
	comm_sizes = tuple((tuple((wf.get_data_size(t0, t1) for t1 in task_names)) for t0 in task_names))
	
	return task_names, 		\
		   type_names, 		\
		   type_info_price, \
		   type_info_ecu, 	\
		   task_base_time, 	\
		   task_preds, 		\
		   comm_speeds, 	\
		   comm_sizes

def generate(random, n_tasks, n_types):
	def cycle(*args):
		for x in itertools.izip(*args):
			for a in x:
				yield a
	return array.array("I", cycle([random.randint(0, n_tasks-1) for _ in range(n_tasks)], [random.randint(0, n_types-1) for _ in range(n_tasks)]))

def evaluate(candidate, type_info_price,
			 type_info_ecu,
			 task_base_time,
			 task_preds,
			 comm_speeds,
			 comm_sizes,
			 n_tasks,
			 n_nodes,
			 n_types):

	c_task_node = lambda x:candidate[x*2]
	c_node_type = lambda x:candidate[x*2+1]

	aft = array.array('f', [0] * n_tasks)
	nodes_avail = array.array('f', [0] * n_nodes)
	nodes_start = array.array('f', [-1] * n_nodes)

	for task_index in range(n_tasks):
		task_node = c_task_node(task_index)
		node_type = c_node_type(task_node)
		comp_time = round(task_base_time[task_index] / type_info_ecu[node_type])
		aft[task_index] = comp_time
		ast = 0
		for ti in task_preds[task_index]:
			ti_node = c_task_node(ti)
			ti_type = c_node_type(ti_node)
			if ti_node == task_node:
				comm_time = 0
			else:
				speed = comm_speeds[ti_type][node_type]
				comm_time = round(comm_sizes[ti][task_index]/speed)
			est = comm_time + aft[ti]
			eft = comp_time + est
			if aft[task_index] < eft:
				aft[task_index] = eft
				ast = est
		if ast < nodes_avail[task_node]:
			ast = nodes_avail[task_node]
			aft[task_index] = ast + comp_time
		if nodes_start[task_node] < 0:
			nodes_start[task_node] = ast
		nodes_avail[task_node] = aft[task_index]

	o_time = max(nodes_avail)

	o_cost = 0
	for start, end, index in itertools.izip(nodes_start, nodes_avail, range(n_nodes)):
		if start >= 0:
			o_cost += math.ceil((end - start) / 3600) * type_info_price[c_node_type(index)]

	return round(o_time, 0), round(o_cost, 2)

def cross_tool(random, mom, dad, n_tasks):
	c = copy.deepcopy(mom)

	for i in range(random.randint(0, n_tasks-1), n_tasks):
		c[i*2] = dad[i*2]

	for i in range(random.randint(0, n_tasks-1), n_tasks):
		c[i*2+1] = dad[i*2+1]

	return [c]

def mutate_tool(random, candidate, n_tasks, n_types):
	for i in range(n_tasks):
		p = random.random()
		if p <= 1.0/n_tasks:
			candidate[i*2] = random.randint(0, n_tasks-1)
		p = random.random()
		if p <= 1.0/n_tasks:
			candidate[i*2+1] = random.randint(0, n_types-1)
	return candidate