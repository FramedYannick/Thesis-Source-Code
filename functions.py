"""""
designed by Dandois for saving all the seperate small functions
#side functions as support

"""


#check if a file exists in a location
def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))


#make an unique version of a list
def fn_unique(list):
	unique = []
	[unique.append(item) for item in list if item not in unique]
	return unique


#find the required integrals on a curve; given the peaks
def fn_integrals(chunk_max, peaks_ind):
	# use the indices to find the integral limits
	integral_limits = []
	for x in peaks_ind:
		y, z = x, x  # y for the left bound; z for the right
		while (chunk_max[y] > 0.505630659713 * chunk_max[x] and y > 2 or chunk_max[y] > 0.07):
			y = y - 1
		while (chunk_max[z] > 0.4505630659713 * chunk_max[x] and z < len(chunk_max)-2 or chunk_max[z] > 0.07):
			z = z + 1
		integral_limits.append([y, z])

	#correct for identical integrals
	remove = []
	for x in range(len(peaks_ind)-1):
		if integral_limits[x] == integral_limits[x+1]:
			remove.append(x+1)
	unique = []
	[unique.append(item) for item in remove if item not in unique]
	remove = sorted(unique, reverse=True)
	for x in remove:
		peaks_ind.pop(x)
		integral_limits.pop(x)

	# correct for double integrals - upper limit
	remove = []
	for x in range(len(peaks_ind) - 1):
		for y in range(x + 1, len(peaks_ind)):
			if integral_limits[y][0] < integral_limits[x][1] < integral_limits[y][1]:
				integral_limits[y][0] = integral_limits[x][0]
				remove.append(x)
	unique = []
	[unique.append(item) for item in remove if item not in unique]
	remove = sorted(unique, reverse=True)
	for x in remove:
		peaks_ind.pop(x)
		integral_limits.pop(x)

	# correct for containing integrals
	remove = []
	for x in range(len(peaks_ind)):
		for y in range(len(peaks_ind)):
			if integral_limits[x][0] < integral_limits[y][0] and integral_limits[y][1] < integral_limits[x][1]:
				remove.append(y)
	unique = []
	[unique.append(item) for item in remove if item not in unique]
	remove = sorted(unique, reverse=True)
	for x in remove:
		peaks_ind.pop(x)
		integral_limits.pop(x)

	"""""
	#combine touching integrals - not used for the moment
	remove = []
	for x in range(len(peaks_ind) - 1):
		for y in range(x + 1, len(peaks_ind)):
			if integral_limits[x][1] == integral_limits[y][0]:
				integral_limits[y][0] = integral_limits[x][0]
				remove.append(x)
	remove = sorted(remove, reverse=True)
	for x in remove:
		peaks_ind.pop(x)
		integral_limits.pop(x)
	"""
	return [integral_limits, peaks_ind]


#calculate the integration curves
def fn_integrate(chunk, chunk_integrals, chunk_peak_ind, SW_ppm):
	import numpy as np
	chunk_values = []
	chunk_peak_ind_ppm = []
	for y in range(len(chunk_peak_ind)):  # loop over all indices
		x = chunk_peak_ind[y]
		chunk_peak_ind_ppm.append((len(chunk[0]) - x) / len(chunk[0]) * SW_ppm)  # ppm calculation of the integral
		temp = []
		for row in chunk:
			temp.append(np.trapz(row[chunk_integrals[y][0]:chunk_integrals[y][1]]))
		chunk_values.append(temp)
	# normalise per chunk
	chunk_values = chunk_values / np.max(chunk_values)
	return chunk_values, chunk_peak_ind_ppm


#find the subplot number
def fn_calc_plots (list):
	number = len(list)
	dict = {"1": 111, "2": 211, "3":311, "4":221,"5":321,"6":321,"7":331,"8":331,"9":331}
	if number > 9:
		return "error"
	else:
		return dict[str(number)]


#perform duplet and triplet filtering
def fn_duplet_filter(chunk_param, duplet_ppm):
	import numpy as np
	remove = []
	redo_integrals = False
	#compare peak #x with #(x+1)
	for x in range(len(chunk_param["chunk_peak_ind_ppm"])-1):
		#ppm diference
		delta_ppm = abs((chunk_param["chunk_peak_ind_ppm"][x+1] - chunk_param["chunk_peak_ind_ppm"][x])) < duplet_ppm
		#find the correlation between both
		PCC = abs(fn_correlation(chunk_param["chunk_values"][x], chunk_param["chunk_values"][x+1])) > 0.9

		if(delta_ppm and PCC):
			chunk_param["chunk_integrals"][x+1] = [chunk_param["chunk_integrals"][x][0],chunk_param["chunk_integrals"][x+1][1]]
			#stop the cycle and restart for x
			remove.append(x)
			redo_integrals = True

	#remove the data from the filtered out peaks
	remove = sorted(fn_unique(remove), reverse=True)
	for x in remove:
		chunk_param["chunk_values"].tolist().pop(x)
		chunk_param["chunk_peak_ind_ppm"].pop(x)
		chunk_param["peak_info"].pop(x)
		chunk_param["chunk_integrals"].pop(x)
		chunk_param["chunk_peak_ind"].pop(x)
	return chunk_param, redo_integrals


#remove the lowest 1.5%
def fn_thresholt_filter(chunk_param):
	import numpy as np
	remove = []
	for x in range(len(chunk_param["chunk_peak_ind_ppm"])):
		if np.max(chunk_param["chunk_values"]) < 0.2:
			remove.append(x)
		remove = sorted(fn_unique(remove), reverse=True)
	for x in remove:
		chunk_param["chunk_values"].tolist().pop(x)
		chunk_param["chunk_peak_ind_ppm"].pop(x)
		chunk_param["peak_info"].pop(x)
		chunk_param["chunk_integrals"].pop(x)
		chunk_param["chunk_peak_ind"].pop(x)
	return chunk_param


#calculate the correlation coeff - will calculate linearity if only one list is given
def fn_correlation (list, list2 = []):
	from numpy import corrcoef
	if len(list2) == 0:
		for x in range(len(list)):
			list2.append(x)
	correlation = corrcoef(list, list2)[0][1]
	return correlation


#calculate the SSD
def fn_SSD (listA, listB=[]):
	import numpy as np
	if listB == []:
		for x in range(len(listA)):
			listB.append(0.)
	data = np.array(listA) - np.array(listB)
	result = np.sqrt(np.sum((np.mean(data)-data)**2))
	return result


#calculate the rico between the first and last point
def fn_rico (list, vclist):
	return (list[len(list)-1] - list[0])/(len(vclist))