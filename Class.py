
class Experiment(object):
	"""
	designed to initialise an expermiment processing upon a given directory.
	also requires a printinglabel incase of visual feedback

	"""

	def __init__(self, dir, printlabel, Settings="empty"):
		from functions import fn_check_dir
		from GUI_mainframe import update_GUI
		update_GUI("Reading in experiment.",printlabel)

		self.dir = dir
		if Settings == "empty":
			from functions import fn_settings
			Settings = fn_settings()
		self.Settings = Settings
		self.printlabel = printlabel

		if fn_check_dir(dir[:dir.find('pdata')], "pulseprogram"):
			if "seldigpzs2d" in open(dir[:dir.find('pdata')] + r"\pulseprogram", "r").readlines()[0]:
				self.pp = "seldigpzs2d"
				self.init_seldigpzs2d(self.dir, self.printlabel)
			elif "dipsigpphzsbs" in open(dir[:dir.find('pdata')] + r"\pulseprogram", "r").readlines()[0]:
				self.pp = "dipsigpphzsbs"
				self.init_dipsigpphzsbs(self.dir, self.printlabel)
		else:
			update_GUI("error; no correct pulseprogram found", printlabel)

	def init_seldigpzs2d(self, dir, printlabel):
		import nmrglue as ng
		import numpy as np
		from functions import fn_check_dir
		from GUI_mainframe import update_GUI

		self.dic, self.data = ng.bruker.read_pdata(dir)

		# read in the alternate data if possible - compenation for the NMRGlue chunk error
		# can be deleted once we fixed nmrglue!!!

		if self.dic["procs"]["XDIM"] != self.dic["procs"]["FTSIZE"]:
			self.data_file = ""
			if fn_check_dir(dir, "DATABASE.txt"):
				self.data_file = open(dir + r"\DATABASE.txt", 'r').readlines()
			elif fn_check_dir(dir, "SAMPLES.txt"):
				self.data_file = open(dir + r"\SAMPLES.txt", 'r').readlines()
			if self.data_file != "":
				self.data = []
				for line in self.data_file:
					if ("row" in line):
						self.data.append([])
					else:
						if "#" not in line:
							self.data[len(self.data) - 1].append(float(line.replace(r"\n", "")))
			else:
				update_GUI("No extra data file was found...", printlabel)
				quit()

		# reform the data for oversaving effect
		from copy import deepcopy
		test_data = deepcopy(self.data)
		self.data = []
		for x in range(len(test_data)):
			if (test_data[x][0] != 0.0):
				self.data.append(test_data[x])

		# collect the parameters
		from functions import fn_vclist, fn_fqlist, fn_parameters, fn_read_title
		self.dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
		self.dic3 = open(dir[:dir.find('pdata')] + r'\acqu2s', 'r').read()

		self.B0_hz, self.SW_ppm, self.SW_hz, self.duplet_ppm, self.chunk_num, self.offset = fn_parameters(self.dic, self.dic2, self.dic3, self.pp)
		self.SW_ppm = 0.5*self.SW_ppm
		self.SO1_ppm = 0.5*self.SW_ppm - self.offset

		# collect the lists
		self.vclist = fn_vclist(dir)
		self.fqlist, self.fqlist_ppm = fn_fqlist(dir, self.B0_hz)
		self.mtlist = np.array(self.vclist)*115.112 * 25 * 10 ** (-6)

		# colect the title
		self.sample_name, self.extra_info, self.order = fn_read_title(dir)

		# print out the title
		update_GUI("Working on %s sample." % self.sample_name, self.printlabel)

		# all data was read in now - end of initialisation of the sample
		# starting the chunkification if present


		import numpy as np
		from functions import fn_unique
		from GUI_mainframe import update_GUI

		# find the unique fqs
		self.fqlist_u = fn_unique(self.fqlist)

		# chunk up the data per fq and remove the minus signals (reduce data amount for calculations)
		self.chunks = []
		update_GUI("Calculating peaks and integrals for each chunk.", self.printlabel)
		for x in range(self.chunk_num):
			chunk = self.data[x * len(self.vclist):((x + 1) * len(self.vclist))]
			max = np.max(chunk)
			row = chunk[0]
			keep = int(len(row) / 2)  # remove negative half
			new_chunk, new_data = [], []
			for row in chunk:
				new_chunk.append(row[:keep] / max)

			# create the title for the chunk
			if len(self.order) != 0:
				title = self.order[x]
			else:
				title = "%i-%s" % (x, self.sample_name)

			#initialise chunk and perform the functions that are needed
			chunk_temp = Chunk(new_chunk, title, self.fqlist[x], self.SW_ppm, self.duplet_ppm, self.mtlist, self.SO1_ppm, self.pp, self.printlabel, self.Settings)
			self.chunks.append(chunk_temp)
		#return self # list of all chunk objects

		if self.Settings["plot_exp"]:
			self.fn_plot()

	def init_dipsigpphzsbs(self, dir, printlabel):
		import nmrglue as ng
		import numpy as np
		from functions import fn_check_dir, fn_p3d_reform, fn_p3d_diagonal, fn_noise_filter, index_from_ppm, ppm_from_index
		from GUI_mainframe import update_GUI

		self.dic, self.data = ng.bruker.read_pdata(dir)

		#oversave effect and reorder the data
		self.data = fn_p3d_reform(self.data)

		# collect the parameters
		from functions import fn_vclist, fn_parameters, fn_read_title
		self.dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
		self.dic3 = open(dir[:dir.find('pdata')] + r'\acqu2s', 'r').read()
		self.B0_hz, self.SW_ppm, self.SW2_ppm, self.SW_hz, self.duplet_ppm, self.chunk_num, self.offset = fn_parameters(self.dic, self.dic2, self.dic3, self.pp)
		# extra parameter
		self.SO1_ppm = float(self.dic2[self.dic2.find(r'$O1=') + 5:][:self.dic2[self.dic2.find(r'$O1=')+5:].find("\n")])/self.B0_hz - self.offset

		# collect the lists
		self.vclist = fn_vclist(dir)
		self.mtlist = np.array(self.vclist)*115.112 * 25 * 10 ** (-6)

		# colect the title
		self.sample_name, self.extra_info, self.order = fn_read_title(dir)

		# find the diagonal
		self.diag = fn_p3d_diagonal(self.data[0], self.SW_ppm, self.SW2_ppm, self.SO1_ppm)
		from detect_peaks import detect_peaks
		self.ind_diag = detect_peaks(self.diag, show=self.Settings["plot_diagonal"], mph=self.Settings["gp_threshold"])
		self.ind_diag, limit = fn_noise_filter(self.ind_diag, self.diag, 5)

		# find duplets on the diagonal; must be averaged index & recombine
		duplet_ind = int(self.duplet_ppm/self.SW2_ppm*len(self.data[0]))
		duplet_ind_new, remove = [], []
		self.ind_diag.append(9)
		for z in range(len(self.ind_diag)-1):
			x = self.ind_diag[z]
			y = self.ind_diag[z+1]
			if (abs(self.diag[x]-self.diag[y])/np.max([self.diag[x], self.diag[y]]) < 0.3) and ((y-x) < duplet_ind):
				duplet_ind_new.append(int((x+y)/2))
				remove.append(z+1)
			else:
				duplet_ind_new.append(x)

		# remove the H2O peak
		len2 = len(self.data[0])
		h2p_ind = index_from_ppm(4.79, self.SO1_ppm, self.SW2_ppm, len2)
		for z in range(len(duplet_ind_new)):
			x = duplet_ind_new[z]
			if (abs(h2p_ind - x) < 10/1024*len2):
				remove.append(z)
		unique = []
		[unique.append(item) for item in remove if item not in unique]
		remove = sorted(unique, reverse=True)
		for x in remove:
			duplet_ind_new.pop(x)
		self.ind_diag = duplet_ind_new
		self.chunk_num = len(self.ind_diag)

		# get the new data 2d planes and initialise the chunks
		self.chunks = []
		update_GUI("Calculating peaks and integrals for each chunk.", self.printlabel)
		for x in range(self.chunk_num):
			index = self.ind_diag[x]
			chunk =  []
			for y in self.data:
				chunk.append(y[index])
			max = np.max(chunk)
			new_chunk, new_data = [], []
			for row in chunk:
				new_chunk.append(row / max)

			# create the title for the chunk
			temp_ppm = (len2 - self.ind_diag[x]) / len2 * self.SW2_ppm + self.SO1_ppm - 0.5 * self.SW2_ppm
			title = "%.2fppm - %s" % ((temp_ppm), self.sample_name)

			# initialise chunk and perform the functions that are needed
			chunk_temp = Chunk(new_chunk, title, temp_ppm, self.SW_ppm, self.duplet_ppm, self.mtlist, self.SO1_ppm, self.pp, self.printlabel, self.Settings)
			self.chunks.append(chunk_temp)

	def fn_plot(self):
		import matplotlib.pyplot as plt
		from functions import fn_calc_plots
		chunks = self.chunks

		num = fn_calc_plots(chunks)
		for z in range(len(chunks)):
			x = chunks[z]  # x is a chunk object
			ax = plt.subplot(num + z)
			ax.set_title(x.sample_name)
			ax.set_ylabel("Intensity (rel.)")
			ax.set_xlabel("Mixing Time (s)")
			for y in (x.content.content):  # y is a curve object
				plt.plot(self.mtlist, y.data, label=(x.sample_name + " " + str(y.ppm)))
		plt.show()
		return plt

	def fn_compare(self, data):
		# get the chunklist
		temp_list = self.Settings["gp_chunks_list"]
		if type(temp_list) == list:
			if len(temp_list) == 0:
				temp_list2 = range(len(self.chunks))
			else:
				temp_list2 = temp_list
		elif type(temp_list) == str:
			if "range" in temp_list:
				temp_list2 = range(int(temp_list[temp_list.find(",")-1]),int(temp_list[temp_list.find(",")+2]))
			else:
				temp_list = temp_list.split(",")
				temp_list2 = []
				for x in temp_list:
					temp_list2.append(int(x))
		else:
			self.status = False
		comparison = []
		self.Settings["gp_chunks_list"] = temp_list2
		for x in temp_list2:
			comp = self.chunks[x].fn_compare(data)
			comparison.append([x,comp])
		self.result = comparison
		return comparison



