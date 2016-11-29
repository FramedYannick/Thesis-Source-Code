"""""
designed by Dandois for reading the data using the NMRGlue python processing module

"""

def fn_read_data(dir, printlabel):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from GUI_mainframe import update_GUI
	#read in the data from given dir
	update_GUI("Reading in data.",printlabel)

	#read the data
	dic, data = ng.bruker.read_pdata(dir)  # this has been processed with topspin; no math is needed

	# collect the parameters and convert to ppm
	dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	#SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
	SW_hz = float(dic['procs']['SW_p'])
	SW_ppm = SW_hz / B0_hz
	duplet_ppm = 15/B0_hz #from Karplus

	#collect the list parameters
	vclist = []
	from functions import fn_check_dir
	if (fn_check_dir(dir[:dir.find('pdata')],r'\vclist')):
		vclist_file = open(dir[:dir.find('pdata')] + r'\vclist', 'r').readlines()
		for x in vclist_file:
			vclist.append(int(x))
	fqlist = []
	fqlist_ppm = []
	if (fn_check_dir(dir[:dir.find('pdata')], r'\fq0list')):
		fqlist_file = open(dir[:dir.find('pdata')] + r'\fq0list', 'r').readlines()
		for x in fqlist_file:
			if x != "o 700.130000\n":
				fqlist.append(float(x))
				fqlist_ppm.append(float(x)/B0_hz)

	#colect the title
	if (fn_check_dir(dir, "title")):
		title_line = open(dir + r"\title", 'r').readlines()[0]
		if (title_line.find("-") != -1):
			sample_name = title_line[:(title_line.find("-") -1)]
			extra_info = title_line[:(title_line.find("-") +1)]
		else:
			sample_name = title_line
			extra_info = ""
	else:
		sample_name = "unknown"
		extra_info = "unknown"

	#print out the title
	if sample_name != "unknown":
		update_GUI("Working on %s" %sample_name, printlabel)

	#temporary reform of data due to 'oversave effect' - should no longer be needed due to the chunkification
	from copy import deepcopy
	test_data = deepcopy(data)
	data = []
	for x in range(len(test_data)):
		if (test_data[x][0] != 0.0):
			data.append(test_data[x])

	#create central dictionary with params and pas it on
	dict_param = {"vclist":vclist, "fqlist_ppm":fqlist_ppm, "SW_ppm":SW_ppm, "duplet_ppm":duplet_ppm, "sample_name":sample_name, "extra_info":extra_info}
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
	num_fq = len(fqlist_u)

	#chunk up the data per fq and remove the minus signals (reduce data amount for calculations)
	#also normalise the data per chunk!
	new_data = []
	for x in range(num_fq):
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
		chunk_peak_ind = pk.indexes(chunk_max, thres = 0.0)
		#recheck the peak index search function
		#chunk_peak_ind = detect_peaks(data[len(data)-1], mph=(np.max(data)*config.Default_minpeakhight), mpd=(config.Default_inter_peak_distance*len(data[len(data)-1])/SW_ppm),threshold=config.Default_Threshold,edge='rising',show=config.Default_show)

		#remove super low peaks (background noise)
		limit = 0.005*np.max(chunk_max)	#set a noise peak limit
		temp_ind = []
		for x in chunk_peak_ind:
			if chunk_max[x] > limit:
				temp_ind.append(x)
		chunk_peak_ind = temp_ind

		#find the integrals - no support is given towards the intensity mode for now!
		from functions import fn_integrals
		[chunk_integrals, chunk_peak_ind] = fn_integrals(chunk_max, chunk_peak_ind)

		#find the integral curves
		from functions import fn_integrate
		chunk_values, chunk_peak_ind_ppm = fn_integrate(chunk, chunk_integrals, chunk_peak_ind, SW_ppm)

		#store everything in the chunk parameter tuple
		chunk_par["chunk_values"] = chunk_values
		chunk_par["chunk_integrals"] = chunk_integrals
		chunk_par["chunk_peak_ind_ppm"] = chunk_peak_ind_ppm
		chunk_par["chunk_max"] = chunk_max

		#store the chunk parameter tuple in a list
		chunk_param.append(chunk_par)
	#store the list in dict param to keep the uniform data structure
	dict_param["chunk_param"] = chunk_param
	return dict_param, data



#process the curves towards the database comparison
def fn_process_curve(dict_param, printlabel):
	#update the GUI
	from GUI_mainframe import update_GUI
	update_GUI("Fitting curves...",printlabel)
	#set needed general variables from dict
	import numpy as np
	#perform the action on every chunk
	for chunk_num in range(len(dict_param["chunk_param"])):
		chunk_param = dict_param["chunk_param"][chunk_num]
		peak_info = []
		#perform the action on every peak
		for peak_num in range(len(chunk_param["chunk_values"])):
			temp_ppm = chunk_param["chunk_peak_ind_ppm"][peak_num]
			temp_values = chunk_param["chunk_values"][peak_num]
			temp_info = {}

			#collect all the info
			#splitting the peaks in alpha and beta peaks
			temp_info["alpha"] = (temp_ppm > 4.25 and temp_values[0] > 0.3)

			#test for linearity
			from functions import fn_correlation, fn_rico
			temp_info["linearity"] = fn_correlation(temp_values)
			temp_info["rico"] = fn_rico(temp_values, dict_param["vclist"])



			peak_info.append(temp_info)
		#save the peak list into the chunk_param
		chunk_param["peak_info"] = peak_info

		#perform filtering
		from functions import fn_integral_filter
		chunk_param = fn_integral_filter(chunk_param)






		#store the chunk_param back into the dict_param
		dict_param["chunk_param"][chunk_num] = chunk_param
	return dict_param