def calculate_rank_u(task, rank_u, pool, workflow):
	if task in rank_u:
		return rank_u[task]
	elif task == "exit":
		rank_u[task] = pool.average_cost(workflow.get_cost(task))
		return rank_u[task]
	else:
		ac = workflow.get_cost(task)
		rank_u[task] = ac + max(
					[pool.average_comm_cost(workflow.get_data_size(task, t)) + \
					calculate_rank_u(t, rank_u, pool, workflow) for t in workflow.secc(task)]
				)
	return rank_u[task]

def schedule(workflow, pool):
	rank_u = {}
	calculate_rank_u("entry", rank_u, pool, workflow)
	ts = sorted(workflow.tasks(), key=lambda x:rank_u[x])
	aft = {}
	loc = {}
	while len(ts):
		task = ts.pop()
		eft_min = -1
		est_min = 0
		for node in pool.avail():
			if task == "entry":
				est = 0
			else:
				est = max([aft[t]+pool.comm_cost(workflow.data_size_set(t, task), loc[t], node) for t in workflow.pred(task)])
			if est < pool.avail_time(node):
				est = pool.avail_time(node)
			eft = est + pool.comp_cost(workflow.get_cost(task), node)
			if eft_min == -1 or eft_min > eft:
				est_min, eft_min = est, eft
				loc[task] = node
		aft[task] = eft_min
		pool.add_task(task, loc[task], est, eft)
	return aft["exit"]

def stat(result):
	s = {}
	for _, t, _ in result:
		if t not in s:
			s[t] = 1
		else:
			s[t] += 1

	# a = []
	# for n in result:
	# 	_, _, es = n
	# 	for e in es:
	# 		a.append((e, n[0]))

	# a = sorted(a, key=lambda x: x[0])
	# for ee, n in a:
	# 	t, ss, e = ee
	# 	print "%s\t%.2f\t%.2f\t%s" % (t,ss,e,n)

	print "Num of Instances: %d" % len(result)
	for k,v in s.iteritems():
		print "%s: %d" % (k, v)

if __name__ == '__main__':
	from sys import argv
	from workflow import Workflow
	from pool import AWS, GridFromAWS

	wf = Workflow(argv[1])
	# cloud = GridFromAWS(int(argv[2]))
	cloud = AWS("aws.info")

	print "Makespan: %.0fs\tCost: $%.2f" % (schedule(wf, cloud), cloud.charge())
	# print list(cloud.results())

	from  plot import trans, show
	result = list(cloud.results())

	# stat(result)	

	# show(*trans(result))