########################################################################################################################
########################################################################################################################

#chunk class
class Chunk(object):
	def __init__(self, chunk_data, title, chunk_fq, SW_ppm, duplet_ppm, mtlist, SO1_ppm, pp, printlabel, Settings):
		self.Settings = Settings

		self.data = chunk_data
		self.sample_name = title
		self.chunk_fq = chunk_fq
		self.Settings["SW_ppm"] = SW_ppm
		self.Settings["duplet_ppm"] = duplet_ppm
		self.mtlist = mtlist
		self.Settings["SO1_ppm"] = SO1_ppm
		self.pp = pp
		self.printlabel = printlabel


		#import required functions
		import numpy as np
		#import peakutils as pk
		from detect_peaks import detect_peaks
		from functions import fn_max_curve, fn_noise_filter, fn_integrals, fn_integrate

		#find the max curve
		self.max_curve = fn_max_curve(self.data)

		#set general settigns
		self.Settings["res"] = len(self.max_curve)

		#find the integral limits
		self.integrals, self.indices, Settings["noise"] = fn_integrals(self.max_curve, Settings["am_norm"], Settings["gp_splitter"])

		#calculate the integral values
		temp_values, self.integrals, self.indices = fn_integrate(self.data, self.integrals, self.indices, self.Settings["SW_ppm"], self.Settings["SO1_ppm"], self.pp)
		#set the content using the Values class
		self.content = Values(temp_values, self.integrals, self.max_curve, self.sample_name, self.mtlist, self.chunk_fq, self.printlabel, self.Settings)

		if self.Settings["plot_integration"]:
			self.fn_plot_int()

	def fn_plot(self, second = [], text="",save=''):
		import numpy as np

		chunk_list = [self]
		if type(second) == Chunk:
			chunk_list += [second]
		elif type(second) == list:
			chunk_list += second

		import matplotlib.pyplot as plt
		plt.figure()
		ax = plt.subplot()
		for x in range(len(chunk_list)):
			for y in range(len(chunk_list[x].content.content)):
				if y == 0:
					plt.plot(self.mtlist,(np.array(chunk_list[x].content.content[y].data)+x*0.001), ["r-", "g-", "b-", "y-"][x], label=chunk_list[x].sample_name)
				else:
					plt.plot(self.mtlist,(np.array(chunk_list[x].content.content[y].data)+x*0.001), ["r-", "g-", "b-", "y-"][x])
		plt.xlim(0.007,0.113)
		if text != "":
			plt.text(0.1,0.8,text, fontsize=15)
		ax.set_ylabel("Intensity (rel.)")
		ax.set_xlabel("Mixing Time (s)")
		plt.legend()
		if save != "":
			plt.savefig(save)
		else:
			plt.show()

	def fn_plot_int(self):
		# plots the integration curve
		import matplotlib.pyplot as plt
		plt.figure()
		ax = plt.subplot()
		ax.set_title(self.sample_name)
		temp = []
		temp_max_curve = []
		for x in range(len(self.max_curve)-1):
			temp.append(0)
			temp.append(0)
			temp_max_curve.append(self.max_curve[x])
			temp_max_curve.append(0.5*self.max_curve[x]+0.5* self.max_curve[x+1])
		for x in self.content.content:
			temp_limit = x.index
			for x in range(2*temp_limit[0], 2*temp_limit[1]+1):
				if temp[x]==1:
					temp[x] = 0.5
				else:
					temp[x] =1
		plt.plot(temp_max_curve, label="Projection curve")
		plt.plot(temp, label="Integral Filter")

		ax.set_ylabel("Intensity (rel.)")
		ax.set_xlabel("Double Data #")
		plt.legend()
		plt.show()

	def fn_compare(self, database, sort=True):
		comparison = []
		for chunk in database.content:
			new = self.content.fn_compare(chunk.content)
			comparison.append([new,chunk])
		if sort:
			comparison.sort(key=lambda x: x[0],reverse=True)

		if self.Settings["plot_chunk"]:
			temp = []
			for x in comparison[:3]:
				temp.append(x[1])
			self.fn_plot(temp)

		return comparison


