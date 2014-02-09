def get_soup(filename):
	from bs4 import BeautifulSoup as BS
	return BS(open(filename)).adag

def get_runtime(soup, base_ECU=8):
	d = {"0":0, "1":0}
	for job in soup.find_all("job"):
		d[job["id"]] = float(job["runtime"]) * base_ECU
	return d

def get_structure(soup):
	d = {"0":[]}
	for child in soup.find_all("child"):
		for parent in child.find_all("parent"):
			pid = parent["ref"]
			if pid not in d:
				d["0"].append(pid)
				d[pid] = ["1", child["ref"]]
			else:
				d[pid].append(child["ref"])
	return d

def get_file(soup):
	d = {}
	for job in soup.find_all("job"):
		for use in job.find_all("uses"):
			fid = use["file"]
			if fid not in d:
				d[fid] = {use["link"]:job["id"], "size":float(use["size"])}
			else:
				d[fid][use["link"]] = job["id"]
	return d

def get_commcost(soup, commspeed=12*1024*1024):
	d = {}
	fs = get_file(soup)
	for f,v in fs.iteritems():
		if "input" not in v:
			inf, ouf, size = "1", v["output"], v["size"]
		elif "output" not in v:
			inf, ouf, size = v["input"], "0", v["size"]
		else:
			inf, ouf, size = v["input"], v["output"], v["size"]
		if ouf not in d:
			d[ouf] = {inf:size/commspeed}
		elif inf not in d[ouf]:
			d[ouf][inf] = size/commspeed
		else:
			d[ouf][inf] += size/commspeed
	return d

if __name__ == '__main__':
	from sys import argv
	soup = get_soup(argv[1])
	# print get_runtime(soup)
	print get_structure(soup)
	# print get_file(soup)
	# print get_commcost(soup)
