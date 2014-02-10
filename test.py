import sh
import time


tests = [
	"Inspiral_30.xml",
	"Inspiral_50.xml",
	"Inspiral_100.xml",
	"Inspiral_1000.xml",
]


for t in tests:
	dax = "dax/%s" % t
	start = time.time()
	sh.time("python", "emo4.py", dax)
	print "%s\t%.2fs" % (dax, time.time() - start)