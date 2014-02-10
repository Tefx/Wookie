if __name__ == '__main__':
	from sys import argv
	import cPickle as pickle 

	with open(argv[1]) as f:
		results = pickle.load(f)
		count = 0
		for makespan, cost, result in results:
			print "[%d]: Makespan: %.0fs\tCost: $%.2f" % (count, makespan, cost)
			count += 1
