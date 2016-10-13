
#check if a xml file is present in the current dir
def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))

def fn_read_xml(dir):                     #read in peaks from xml
	print("reading xml")
	from xml.dom import minidom
	doc = minidom.parse(dir + r"\peaklist.xml")
	itemlist = doc.getElementsByTagName('Peak2D')
	peaks_ppm = []
	for x in itemlist:
		peaks_ppm.append([float(x.attributes['F1'].value), float(x.attributes['F2'].value), float(x.attributes['intensity'].value)])
	return (peaks_ppm)


def fn_read_integrals (dir):            #not implemented obviously
	doc = open(dir + r"\integrals.txt")















def fn_check_peak (peak, peaks_ppm):    #check if peak is there - needed for copying
	import config
	peak_present = False
	for x in peaks_ppm:
		if ((abs(x[0]-peak[0]) < config.Default_Threshold_sep) and ((abs(x[1] - peak[1]) < config.Default_Threshold_sep))):
			peak_present = True
	return peak_present

#def fn_check_peak_area (peak, )

def fn_sort_peaks (peaks_ppm,dir):				#list of peaks; each peak is list [x, y, intensity] will add anotation
	import config
	peaks_ppm_diag = []
	peaks_ppm_cross = []
	for x in peaks_ppm:
		if (abs(x[0]-x[1]) <= config.Default_Diag_sep):
			peaks_ppm_diag.append(x + ['D'])
		else:
			peaks_ppm_cross.append(x + ['C'])

	# sort diag & crosspeaks on from high to low ppm
	from operator import itemgetter
	peaks_ppm_diag = sorted(peaks_ppm_diag, key=itemgetter(1), reverse=True)
	peaks_ppm_cross = sorted(peaks_ppm_cross, key=itemgetter(1), reverse=True)

	# remove crosspeaks outside diag range and split up peaks
	xmax = peaks_ppm_diag[0][0]
	ymax = peaks_ppm_diag[0][1]
	peaks_ppm_cross_top = []
	peaks_ppm_cross_bot = []
	for x in peaks_ppm_cross:
		if (x[0] > xmax) or x[1] > ymax:
			peaks_ppm_cross.remove(x)
		else:
			if x[0] - x[1] > 0:  # means it is above diagonal
				peaks_ppm_cross_top.append(x)
			else:
				peaks_ppm_cross_bot.append(x)

	#copy over the unexisting peaks in the other pannel
	if config.Default_copy:
		peaks_ppm_cross_temp = []
		for x in peaks_ppm_cross_top:
			if not (fn_check_peak([x[1],x[0]],peaks_ppm_cross_bot)):
				peak = [x[1], x[0], x[2]]
				peaks_ppm_cross_temp.append(peak)
		for x in peaks_ppm_cross_bot:
			if not (fn_check_peak([x[1], x[0]], peaks_ppm_cross_top)):
				peak = [x[1], x[0], x[2]]
				peaks_ppm_cross_top.append(peak)
		peaks_ppm_cross_bot += peaks_ppm_cross_temp

	#correct for artefacts around the alpha and for dup/triplets
	if config.Default_artefacts:
		#artefact correction

		#duplet correction


		print('no duplet compensation yet')





	# check for possible alpha peaks - inside range AND first of the system
	peaks_ppm_alpha = []
	for x in peaks_ppm_diag:
		if config.Default_Sugar_ARange[0] <= x[0] <= config.Default_Sugar_ARange[1]:
			alpha = True
			for y in peaks_ppm_cross_bot:
				if ((abs(x[0]-y[0]) < config.Default_Threshold_sep) and (x[1] < y[1])):
					alpha = False
			if alpha:
				peaks_ppm_alpha.append(x)



	# resort to make a list of sugars - only for bottom half
	# annotate per sugar (letter plus number)
	print(str(len(peaks_ppm_cross_top+peaks_ppm_cross_bot+peaks_ppm_diag)) + " and alpha: " + str(len(peaks_ppm_alpha)))
	return ([peaks_ppm_diag, peaks_ppm_alpha, peaks_ppm_cross_bot, peaks_ppm_cross_top])






