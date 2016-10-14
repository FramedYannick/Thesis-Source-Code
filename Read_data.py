"""""
designed by Dandois for reading the data using the NMRGlue python processing module

"""

def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))

def fn_fit_function(array):
	return 0

def fn_read_data(dir,label):
	import nmrglue as ng
	import numpy as np
	import matplotlib.pyplot as plt
	import config
	from detect_peaks import detect_peaks
	# read in the data from given dir
	label.set("Reading in data.")
	dic, data = ng.bruker.read_pdata(dir)  # this has been processed with topspin; no math is needed

	# collect the parameters and convert to ppm
	dic2 = open(dir[:dir.find('pdata')] + r'\acqus', 'r').read()
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
	SW_hz = float(dic['procs']['SW_p'])
	SW_ppm = SW_hz / B0_hz
	SO1_ppm = SO1_hz / B0_hz

	#search for the peaks in the last data point
	ind = detect_peaks(data[-1],mpd=(config.Default_inter_peak_distance*len(data[-1])/SW_ppm),threshold=config.Default_Threshold,edge='rising',show=True)
	print(ind)
	label.set("Number of peaks:  " +str(ind))



























