"""""
designed by Dandois for reading the data using the NMRGlue python processing module

"""

def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))

def fn_read_data(dir,printlabel):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from GUI_mainframe import update_GUI
	# read in the data from given dir
	update_GUI("Reading in data.\ntesting second line",printlabel)

	dic, data = ng.bruker.read_pdata(dir)  # this has been processed with topspin; no math is needed

	#temporary reform of data due to 'oversave effect'
	from copy import deepcopy
	test_data = deepcopy(data)
	data = []
	for x in test_data:
		if x[0] != 0.0:
			data.append(x)

	# collect the parameters and convert to ppm
	dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
	SW_hz = float(dic['procs']['SW_p'])
	SW_ppm = SW_hz / B0_hz
	SO1_ppm = SO1_hz / B0_hz
	duplet_ppm = 14/B0_hz

	#collect the list type parameter (should be changed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
	vclist = []
	vclist_file = open(dir[:dir.find('pdata')] + r'\vclist', 'r').readlines()
	for x in vclist_file:
		vclist.append(int(x))

	#temperature shift correction on the data
	temp = []
	zeromax = max(enumerate(data[0]),key=(lambda x: x[1]))[0]
	for x in data:      #find a list with the shifts
			temp.append(max(enumerate(x[(zeromax - 3) : (zeromax + 3)]),key=(lambda x: x[1]))[0] + zeromax -3)
	for x in range(1,len(data)):
		if temp[x] < zeromax:
			for y in range(abs(temp[x] - zeromax)):
				data[x] = np.insert(data[x],0,0.00001)
				data[x] = np.delete(data[x],len(data[x])-1)
		elif temp[x] > zeromax:
			for y in range(abs(temp[x] - zeromax)):
				data[x] = np.delete(data[x],0)
				data.append(0.)
	return vclist, data, SW_ppm, SO1_ppm, duplet_ppm




def fn_process_peaks(vclist, data, SW_ppm, SO1_ppm, printlabel):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	from GUI_mainframe import update_GUI

	#search for the peaks in the last data point
	if (config.Default_show):
		update_GUI("Please double check the peaks.",printlabel)

	#max compensation algorithm
	data_max = []
	for x in np.array(data).T:
		data_max.append(np.max(x))
	#peak picking - this is best done on non-normalised data
	#multiple have been tested; it has been shown that Marcos Duerto and peakutiles have been the most precise
	import peakutils as pk
	peaks_ind = pk.indexes(data_max, thres=0.0)

	# find the noise size
	#temp = []
	#for x in peaks_ind:
	#	temp.append(abs(data_max[x]))
	#limit = np.mean(temp)*10
	limit = 0.02*np.max(data_max) #set the limit to 2%; it has consistent results in comparison to calculations
	#remove peaks beneath the noise ratio
	ind_temp = []
	for x in peaks_ind:
		if data_max[x] > limit:
			ind_temp.append(x)
	peaks_ind = ind_temp
	#peaks_ind = detect_peaks(data[len(data)-1], mph=(np.max(data)*config.Default_minpeakhight), mpd=(config.Default_inter_peak_distance*len(data[len(data)-1])/SW_ppm),threshold=config.Default_Threshold,edge='rising',show=config.Default_show)


	#update the GUI
	npeaks = len(peaks_ind)
	update_GUI("Number of unique determined peaks:  %s\n" %str(npeaks),printlabel)

	#calculate all values per peak and convert ind to ppm
	peaks_value_list = []
	peak_ind_ppm = []
	for x in peaks_ind:
		peak_ind_ppm.append(((len(data[0])-x)/len(data[0])*SW_ppm)+(SO1_ppm-0.5*SW_ppm))
		temp = []
		for row in data:
			if config.Default_mode:
				#use the integral of the function - stepwize: 1. find boundries; 2. use trapz to achieve intensity; 3. fit curves will normalize anyway
				if config.Default_show:
					print("integral mode is not operatable yet")
				temp.append(row[x])
			else:
				temp.append(row[x])
		peaks_value_list.append(temp)
	return(vclist,peaks_value_list, peak_ind_ppm)     #list of mixing times, list of colums with intensities, list of ppm values of each decay listed


