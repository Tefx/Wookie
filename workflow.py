import networkx as nx

class Workflow(object):
	def __init__(self, path, base_ECU=8):
		from bs4 import BeautifulSoup
		self._soup = BeautifulSoup(open(path)).adag
		self.graph = nx.DiGraph()
		self.base_ECU = base_ECU
		self.get_exectime()
		self.get_structure()
		self.get_dataflow()

	def tasks(self):
		return self.graph.nodes()

	def get_cost(self, task):
		return self.graph.node[task]["exectime"]

	def get_data_size(self, n1, n2):
		if self.graph.has_edge(n1, n2):
			return self.graph[n1][n2]["size"]
		else:
			return 0

	def get_exectime(self):
		for job in self._soup.find_all("job"):
			jid = job["id"]
			self.graph.add_node(jid, {"exectime":float(job["runtime"]) * self.base_ECU})
		self.graph.add_node("entry", {"exectime":1})
		self.graph.add_node("exit", {"exectime":0})

	def get_structure(self):
		for child in self._soup.find_all("child"):
			cid = child["ref"]
			for parent in child.find_all("parent"):
				pid = parent["ref"]
				self.graph.add_edge(pid, cid, {"size":0, "files":[]})
		for node in self.graph:
			if node not in ("entry", "exit"):
				if self.graph.successors(node) == []:
					self.graph.add_edge(node, "exit", {"size":0, "files":[]})
				if self.graph.predecessors(node) == []:
					self.graph.add_edge("entry", node, {"size":0, "files":[]})

	def get_dataflow(self):
		fs = {}
		for job in self._soup.find_all("job"):
			for use in job.find_all("uses"):
				fid = use["file"]
				if fid not in fs:
					fs[fid] = {
						use["link"]	:	job["id"],
						"size"		:	float(use["size"])	
					}
				else:
					fs[fid][use["link"]] = job["id"]
		for f, v in fs.iteritems():
			if "input" not in v:
				a1, a2, size = v["output"], "exit", v["size"]
			elif "output" not in v:
				a1, a2, size = "entry", v["input"], v["size"]
			else:
				a1, a2, size = v["output"], v["input"], v["size"]
			if not self.graph.has_edge(a1, a2):
				self.graph.add_edge(a1, a2, {"size":0, "files":[]})
			self.graph[a1][a2]["files"].append((f, size))
			self.graph[a1][a2]["size"] += size

	def data_size_set(self, a1, a2):
		return [x[1] for x in self.graph[a1][a2]["files"]]

	def secc(self, task):
		return self.graph.successors(task)

	def pred(self, task):
		return self.graph.predecessors(task)

	def topological_sort(self):
		return nx.topological_sort(self.graph)

	def dot(self, path):
		nx.write_dot(self.graph, path)

	def __len__(self):
		return len(self.graph)

if __name__ == '__main__':
	from sys import argv
	wf = Workflow(argv[1])