########################################################################################################################
########################################################################################################################

class Values(object): # prob gonna reorder the chunk class to a more definit way of handling it
	def __init__(self, values, peak_ind, max_curve, sample_name, mtlist, chunk_fq, printlabel, Settings):
		#set all parameters given for backup
		self.data = values 		#self.data now is a list of lists
		self.peak_ind = peak_ind
		self.max_curve = max_curve
		self.sample_name = sample_name
		self.mtlist = mtlist
		self.chunk_fq = chunk_fq
		self.printlabel = printlabel
		self.Settings = Settings


		#import GUI printer
		from GUI_mainframe import update_GUI
		import numpy as np
		update_GUI(format("Fitting curves on chunk of %s..." %self.sample_name), self.printlabel)

		self.content = []		#self.content will become a list of curves
		# split up the values into different curves
		for x in range(len(self.data)):
			temp_curve = Curve(self.data[x], self.peak_ind[x], self.max_curve[self.peak_ind[x][0]:self.peak_ind[x][1]], self.mtlist, self.Settings)
			if temp_curve.ok:
				self.content.append(temp_curve)

		# sort the curves (shouldnt be required)
		self.content.sort(key=lambda x: x.index[0])

		# duplet and triplet filtering
		if self.Settings["gp_duplet_filtering"]:
			# triplet filtering
			self.content = self.fn_triplet_cluster()
			# quadruplet filtering
			self.content = self.fn_quadruplet()
			# duplet filtering
			self.content = self.fn_duplet()
			# baseline filter
			#self.content = self.fn_baseline()

		self.fn_normalise()
		self.fn_curve_filter()
		if self.Settings["plot_values"]:
			self.fn_plot()

	def fn_normalise(self):
		import numpy as np
		#get max value
		temp_max = 0
		for x in self.content:
			if np.max(x.data) > temp_max:
				temp_max = np.max(x.data)
		#devide by max
		for x in self.content:
			x.data = x.data/temp_max


	# filtering of individual curves
	def fn_curve_filter(self):
		import numpy as np
		remove = []
		for y in range(len(self.content)):
			x = self.content[y]
			# minimum filter
			if np.max(x.data) < 0.005:
				remove.append(y)
			# ppm filter (left)
			elif x.ppm > (self.chunk_fq + self.Settings["duplet_ppm"]):
				remove.append(y)
			# h2o peak filter
			elif abs(x.ppm - 4.79) < 0.01:
				remove.append(y)
			# high ppm low intensity filter
			elif x.ppm > 4.5 and np.max(x.data) < 0.3:
				remove.append(y)

		unique = []
		[unique.append(item) for item in remove if item not in unique]
		remove = sorted(unique, reverse=True)
		for x in remove:
			self.content.pop(x)

	def fn_duplet(self):
		import numpy as np
		temp = []
		if (len(self.content) > 1):
			for z in range(len(self.content) - 1):
				x = self.content[z]
				y = self.content[z + 1]
				if not x.triplet and not y.triplet and not x.duplet and not x.quadruplet and not y.quadruplet:
					temp_duplet = x.fn_duplet(y, self.Settings["duplet_ppm"])
					if temp_duplet or (x.alpha and y.alpha and (abs(x.ppm - y.ppm) < 0.15)):
						x = Curve(np.array(x.data) + np.array(y.data), [x.index[0], y.index[1]], x.max_curve + y.max_curve, self.mtlist, self.Settings, ppm=(x.ppm + y.ppm)/2, duplet_ppm = abs((x.ppm - y.ppm)))
						x.duplet = True
						y.duplet = True
					temp.append(x)
				else:
					if not x.duplet:
						temp.append(x)  # keep the x curve in case of triplet

			# ad the last one if not a duplet
			if not y.duplet:
				temp.append(y)
			return temp
		else: return self.content

	def fn_quadruplet(self):
		import numpy as np
		temp = []
		for z in range(len(self.content) - 3):
			x = self.content[z]
			y = self.content[z + 1]
			u = self.content[z + 2]
			v = self.content[z + 3]
			triplet = x.triplet or y.triplet or u.triplet or v.triplet
			duplets = x.fn_duplet(y, self.Settings["duplet_ppm"]) and u.fn_duplet(v, self.Settings["duplet_ppm"]) and y.fn_duplet(u, self.Settings["duplet_ppm"]*1.2)
			eq_dist = (abs(u.ppm - y.ppm) < 0.1) and (abs(abs(v.ppm - u.ppm) - abs(x.ppm - y.ppm)) < 0.0060)
			if not triplet and not x.quadruplet:
				if duplets and eq_dist:
					x.quadruplet = True
					x = (Curve(np.array(x.data) + np.array(y.data) + np.array(u.data) + np.array(v.data), [x.index[0], v.index[1]],  x.max_curve + y.max_curve + u.max_curve + v.max_curve, self.mtlist, self.Settings, ppm=(y.ppm + u.ppm)/2))
					x.quadruplet = True
					y.quadruplet = True
					u.quadruplet = True
					v.quadruplet = True
				temp.append(x)
			else:
				if not x.quadruplet:
					temp.append(x)
		if len(self.content) < 4:
			temp = self.content
		else:
			if not y.quadruplet:
				temp.append(y)
			if not u.quadruplet:
				temp.append(u)
			if not v.quadruplet:
				temp.append(v)
		return temp

	def fn_triplet_cluster(self):
		import numpy as np
		found = True
		cluster, triplets, temp = [], [], []
		for z in range(1, len(self.content)-1):
			cluster.append(self.content[z-1].fn_triplet(self.content[z], self.content[z+1], self.Settings["duplet_ppm"]))
		if not cluster: found = False
		while found and max(cluster):
			index = (np.where(cluster == (np.array(cluster)).max()))[0][0]
			if cluster[index]:
				for x in [-2,-1,0,1,2]:
					if 0 <= (index + x) <= (len(cluster)-1):
						cluster[index + x] = 0
				x = self.content[index]
				y = self.content[index + 1]
				u = self.content[index + 2]
				x.triplet = True
				y.triplet = True
				u.triplet = True
				x = Curve(np.array(x.data) + np.array(y.data) + np.array(u.data), [x.index[0], u.index[1]], x.max_curve + y.max_curve + u.max_curve, self.mtlist, self.Settings)
				x.triplet = True
				temp.append(x)
			else:
				found = False
		# add all peaks not part of a triplet
		for x in self.content:
			if not x.triplet:
				temp.append(x)
		temp.sort(key=lambda x: x.ppm, reverse=True)
		return temp

	def fn_baseline(self):
		import numpy as np
		temp = []
		for z in range(len(self.content) - 1):
			x = self.content[z]
			y = self.content[z + 1]
			if not x.baseline_corr:
				if abs(x.index[1] - y.index[0]) < 2 and x.max_curve[len(x.max_curve)-1] > self.Settings["noise"]*2 and y.max_curve[0] > self.Settings["noise"]*2:
					x.baseline_corr = True
					y.baseline_corr = True
					x = Curve(np.array(x.data) + np.array(y.data), [x.index[0], y.index[1]], x.max_curve + y.max_curve,self.mtlist, self.Settings, ppm=(x.ppm + y.ppm) / 2, duplet_ppm=abs((x.ppm - y.ppm)))
					x.baseline_corr = True
				temp.append(x)
		if not y.baseline_corr:
			temp.append(y)
		return temp


	def fn_plot(self):
		import matplotlib.pyplot as plt
		plt.figure()
		ax = plt.subplot()
		ax.set_title(self.sample_name)
		for x in range(len(self.content)):
			plot_label = str(self.content[x].ppm)[:5] + " ppm"
			plt.plot(self.mtlist, self.content[x].data, label=plot_label)
		ax.set_ylabel("Intensity (rel.)")
		ax.set_xlabel("Mixing Time (s)")
		plt.legend()
		plt.show()
		return plt

	#compare two chunks between each other
	def fn_compare(self, second):
		from copy import deepcopy
		from numpy import trapz

		if len(self.content) <= len(second.content):
			list1_c = deepcopy(self.content)
			list2_c = deepcopy(second.content)
		else:
			list1_c = deepcopy(second.content)
			list2_c = deepcopy(self.content)

		CCF = 1.
		# sort list1 on importance
		list1_c.sort(key=lambda x: x.size, reverse=True)
		# find best comparable curve and save the data
		for x in range(len(list1_c)):
			curve1 = list1_c[x]
			best = -1.
			best_curve = 0.
			for curve2 in list2_c:
				temp = 0.8*curve1.fn_compare(curve2,norm=True) + 0.2*curve1.fn_compare(curve2)

				if temp > best:
					best = temp
					best_curve = curve2
			if best_curve != 0.:
				list2_c.remove(best_curve)
				CCF *= best
			else: print('error')
		# punish for the remaining curves
		tot = 1
		for x in list2_c:
			tot += 3*trapz(x.data)
		return CCF / tot




