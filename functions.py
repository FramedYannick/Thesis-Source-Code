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
		while (chunk_max[y] > 0.605630659713 * chunk_max[x] and y > 2 or chunk_max[y] > 0.07):
			y = y - 1
		while (chunk_max[z] > 0.605630659713 * chunk_max[x] and z < len(chunk_max)-2 or chunk_max[z] > 0.07):
			z = z + 1
		integral_limits.append([y, z])

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
	remove = sorted(remove, reverse=True)
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
def fn_integral_filter(chunk_param):

	return chunk_param


#calculate the correlation coeff
def fn_correlation (list, list2 = []):
	from numpy import corrcoef
	if len(list2) == 0:
		for x in range(len(list)):
			list2.append(x)
	#will test linearity if only one list is given
	correlation = corrcoef(list, list2)[0][1]
	return correlation





#calculate the rico between the first and last point
def fn_rico (list, vclist):
	return (list[len(list)-1] - list[0])/(len(vclist))