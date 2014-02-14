import matplotlib.pyplot as plt
import matplotlib as mpl 
import cPickle as pickle
import os
import math
from matplotlib.backends.backend_pdf import PdfPages


def plot_name(ax, filename, heft_ar="archive/heft.ar"):
	name = os.path.split(filename)[1][:-2] + "xml"
	emo_results = pickle.load(open(filename))
	emo_mc = [x[:2] for x in emo_results]

	heft_makespan, heft_cost = 0, 0
	with open(heft_ar) as f:
		for line in f:
			f_name, makespan, cost = line.split()
			if f_name == name:
				heft_makespan = float(makespan)
				heft_cost = float(cost)

	ax.grid(True)
	ax.set_title(name)
	plt.xlabel('Makespan(s)')
	plt.ylabel('Cost($)')
	plt.subplots_adjust(hspace=0.3)

	for x, y in emo_mc:
		ax.plot(x, y, "go")
	ax.plot(heft_makespan, heft_cost, "rx")



def plot_all(fs, heft_ar, pdf=False):
	if pdf:
		pp = PdfPages('%s.pdf' % pdf)

	plt.figure(figsize=(11.69,8.27))

	num = len(fs)
	size = int(math.ceil(math.sqrt(num)))
	base = size*100+size*10

	for i in range(len(fs)):
		ax = plt.subplot(base+i+1)
		plot_name(ax, fs[i], heft_ar)

	if not pdf:
		plt.show()
	else:
		pp.savefig()
		pp.close()

if __name__ == '__main__':
	from sys import argv
	from glob import glob

	fs = []
	for arg in argv[1:]:
		fs += glob(arg)

	base = os.path.split(fs[0])[0]
	heft_ar = "%s/heft2.ar" % base
	pdf_base = base.replace("archive", "pdf")

	if heft_ar in fs:
		fs.remove(heft_ar)

	if not os.path.exists(pdf_base):
		os.mkdir(pdf_base)

	pdf = os.path.split(fs[0])[1].split("_")[0]
	pdf = "%s/%s" % (pdf_base, pdf)
	plot_all(fs, heft_ar, pdf=pdf)