########################################################################################################################
########################################################################################################################

class Curve(object): #use to collect all the information on each peak
	def __init__(self, curve, index, max_curve, mtlist, Settings, ppm=0, duplet_ppm = 0):
		#info directly given from the Values
		self.data = curve
		self.index = index
		self.max_curve = max_curve
		self.mtlist = mtlist
		self.Settings = Settings

		from numpy import trapz, where

		#calculate required information which is different
		from functions import fn_rico, ppm_from_index
		from numpy import mean, trapz
		if ppm == 0:
			self.ppm = ppm_from_index(self.index[0]+where(self.max_curve==max(max_curve))[0][0], self.Settings["SO1_ppm"], self.Settings["SW_ppm"], self.Settings["res"])
		else:
			self.ppm = ppm
		if duplet_ppm == 0:
			self.duplet_ppm = 0
		else:
			self.duplet_ppm = duplet_ppm
		self.size = trapz(self.data)
		self.ok = (mean(self.data)) != 0. and trapz(self.data) > 0.1
		if self.ppm > 4 and (max(self.max_curve) < 0.3): self.ok = False
		self.alpha = (self.ppm > 4) and (max(self.max_curve) > 0.3)
		self.rico = fn_rico(self.data, mtlist)
		self.duplet = False
		self.triplet = False
		self.quadruplet = False
		self.baseline_corr = False

	def fn_duplet(curve1, curve2, duplet_ppm):
		if (abs(curve1.ppm - curve2.ppm) < duplet_ppm) and (curve1.fn_compare(curve2) > 0.35):
			return True
		else:
			return False

	def fn_triplet(curve1, curve2, curve3, duplet_ppm):
		quadruplet = curve1.quadruplet or curve2.quadruplet or curve3.quadruplet
		duplet = curve1.duplet or curve2.duplet or curve3.duplet
		similar = min([curve1.fn_compare(curve2), curve1.fn_compare(curve3)]) > 0.3 and min([curve2.fn_compare(curve1,norm=True), curve2.fn_compare(curve3,norm=True)]) > 0.5
		if (abs(curve1.ppm - curve2.ppm) < duplet_ppm) and (abs(curve2.ppm - curve3.ppm) < duplet_ppm) and (abs(abs(curve2.ppm - curve3.ppm) - abs(curve1.ppm - curve2.ppm)) < 0.004) and not quadruplet and not duplet and similar:
			odd = 1
		else:
			odd = 0
		comp = min([curve1.fn_compare(curve2), curve1.fn_compare(curve3)])
		comp_norm = min([curve2.fn_compare(curve1,norm=True), curve2.fn_compare(curve3,norm=True)])
		return odd*comp*comp_norm/abs(abs(curve2.ppm - curve3.ppm) - abs(curve1.ppm - curve2.ppm))

	def fn_compare(self, second, norm = False):
		import numpy as np
		import math
		data1 = self.data
		data2 = second.data
		if norm:
			data1 = np.array(data1)/np.max(data1)
			data2 = np.array(data2)/np.max(data2)
		# here you can play with the diff types of correlations
		if self.Settings["am_norm"]:
			# use the Frechet distance instead of the normal curve
			from functions import fn_frechet
			corr = (fn_frechet(data1, data2, self.mtlist))

		else:
			maxi = max(np.trapz(np.abs(data1)), np.trapz(np.abs(data2)))
			corr = np.trapz(np.abs(np.array(data1) - np.array(data2))) / maxi
		if math.isnan(corr) or corr < 0.0000002:
			corr = 0.0
		if corr > 1.0:
			corr = 1.0
		#switch from how different to how similar
		corr = 1.0 - corr
		#returns correlation % - 1 is perfect!
		return corr


