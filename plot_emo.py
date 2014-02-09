from show_result import trans, show

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
