import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np 
import math

def trans(results):
	results = list(results)
	lables = ["%s_%s" % (x[1], x[0]) for x in results]
	es = [
		[(e[1], e[2]) for e in node[2]] for node in results
	]
	during = [
		(min([e[0] for e in n]), max([e[1] for e in n])) for n in es
	]
	hours = [
		(start, start+math.ceil((end-start+0.00001)/3600.0)*3600) for start, end in during
	]
	x_len = max([max([e[1] for e in n]) for n in es])
	h_len = max([h[1] for h in hours])
	if x_len < h_len:
		x_len = h_len
	z = np.zeros((len(es), x_len))
	for i in range(len(es)):
		for x in range(*map(int, hours[i])):
			z[i, x] = 2
		for s,e in es[i]:
			for x in range(int(s), int(e)):
				z[i, x] = 5
	return z, lables

def show(z, lables):
	flg, ax = plt.subplots()
	ax.set_yticks(np.arange(z.shape[0]) + 0.5, minor=False)
	ax.invert_yaxis()
	graph = ax.pcolormesh(z, cmap=mpl.cm.Greens)
	ax.grid(False)

	ax.set_yticklabels(lables, minor=False)
	plt.show()

def show2():
	lables = ["%s_%s" % (x[1], x[0]) for x in results]


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
	import cPickle as pickle 

	with open(argv[1]) as f:
		results = pickle.load(f)

	makespan, cost, result = results[int(argv[2])]
	print "Makespan: %.0fs\tCost: $%.2f" % (makespan, cost)
	stat(result)
	# print result
	show(*trans(result))
