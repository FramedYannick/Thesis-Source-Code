"""""
designed by Dandois for reading the data using the NMRGlue python processing module

"""

def fn_read_data(dir, printlabel="testing"): #CLASSIFIED
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from functions import fn_check_dir
	from GUI_mainframe import update_GUI
	#read in the data from given dir
	update_GUI("Reading in data.",printlabel)

	#read the data
	dic, data = ng.bruker.read_pdata(dir)  # this has been processed with topspin; no math is needed

	#read in the alternate data if possible - compenation for the NMRGlue chunk error
	data_file = ""
	if fn_check_dir(dir, "DATABASE.txt"):
		data_file = open(dir + r"\DATABASE.txt", 'r').readlines()
	elif fn_check_dir(dir, "SAMPLES.txt"):
		data_file = open(dir + r"\SAMPLES.txt", 'r').readlines()
	if data_file != "":
		data = []
		for line in data_file:
			if ("row" in line):
				data.append([])
			else:
				if "#" not in line:
					data[len(data)-1].append(float(line.replace(r"\n","")))
	else:
		update_GUI("No extra data file was found...", printlabel)
		quit()

	# collect the parameters and convert to ppm
	dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	#SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
	SW_hz = float(dic['procs']['SW_p'])
	SW_ppm = SW_hz / B0_hz
	duplet_ppm = 15/B0_hz #from Karplus

	dic3 = open(dir[:dir.find('pdata')] + r'\acqu2s', 'r').read()
	chunk_num = int(int(dic3[dic3.find(r'$TD=') + 5:dic3.find(r'$TD=')+7])/13)

	#collect the list parameters
	vclist = []
	if (fn_check_dir(dir[:dir.find('pdata')],r'\vclist')):
		vclist_file = open(dir[:dir.find('pdata')] + r'\vclist', 'r').readlines()
		for x in vclist_file:
			vclist.append(int(x))
	fqlist = []
	fqlist_ppm = []
	if (fn_check_dir(dir[:dir.find('pdata')], r'\fq0list')):
		fqlist_file = open(dir[:dir.find('pdata')] + r'\fq0list', 'r').readlines()
		for x in range(len(fqlist_file)):
			if x != 0:
				fqlist.append(float(fqlist_file[x]))
				fqlist_ppm.append(float(fqlist_file[x])/B0_hz)

	#calculate the correct time interval
	mtlist = []
	for x in vclist:
		mtlist.append(115.122*25*10**(-6)*x)

	#colect the title
	from functions import fn_read_title
	sample_name, extra_info, order = fn_read_title(dir)

	#print out the title
	update_GUI("Working on %s sample." %sample_name, printlabel)

	#temporary reform of data due to 'oversave effect' - should no longer be needed due to the chunkification
	from copy import deepcopy
	test_data = deepcopy(data)
	data = []
	for x in range(len(test_data)):
		if (test_data[x][0] != 0.0):
			data.append(test_data[x])

	#create central dictionary with params and pas it on
	dict_param = {"vclist":vclist, "fqlist_ppm":fqlist_ppm, "SW_ppm":SW_ppm, "duplet_ppm":duplet_ppm, "sample_name":sample_name, "extra_info":extra_info, "mtlist": mtlist, "order": order,"chunk_num":chunk_num}
	return dict_param, data



#function to split up data; and find the unique frequencies
#returns list with each fq specific data and the unique fqlist
def fn_reform (dict_param, data):
	import numpy as np

	#set the easy variables
	vclist, fqlist = dict_param["vclist"], dict_param["fqlist_ppm"]
	dict_param["SW_ppm"] = dict_param["SW_ppm"]/2

	#find the unique fqs
	from functions import fn_unique
	fqlist_u = fn_unique(fqlist)

	#chunk up the data per fq and remove the minus signals (reduce data amount for calculations)
	#also normalise the data per chunk!
	new_data = []
	for x in range(dict_param["chunk_num"]):
		chunk = data[x*len(vclist):((x+1)*len(vclist))]
		max = np.max(chunk)
		row = chunk[0]
		keep = int(len(row)/2)	#remove negative half
		new_chunk = []
		for row in chunk:
			new_chunk.append(row[:keep]/max)
		new_data.append(new_chunk)
	dict_param["fqlist_ppm_u"] = fqlist_u
	return dict_param, new_data



