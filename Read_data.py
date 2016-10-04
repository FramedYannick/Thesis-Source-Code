
#import needed modules
import nmrglue as ng						#NMR software
import numpy as np

#check if a xml file is present in the current dir
def fn_check_xml(dir):
	import os.path
	return (os.path.isfile(dir + r"\peaklist.xml"))

def fn_read_xml(dir):
	from xml.dom import minidom
	doc = minidom.parse(dir + r"\peaklist.xml")
	itemlist = doc.getElementsByTagName('Peak2D')
	peaks_ppm = []
	for x in itemlist:
		peaks_ppm.append([float(x.attributes['F1'].value), float(x.attributes['F2'].value), float(x.attributes['intensity'].value)])
	print(len(peaks_ppm))
	return (peaks_ppm)

def fn_sort_peaks (peaks_ppm):				#list of peaks; each peak is list [x, y, intensity] will add anotation
	import config
	peaks_ppm_diag = []
	peaks_ppm_cross = []
	for x in peaks_ppm:
		if (abs(x[0]-x[1]) <= config.Default_Threshhold_sep):
			peaks_ppm_diag.append(x)
		else:
			peaks_ppm_cross.append(x)
	#sort diag & crosspeaks on from bottom to top
	from operator import itemgetter
	peaks_ppm_diag = sorted(peaks_ppm_diag, key=itemgetter(1), reverse=True)
	peaks_ppm_cross = sorted(peaks_ppm_cross, key=itemgetter(1), reverse=True)
	#devide both boundries
	#split up top and bottom half for faster sweeping
	#remove crosspeaks lower then lowest diag
	#resort to make a list of sugars
	#annotate per sugar (letter plus number)
	return ([peaks_ppm_diag, peaks_ppm_cross])