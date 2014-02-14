import cPickle as pickle
import itertools
import os
import math
from bs4 import BeautifulSoup as BS
from urllib import urlopen
from urllib import urlopen
import json
			
class Pool(object):

	def average_cost(self, task_time):
		pass

	def comm_cost(self, data_size_set, n1, n2):
		pass

	def avail(self, node):
		pass

	def add_task(self, task_name, node, start, end):
		pass

	def comp_cost(self, task_time, node):
		pass

url_price_ec2_linux = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/ec2/linux-od.js"
url_description_ec2_linux = "http://aws.amazon.com/ec2/instance-types/"

class AWS(Pool):
	def __init__(self, filename=None):
		if not filename or not self.read_file(filename):
			self.get_info()
			if filename:
				self.write_file(filename)
		self.node_id_count = len(self.info) + 1
		# self.avail_nodes = set([x for x in range(self.node_id_count-1)])
		self.avail_nodes = range(self.node_id_count-1)
		self.nodes = {n:{"type":t,"event":[],"avail":0} for n,t in zip(self.avail_nodes, self.info.keys())}

	def read_file(self, filename):
		if os.path.exists(filename):
			self.info = pickle.load(open(filename, "r"))
			return True
		else:
			return False

	def write_file(self, filename):
		pickle.dump(self.info, open(filename, "w"))

	def add_task(self, tn, n, s, e):
		self.nodes[n]["event"].append((tn, s, e))
		if self.nodes[n]["avail"] == 0:
			# self.avail_nodes.add(self.node_id_count)
			self.avail_nodes.append(self.node_id_count)
			self.nodes[self.node_id_count] = {
				"event"	:	[],
				"type"	:	self.nodes[n]["type"],
				"avail"	:	0
			}
			self.node_id_count += 1
		if e > self.nodes[n]["avail"]:
			self.nodes[n]["avail"] = e

	def avail_time(self, n):
		return self.nodes[n]["avail"]

	def comp_cost(self, tt, n):
		return tt/self.info[self.nodes[n]["type"]]["ecu"]

	def average_cost(self, task_time):
		return sum([task_time/v["ecu"] for v in self.info.itervalues()])/len(self.info)

	def average_comm_cost(self, data_size):
		return sum([
			data_size/min([v1["net"],v2["net"]]) for v1, v2 in itertools.product(self.info.itervalues(), self.info.itervalues())
			])
	def comm_cost(self, dss, n1, n2):
		# return 0
		if n1 == n2:
			return 0
		n1_type = self.nodes[n1]["type"]
		n2_type = self.nodes[n2]["type"]
		speed = min([self.info[n1_type]["net"], self.info[n2_type]["net"]])
		return sum([ds/speed for ds in dss])

	def avail(self):
		return self.avail_nodes

	def results(self):
		for n in self.avail_nodes:
			if self.nodes[n]["event"] != []:
				yield (n, self.nodes[n]["type"], self.nodes[n]["event"])

	def charge(self):
		total = 0
		for n in self.avail_nodes:
			if self.nodes[n]["event"] != []:
				start = -1
				end = 0
				for t, s, e in self.nodes[n]["event"]:
					if start == -1 or start > s:
						start = s
					if e > end:
						end = e
				# print self.nodes[n]["type"], start, end
				h = math.ceil((end - start)/3600.0)
				# if h == 0:
				# 	h = 1
				total += h * self.info[self.nodes[n]["type"]]["price"]
		return total


	def netspeed(self, description):
		if description == "Low":
			return 300.0*1024*1024/8
		elif description == "Moderate":
			return 650.0*1024*1024/8
		elif description == "High":
			return 1000.0*1024*1024/8

	def get_info(self, region=["apac-sin"], family=["General purpose"]):

		def get_instances_price():
			json_str = urlopen(url_price_ec2_linux).read()[9:-1].strip()
			d = json.loads(json_str)["config"]["regions"]
			price = {}
			for region in d:
				r = {}
				for ins_type in region["instanceTypes"]:
					for t in ins_type["sizes"]:
						name = t["size"]
						if name == "t1.micro":
							t["ECU"] = 2
						r[name] = {
							"ecu"		:	float(t["ECU"]),
							"price"		:	float(t["valueColumns"][0]["prices"]["USD"])
						}
				price[region["region"]] = r
			return price

		def get_table():
			soup = BS(urlopen(url_description_ec2_linux))
			for t in soup.html.body.find_all("table"):
				if "aws-table" in t.parent["class"]:
					yield t.tbody

		def parse_table_0(table):
			d = {}
			for line in table.find_all("tr")[1:]:
				items = [item.string for item in line.find_all("td")]
				if items[1] == "t1.micro":
					items[4] = 2
				d[items[1]] = {
					"family"	:	items[0],
					"ecu"		:	float(items[4]),
					"memory"	:	float(items[5]),
					"storage"	:	items[6],
					"ebsopt"	:	items[7],
					"net"		:	items[8]
				}
			return d

		def get_instances_description():
			table = get_table().next()
			return parse_table_0(table)

		p = get_instances_price()
		d = get_instances_description()
		self.info = {}
		for r in p:
			if r not in region:
				continue
			for i in p[r]:
				if d[i]["family"] in family:
					self.info["%s#%s" % (r, i)] = {
						"price"		:	p[r][i]["price"],
						"ecu"		:	d[i]["ecu"],
						"net"		:	self.netspeed(d[i]["net"])
					}
		# self.info2 = {}
		# self.info2["apac-sin#m3.2xlarge"] = self.info["apac-sin#m3.2xlarge"]
		# self.info = self.info2

class GridFromAWS(AWS):
	def __init__(self, num_of_instances):
		self.get_info()
		self.nodes = {}
		count = 0
		for t in self.info:
			for i in range(num_of_instances):
				self.nodes[count] = {"type":t,"event":[],"avail":0}
				count += 1
		self.avail_nodes = set(self.nodes.keys())

	def add_task(self, tn, n, s, e):
		self.nodes[n]["event"].append((tn, s, e))
		if e > self.nodes[n]["avail"]:
			self.nodes[n]["avail"] = e

if __name__ == '__main__':
	cloud = AWS()
	cloud.add_task("u",1,0,4)
	cloud.add_task("v",1,5,7)
	cloud.add_task("w",3,0,4)
	print list(cloud.results())