########################################################################################################################
########################################################################################################################

class Database(object):
	def __init__(self, dir, printlabel, Settings="empty"):
		self.dir = dir #storage location of the database
		if Settings == "empty":
			from functions import fn_settings
			Settings = fn_settings()
		self.Settings = Settings
		self.printlabel = printlabel

		#check for existing file in location
		self.fn_load()
		if self.content != []:
			self.status = True
		else:
			self.status = False # if the status is false; the GUI should show this; meaning it has to be compiled!

	def fn_load(self):
		# load in the functions
		from pickle import load
		from functions import fn_check_dir
		from GUI_mainframe import update_GUI
		if (fn_check_dir(self.dir, r"\Database.p")):
			self.content = load(open(self.dir + r"\Database.p", "rb"))
			update_GUI("Loaded the Database from given location.", self.printlabel)
			self.fn_override_settings(self.Settings)
		else:
			self.content = []
			update_GUI("No database file was found in the given location.", self.printlabel)
		return self

	def fn_compile(self):

		from GUI_mainframe import update_GUI
		from functions import fn_check_folders

		# check if database exist and prompt user
		from functions import fn_check_dir, fn_progress_gen
		if fn_check_dir(self.dir, "Database.p"):
			import tkinter.messagebox as mg
			if self.printlabel == "testing":
				import tkinter as tk
				crap = tk.Tk()
				crap.withdraw()
			override = mg.askyesno("Delete", "Override current database?\nIf you are missing items the database will not be complete.")
			if not override:
				update_GUI("Not performing database compilation.", self.printlabel)
				return

		# check for all existing folders in the given location
		dir_list = fn_check_folders(self.dir)
		self.dir_list = dir_list
		#initialise all experiments and calculate progressbar
		progress = round(0.000000, 1)

		update_GUI("Performing database compilation.", self.printlabel)
		# wipe current
		self.content = []
		for y in range(len(self.dir_list)):
			if round((1+y) / (len(dir_list)+1), 1) != progress:
				progress = round(y / len(dir_list), 1)
				update_GUI(fn_progress_gen(progress), self.printlabel)

			#load in the experiment
			exp = Experiment(dir_list[y]+"\\pdata\\1", "ignore")
			for chunk in exp.chunks:
				self.content.append(chunk)
		self.status = self.fn_save()

	def fn_save(self):
		#save the files
		from GUI_mainframe import update_GUI
		import pickle
		update_GUI("Completed database - 100%", self.printlabel)
		pickle.dump(self.content, open(self.dir + r"\Database.p", "wb"))

		# temporary add an extra txt file
		if str(self.printlabel) == "testing":
			file = open(self.dir + r"\Database.txt", "a")
			for x in self.content:
				file.write(str(x) + "\n")
		self.status = True
		return self.status

	def fn_plot(self, list1):
		temp_list = []
		for chunk in data.content:
			if chunk.sample_name in list1:
				temp_list.append(chunk)
		if len(temp_list) != 0:
			temp_list[0].fn_plot(temp_list[1:])

	def fn_override_settings(self, Settings):
		self.Settings = Settings
		for x in self.content:
			x.Settings = Settings
			for y in x.content.content:
				y.Settings = Settings