#function to process the data - find the max of data; and the peaklist
def fn_process_chunk(dict_param, data, printlabel):
	import nmrglue as ng
	import numpy as np
	import peakutils as pk

	from GUI_mainframe import update_GUI
	update_GUI("Calculating peaks and integrals for each chunk.", printlabel)

	#define data variables - should be removed
	SW_ppm = dict_param["SW_ppm"]
	chunk_param = []
	for chunk in data:
		chunk_par = {}
		chunk_max = []		#find the max curve for peak picking
		for x in np.array(chunk).T:
			chunk_max.append(np.max(x))
		chunk_par["chunk_max"] = chunk_max
		chunk_peak_ind = pk.indexes(chunk_par["chunk_max"], thres = 0.0)
		#recheck the peak index search function
		from detect_peaks import detect_peaks
		chunk_peak_ind = detect_peaks(chunk_par["chunk_max"],show=False)

		#remove super low peaks (background noise)
		from functions import fn_noise_filter
		chunk_par["chunk_peak_ind"], chunk_par["chunk_noise"] = fn_noise_filter(chunk_peak_ind, chunk_par["chunk_max"])

		#find the integrals - no support is given towards the intensity mode for now!
		from functions import fn_integrals
		chunk_par["chunk_integrals"], chunk_par["chunk_peak_ind"] = fn_integrals(chunk_par["chunk_max"], chunk_par["chunk_peak_ind"], chunk_par["chunk_noise"])

		#find the integral curves
		from functions import fn_integrate
		chunk_par["chunk_values"], chunk_par["chunk_peak_ind_ppm"] = fn_integrate(chunk, chunk_par["chunk_integrals"], chunk_par["chunk_peak_ind"], SW_ppm)

		#store the chunk parameter tuple in a list
		chunk_param.append(chunk_par)
	#store the list in dict param to keep the uniform data structure
	dict_param["chunk_param"] = chunk_param
	return dict_param, data


#process the curves towards the database comparison
def fn_process_curve(dict_param, data, printlabel):
	#update the GUI
	from GUI_mainframe import update_GUI
	update_GUI("Fitting curves...",printlabel)
	#set needed general variables from dict
	import numpy as np
	#perform the action on every chunk
	for chunk_num in range(len(dict_param["chunk_param"])):
		chunk_param = dict_param["chunk_param"][chunk_num]

		#add the title for each chunk
		order = dict_param["order"]
		if len(order) != 0:
			title = order[chunk_num]
		else:
			title = "%i-%s" %(chunk_num, dict_param["sample_name"])
		chunk_param["sample_name"] = title
		chunk_param["peak_info"] = []
#all done till here
		#perform the action on every peak
		for peak_num in range(len(chunk_param["chunk_values"])):
			temp_ppm = chunk_param["chunk_peak_ind_ppm"][peak_num]
			temp_values = chunk_param["chunk_values"][peak_num]
			peak_info = {}

			#collect all the info
			#splitting the peaks in alpha and beta peaks
			peak_info["alpha"] = (temp_ppm > 4.25 and temp_values[0] > 0.3)

			#test for linearity
			from functions import fn_correlation, fn_rico
			peak_info["linearity"] = fn_correlation(temp_values)
			peak_info["rico"] = fn_rico(temp_values, dict_param["vclist"])

			#save the info into chunk info
			chunk_param["peak_info"].append(peak_info)

		#perform filtering - recalculate the integrals if we have duplets and triplets
		from functions import fn_integral_filter
		chunk_param, redo_integrals = fn_integral_filter(chunk_param, dict_param["duplet_ppm"])
		if redo_integrals:
			# find the integral curves
			from functions import fn_integrate
			chunk_param["chunk_values"], chunk_param["chunk_peak_ind_ppm"] = fn_integrate(data[chunk_num], chunk_param["chunk_integrals"], chunk_param["chunk_peak_ind"], dict_param["SW_ppm"])
		from functions import fn_thresholt_filter
		chunk_param = fn_thresholt_filter(chunk_param)


		#store the chunk_param back into the dict_param - can be removed but kept for increased readability
		dict_param["chunk_param"][chunk_num] = chunk_param
	return dict_param


#function that will handle all other functions - to be called directly from the GUI
def fn_main_function(dir, printlabel="testing"):
	import numpy as np
	np.seterr(all="ignore")
	from GUI_mainframe import update_GUI
	import database as db

	dict_param, data = fn_read_data(dir, printlabel)
	dict_param, data = fn_reform(dict_param, data)
	dict_param, data = fn_process_chunk(dict_param, data, printlabel)
	dict_param = fn_process_curve(dict_param, data, printlabel)
	database = db.fn_load()

	result = db.fn_compare_database(dict_param, database, printlabel)
	shown_result = ""
	for x in range(len(result)):
		shown_result += "\n%s identified as %s with a factor of %f" % (dict_param["chunk_param"][x]["sample_name"], result[x][0][0]["sample_name"], result[x][0][1])
	update_GUI(shown_result, printlabel)

