import pickle
import array
import itertools

def get_details(candidate, 
				task_names,
				type_names,
				type_info_price,
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
	scheme = {}

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
		nodes_avail[task_node] = aft[task_index]
		if task_node not in scheme:
			scheme[task_node] = (type_names[node_type], [(task_names[task_index], ast, aft[task_index])])
		else:
			scheme[task_node][1].append((task_names[task_index], ast, aft[task_index]))

	return scheme

def dump(filename, ar, *args):
	l = []
	for i in ar:
		r = []
		for n, v in get_details(i, *args).iteritems():
			r.append((n,)+v)
		l.append(i.fitness.values + (r,))
	pickle.dump(l, open(filename, "w"))

