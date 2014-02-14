import sh
import time

tests_Montage = [
	"Montage_25.xml",
	"Montage_50.xml",
	"Montage_100.xml",
	"Montage_1000.xml",
]

tests_Epigenomics = [
	"Epigenomics_24.xml",
	"Epigenomics_46.xml",
	"Epigenomics_100.xml",
	"Epigenomics_997_fixed.xml",
]

tests_CyberShake = [
	"CyberShake_30.xml",
	"CyberShake_50.xml",
	"CyberShake_100.xml",
	"CyberShake_1000.xml",
]

tests_Sipht = [
	"Sipht_30.xml",
	"Sipht_60.xml",
	"Sipht_100.xml",
	"Sipht_1000.xml",
]

tests_Inspiral = [
	"Inspiral_30.xml",
	"Inspiral_50.xml",
	"Inspiral_100.xml",
	"Inspiral_1000.xml",
]


tests = [
	("Montage", tests_Montage),
	("Epigenomics", tests_Epigenomics),
	("CyberShake", tests_CyberShake),
	("Sipht", tests_Sipht),
	("Inspiral", tests_Inspiral),
]

def test_list(ts):
	from sys import argv
	n, s = ts
	for t in s:
		dax = "dax/%s" % t
		start = time.time()
		res = sh.python(argv[1], dax)
		# print res.split()
		_, makespan, _, cost = res.split()
		makespan = float(makespan[:-1])
		cost = float(cost[1:])
		print t, makespan, cost
		# cost_heft = time.time() - start
		# print "%s\t%.2fs" % (dax, cost_heft)

if __name__ == '__main__':
	map(test_list, tests)
