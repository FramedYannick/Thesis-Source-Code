"""""
designed by Dandois for reading the data using the NMRGlue python processing module

"""
#side functions as support

def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))

def fn_unique(list):
	unique = []
	[unique.append(item) for item in list if item not in unique]
	return unique













#######################################################################main functions

def fn_read_data(dir, printlabel):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from GUI_mainframe import update_GUI
	# read in the data from given dir
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
	if (fn_check_dir(dir[:dir.find('pdata')],r'\vclist')):
		vclist_file = open(dir[:dir.find('pdata')] + r'\vclist', 'r').readlines()
		for x in vclist_file:
			vclist.append(int(x))
	fqlist = []
	fqlist_ppm = []
	if (fn_check_dir(dir[:dir.find('pdata')], r'\fqlist')):
		fqlist_file = open(dir[:dir.find('pdata')] + r'\fqlist', 'r').readlines()
		for x in fqlist_file:
			fqlist.append(float(x))
			fqlist_ppm.append(float(x)/B0_hz)

	#temporary reform of data due to 'oversave effect'
	from copy import deepcopy
	test_data = deepcopy(data)
	data = []
	for x in range(len(test_data)):
		if test_data[x][0] != 0.0:
			data.append(x)
	return [vclist,fqlist_ppm], data, SW_ppm, duplet_ppm



#function to split up data; and find the unique frequencies
#returns list with each fq specific data and the unique fqlist
def fn_reform (data, lists, SW_hz, SW_ppm):
	import numpy as np

	#set the easy variables
	vclist, fqlist = lists[0], lists[1]
	SW_ppm, SW_hz = SW_ppm/2, SW_hz/2

	#find the unique fq and check for errors
	num_fq = int(len(fqlist)/len(vclist))
	fqlist_u = fn_unique(fqlist)
	if (not len(fqlist_u) == num_fq):
		print("Not a correct VCLIST!")
		exit("error")

	#chunk up the data per fq and remove the minus signals (reduce data amount for calculations)
	new_data = []
	for x in range(num_fq):
		chunk = data[x*len(vclist):((x+1)*len(vclist))]
		row = chunk[0]
		keep = len(row)/2	#remove negative half
		new_chunk = []
		for row in chunk:
			new_chunk.append(row[keep])
		new_data.append(new_chunk)
	return new_data, fqlist_u



#function to process the data - find the max of data; and the peaklist
def fn_process_chunk(data, printlabel):
	import nmrglue as ng
	import numpy as np
	import peakutils as pk

	from GUI_mainframe import update_GUI
	update_GUI("Calculating peaks and integrals for each chunk.", printlabel)

	#define data variables
	data_max = []
	data_peaks = []
	data_integrals = []

	for chunk in data:

		chunk_max = []		#find the max curve for peak picking
		for x in np.array(chunk).T:
			chunk_max.append(np.max(x))
		chunk_peak_ind = pk.indexes(chunk_max, thres = 0.0)
		#recheck the peak index search function
		#chunk_peak_ind = detect_peaks(data[len(data)-1], mph=(np.max(data)*config.Default_minpeakhight), mpd=(config.Default_inter_peak_distance*len(data[len(data)-1])/SW_ppm),threshold=config.Default_Threshold,edge='rising',show=config.Default_show)
		limit = 0.01*np.max(chunk_max)	#set a noise peak limit
		temp_ind = []
		for x in chunk_peak_ind:
			if chunk_max[x] > limit:
				temp_ind.append(x)
		chunk_peak_ind = temp_ind

		#use the indices to find the integral limits
		chunk_integrals = []

#integral function should be written here





		data_integrals.append(chunk_integrals)
		data_peaks.append(chunk_peak_ind)
		data_max.append(chunk_max)


	return data, data_max, data_peaks


#######################################################################################################################
#######################################################################################################################



#
def fn_process_peaks_old(vclist, data, SW_ppm, SO1_ppm, printlabel):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from GUI_mainframe import update_GUI




	#update the GUI
	update_GUI("Number of unique determined peaks:  %s\n" %str(len(peaks_ind)),printlabel)

	#find all integral limits
	if config.Default_mode:
		integral_limits = [] #format: list of [left boundry, right boundry]
		for x in peaks_ind:
			y, z = x, x #y for the left bound; z for the right
			while (data_max[y] > 0.605630659713 * data_max[x]):
				y = y - 1
			while (data_max[z] > 0.605630659713 * data_max[x]):
				z = z + 1
			integral_limits.append([y,z])

		#correct for double integrals - upper limit
		remove = []
		for x in range(len(peaks_ind)-1):
			for y in range(x+1,len(peaks_ind)):
				if integral_limits[y][0] < integral_limits[x][1] < integral_limits[y][1]:
					integral_limits[y][0] = integral_limits[x][0]
					remove.append(x)
		unique = []
		[unique.append(item) for item in remove if item not in unique]
		remove = sorted(unique, reverse=True)
		for x in remove:
			peaks_ind.pop(x)
			integral_limits.pop(x)
		#correct for containing integrals
		remove = []
		for x in range(len(peaks_ind)):
			for y in range(len(peaks_ind)):
				if integral_limits[x][0] < integral_limits[y][0] and integral_limits[y][1] < integral_limits[x][1]:
					remove.append(y)
		remove = sorted(remove, reverse=True)
		for x in remove:
			peaks_ind.pop(x)
			integral_limits.pop(x)


	#calculate all values per peak and convert ind to ppm
	peaks_value_list = []
	peak_ind_ppm = []
	for y in range(len(peaks_ind)):
		x = peaks_ind[y]
		peak_ind_ppm.append(((len(data[0])-x)/len(data[0])*SW_ppm)+(SO1_ppm-0.5*SW_ppm))
		temp = []
		for row in data:
			if config.Default_mode:
				temp.append(np.trapz(row[integral_limits[y][0]:integral_limits[y][1]])/0.682)
			else:
				temp.append(row[x])
		peaks_value_list.append(temp)
	return(vclist,peaks_value_list, peak_ind_ppm)     #list of mixing times, list of colums with intensities, list of ppm values of each decay listed


