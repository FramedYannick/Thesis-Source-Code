
class Experiment(object):
	"""
	designed to initialise an expermiment processing upon a given directory.
	also requires a printinglabel incase of visual feedback

	"""

	def __init__(self, dir,printlabel):
		import nmrglue as ng
		import numpy as np
		from functions import fn_check_dir
		from GUI_mainframe import update_GUI
		update_GUI("Reading in data.",printlabel)

		self.dir = dir
		self.printlabel = printlabel

		self.dic, self.data = ng.bruker.read_pdata(dir)


		# read in the alternate data if possible - compenation for the NMRGlue chunk error
		# can be deleted once we fixed nmrglue!!!
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

		self.B0_hz, self.SW_ppm, self.SW_hz, self.duplet_ppm, self.chunk_num = fn_parameters(self.dic, self.dic2, self.dic3)

		# collect the lists
		self.vclist = fn_vclist(dir)
		self.fqlist, self.fqlist_ppm = fn_fqlist(dir, self.B0_hz)
		self.mtlist = np.array(self.vclist)*115.122 * 25 * 10 ** (-6)

		#colect the title
		self.sample_name, self.extra_info, self.order = fn_read_title(dir)

		# print out the title
		update_GUI("Working on %s sample." % self.sample_name, self.printlabel)

		# all data was read in now - end of initialisation of the sample


	#function designed to chunkify the data
	#def chunkify(self):
		import numpy as np
		from functions import fn_unique, fn_integrate
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
			chunk_temp = Chunk(new_chunk, title, self.fqlist[x], self.SW_ppm, self.duplet_ppm, self.mtlist, self.printlabel)
			self.chunks.append(chunk_temp)
		#return self # list of all chunk objects

	def fn_plot(self):
		import matplotlib.pyplot as plt
		from functions import fn_calc_plots
		chunks = self.chunks

		num = fn_calc_plots(chunks)
		for z in range(len(chunks)):
			x = chunks[z]  # x is a chunk object
			ax = plt.subplot(num + z)
			ax.set_title(x.sample_name)
			for y in (x.content.content):  # y is a curve object
				plt.plot(self.mtlist, y.data, label=(x.sample_name + " " + str(y.ppm)))
		plt.show()





########################################################################################################################
########################################################################################################################

#chunk class
class Chunk(object):
	def __init__(self, chunk_data, title, chunk_fq, SW_ppm, duplet_ppm, mtlist, printlabel):
		self.data = chunk_data
		self.sample_name = title
		self.chunk_fq = chunk_fq
		self.SW_ppm = SW_ppm
		self.duplet_ppm = duplet_ppm
		self.mtlist = mtlist
		self.printlabel = printlabel


		#import required functions
		import numpy as np
		#import peakutils as pk
		from detect_peaks import detect_peaks
		from functions import fn_max_curve, fn_noise_filter, fn_integrals, fn_integrate_new

		#find the max curve
		self.max_curve = fn_max_curve(self.data)

		#calculate the peaks	chunk_peak_ind = pk.indexes(self.max_curve, thres = 0.0)
		temp_indices = detect_peaks(self.max_curve,show=False)

		# remove super low peaks (background noise)
		self.indices, self.noise = fn_noise_filter(temp_indices, self.max_curve)

		#find the integral limits
		self.integrals, self.indices = fn_integrals(self.max_curve, self.indices, self.noise)

		#calculate the integral values
		temp_values, self.integrals, self.indices, self.indices_ppm = fn_integrate_new(self.data, self.integrals, self.indices, self.SW_ppm)
		#set the content using the Values class
		self.content = Values(temp_values, self.indices, self.indices_ppm, self.sample_name, self.mtlist, self.printlabel)

	def fn_plot(self, second = []):
		chunk_list = [self]
		if type(second) == Chunk:
			chunk_list += [second]
		elif type(second) == list:
			chunk_list += second

		import matplotlib.pyplot as plt
		plt.figure()
		for x in range(len(chunk_list)):
			for y in range(len(chunk_list[x].content.content)):
				if y == 0:
					plt.plot(chunk_list[x].content.content[y].data, ["r-", "g-", "b-", "o-"][x], label=chunk_list[x].sample_name)
				else:
					plt.plot(chunk_list[x].content.content[y].data, ["r-", "g-", "b-", "o-"][x])
		plt.legend()
		plt.show()







########################################################################################################################
########################################################################################################################

class Values(object): # prob gonna reorder the chunk class to a more definit way of handling it
	def __init__(self, values, peak_ind, peak_ind_ppm, sample_name, mtlist, printlabel):
		#set all parameters given for backup
		self.data = values 		#self.data now is a list of lists
		self.peak_ind = peak_ind
		self.peak_ind_ppm = peak_ind_ppm
		self.sample_name = sample_name
		self.mtlist = mtlist
		self.printlabel = printlabel


		#import GUI printer
		from GUI_mainframe import update_GUI
		update_GUI("Fitting curves...",self.printlabel)

		self.content = []		#self.content will become a list of curves
		#split up the values into different curves
		for x in range(len(self.data)):
			temp_curve = Curve(self.data[x], self.peak_ind_ppm[x], self.mtlist)
			if temp_curve.ok:
				self.content.append(temp_curve)

	def fn_plot(self):
		import matplotlib.pyplot as plt
		plt.figure()
		ax = plt.subplot()
		ax.set_title(self.sample_name)
		for x in range(len(self.content)):
			plot_label = str(self.content[x].ppm)[:5] + " ppm"
			plt.plot(self.content[x].data, label=plot_label)
		plt.legend()
		plt.show()

	#compare two chunks between each other
	def fn_compare(self, second):

		print("TODO")






















########################################################################################################################
########################################################################################################################

class Curve(object): #use to collect all the information on each peak
	def __init__(self, curve, temp_ppm, mtlist):
		#info directly given from the Values
		self.data = curve
		self.ppm = temp_ppm
		self.mtlist = mtlist


		#calculate required information which is different
		from functions import fn_correlation, fn_rico
		from numpy import mean
		self.ok = (mean(self.data)) != 0.
		self.alpha = (self.ppm > 4.25) #and (self.data.max() > 0.3)
		self.linearity = fn_correlation(self.data)
		self.rico = fn_rico(self.data, mtlist)

	def fn_compare(self, second):
		import numpy as np
		import math
		# here you can play with the diff types of correlations
		max = max(np.trapz(abs(self.data)), np.trapz(abs(second.data)))
		corr = np.trapz(abs(np.array(self.data) - np.array(second.data))) / max
		if math.isnan(corr):
			corr = 0.0
		if corr > 1.0:
			corr = 1.0
		return 1.0 - corr



########################################################################################################################
########################################################################################################################

test = Experiment(r"D:\DATA\master2016\DATABASE\93\pdata\1", "testing")
test.chunks[0].fn_plot([test.chunks[1],test.chunks[2]])
test.chunks[1].content.fn_plot()