########################################################################################################################
########################################################################################################################
#code for testing purpoces and to create graphs - not used by the distribution

if __name__ == "__main__":
	"""
	test = Experiment(r"D:\DATA\master2016\DATABASE\72\pdata\1", "testing")
	test.fn_plot()
	test.chunks[0].fn_plot([test.chunks[1]])
	test.chunks[1].content.fn_plot()

	print(test.chunks[0].content.fn_compare(test.chunks[1].content))
	print(test.chunks[0].content.fn_compare(test.chunks[2].content))

	"""

	from config import Database_Directory
	from functions import fn_settings
	data = Database(Database_Directory, "testing", fn_settings())
	#data.fn_plot(["a-L_Rhamnopyr.","b-Ribofur.","b-Ribofur."])
	#data.fn_plot(["a-Galactopyr.", "b-Arabinopyr."])
	print(len(data.content))

	#test = Experiment(r"D:\DATA\master2016\Test_500_3d\3\pdata\1", "testing")
	#test = Experiment(r"D:\DATA\master2016\Samples\32\pdata\1","testing")
	#print(test.chunks[0].max_curve)
	#comp = test.chunks[0].fn_compare(data)
	#comp = test.chunks[5].fn_compare(data)


	if True:	#perform cluster analysis
		from functions import fn_cluster_analysis
		fn_cluster_analysis(data)

	#function to compare katelijne data - still need DTW
	if False:
		from Proces_katelijne import katelijne
		from functions import fn_settings
		kat = katelijne("testing", fn_settings())
		for x in kat:
			if x.sample_name == "b-Rhamnopyr.":
				for y in data.content:
					if y.sample_name == "a-Rhamnopyr.":
						print(type(x), type(y))
						print(x.fn_plot(y))

	#plot the max curve from a specific monosaccharide
	if False:
		for x in data.content:
			if x.sample_name == "a-Glucopyr.":
				a = x
				import matplotlib.pyplot as plt
				fig = plt.figure()
				ax = plt.subplot()

				plt.plot(x.max_curve)
				ax.set_ylabel("Intensity (rel.)")
				ax.set_xlabel("Data point")
				plt.show()

				x.fn_plot()
				x.content.fn_plot()