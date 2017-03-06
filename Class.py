
class Experiment(object):
	"""
	designed to initialise an expermiment processing upon a given directory.
	also requires a printinglabel incase of visual feedback

	"""

	def __init__(self, dir, printlabel, Settings="empty"):
		import nmrglue as ng
		import numpy as np
		from functions import fn_check_dir
		from GUI_mainframe import update_GUI
		update_GUI("Reading in experiment.",printlabel)

		self.dir = dir
		if Settings == "empty":
			from functions import fn_settings
			Settings = fn_settings()
		self.Settings = Settings
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
			chunk_temp = Chunk(new_chunk, title, self.fqlist[x], self.SW_ppm, self.duplet_ppm, self.mtlist, self.printlabel, self.Settings)
			self.chunks.append(chunk_temp)
		#return self # list of all chunk objects

		if self.Settings["plot_exp"]:
			self.fn_plot()

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
	def __init__(self, chunk_data, title, chunk_fq, SW_ppm, duplet_ppm, mtlist, printlabel, Settings):
		self.data = chunk_data
		self.sample_name = title
		self.chunk_fq = chunk_fq
		self.SW_ppm = SW_ppm
		self.duplet_ppm = duplet_ppm	# redundant for now
		self.mtlist = mtlist
		self.printlabel = printlabel
		self.Settings = Settings


		#import required functions
		import numpy as np
		#import peakutils as pk
		from detect_peaks import detect_peaks
		from functions import fn_max_curve, fn_noise_filter, fn_integrals, fn_integrate_new

		#find the max curve
		self.max_curve = fn_max_curve(self.data)
		print(self.max_curve)

		if self.Settings["am_int"]:
			#from scipy.integrate import cumtrapz
			#temp = cumtrapz(self.max_curve)
			# use a min hight filter
			from functions import fn_alt_integrals
			self.integrals, self.indices, self.noise = fn_alt_integrals(self.max_curve)



		if not self.Settings["am_int"]:
			#calculate the peaks	chunk_peak_ind = pk.indexes(self.max_curve, thres = 0.0)
			temp_indices = detect_peaks(self.max_curve,show=False)

			# remove super low peaks (background noise)
			self.indices, self.noise = fn_noise_filter(temp_indices, self.max_curve)

			#find the integral limits
			self.integrals, self.indices = fn_integrals(self.max_curve, self.indices, self.noise)

		#calculate the integral values
		temp_values, self.integrals, self.indices, self.indices_ppm = fn_integrate_new(self.data, self.integrals, self.indices, self.SW_ppm)
		#set the content using the Values class
		self.content = Values(temp_values, self.indices, self.indices_ppm, self.sample_name, self.mtlist, self.printlabel, self.Settings)

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
		bord = [0,1]
		for x in range(len(chunk_list)):
			for y in range(len(chunk_list[x].content.content)):
				if y == 0:
					plt.plot(self.mtlist,(np.array(chunk_list[x].content.content[y].data)+x*0.001), ["r-", "g-", "b-", "o-"][x], label=chunk_list[x].sample_name)
				else:
					plt.plot(self.mtlist,(np.array(chunk_list[x].content.content[y].data)+x*0.001), ["r-", "g-", "b-", "o-"][x])
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
	def __init__(self, values, peak_ind, peak_ind_ppm, sample_name, mtlist, printlabel, Settings):
		#set all parameters given for backup
		self.data = values 		#self.data now is a list of lists
		self.peak_ind = peak_ind
		self.peak_ind_ppm = peak_ind_ppm
		self.sample_name = sample_name
		self.mtlist = mtlist
		self.printlabel = printlabel
		self.Settings = Settings


		#import GUI printer
		from GUI_mainframe import update_GUI
		update_GUI(format("Fitting curves on chunk of %s..." %self.sample_name), self.printlabel)

		self.content = []		#self.content will become a list of curves
		#split up the values into different curves
		for x in range(len(self.data)):
			temp_curve = Curve(self.data[x], self.peak_ind_ppm[x], self.mtlist, self.Settings)
			if temp_curve.ok:
				self.content.append(temp_curve)
		if self.Settings["plot_values"]:
			self.fn_plot()

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
				temp = curve1.fn_compare(curve2)
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
			tot += trapz(x.data)
		return CCF / tot




########################################################################################################################
########################################################################################################################

class Curve(object): #use to collect all the information on each peak
	def __init__(self, curve, temp_ppm, mtlist, Settings):
		#info directly given from the Values
		self.data = curve
		self.ppm = temp_ppm
		self.mtlist = mtlist
		self.Settings = Settings

		from numpy import trapz

		#calculate required information which is different
		from functions import fn_rico
		from numpy import mean, trapz
		self.size = trapz(self.data)
		self.ok = (mean(self.data)) != 0. and trapz(self.data) > 0.2
		self.alpha = (self.ppm > 4.25) #and (self.data.max() > 0.3)
		self.rico = fn_rico(self.data, mtlist)

	def fn_compare(self, second):
		import numpy as np
		import math
		# here you can play with the diff types of correlations
		if self.Settings["am_norm"]:
			# use the Frechet distance instead of the normal curve
			from functions import fn_frechet
			corr = (fn_frechet(self.data, second.data, self.mtlist))

		else:
			maxi = max(np.trapz(np.abs(self.data)), np.trapz(np.abs(second.data)))
			corr = np.trapz(np.abs(np.array(self.data) - np.array(second.data))) / maxi
		if math.isnan(corr) or corr < 0.0000002:
			corr = 0.0
		if corr > 1.0:
			corr = 1.0
		corr = 1.0 - corr
		#returns correlation% - 1 is perfect!
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
	#data.fn_plot(["a-Mannopyr.", "a-Rhamnopyr."])
	#data.fn_plot(["b-Mannopyr.", "b-Rhamnopyr."])
	#data.fn_plot(["a-Galactopyr.", "b-Arabinopyr."])


	test = Experiment(r"D:\DATA\master2016\SAMPLES\32\pdata\1", "testing")
	#comp = test.chunks[0].fn_compare(data)
	#comp = test.chunks[5].fn_compare(data)


	if False:	#perform cluster analysis
		from functions import fn_cluster_analysis
		fn_cluster_analysis(data)

	#compare a number of different monosaccharides
	if False:
		plotter = []
		for x in data.content:
			if x.sample_name in ["a-L_Rhamnopyr.","b-Ribofur.","b-Ribofur."]:
				plotter.append(x)
		plotter[0].fn_plot(plotter[1:])

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

	#plot everything from a specific monosaccharide
	if True:
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