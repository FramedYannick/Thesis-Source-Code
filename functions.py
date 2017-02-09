"""""
designed by Dandois for saving all the seperate small functions
#side functions as support

"""


#check if a file exists in a location
def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))


#find the required integrals on a curve; given the peaks
def fn_integrals(chunk_max, peaks_ind, chunk_noise):
	# use the indices to find the integral limits
	integral_limits = []
	for x in peaks_ind:
		y, z = x, x  # y for the left bound; z for the right
		#while (chunk_max[y] > 0.505630659713 * chunk_max[x] and y > 2 or chunk_max[y] > chunk_noise):
		while chunk_max[y] > chunk_noise*4:
			y = y - 1
		#while (chunk_max[z] > 0.4505630659713 * chunk_max[x] and z < len(chunk_max)-2 or chunk_max[z] > chunk_noise):
		while chunk_max[z] > chunk_noise*4:
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
				integral_limits[y][0] = min([integral_limits[x][0], integral_limits[y][0]])
				integral_limits[y][1] = max([integral_limits[x][1], integral_limits[y][1]])
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
		
	#correct for single dot integrals
	remove = []
	for x in range(len(peaks_ind)):
		if integral_limits[x][0] == integral_limits[x][1]:
			remove.append(x)
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
	return integral_limits, peaks_ind


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


#perform duplet and triplet filtering; also filter
def fn_integral_filter(chunk_param, duplet_ppm):
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

		#remove the water peak
		if abs(chunk_param["chunk_peak_ind_ppm"][x] - 4.7) < 0.02:
			remove.append(x)

		#remove the to low peaks
		if np.max(chunk_param["chunk_values"][x]) < 0.015:
			remove.append(x)


	#remove the data from the filtered out peaks
	remove = sorted(fn_unique(remove), reverse=True)
	for x in remove:
		chunk_param["chunk_values"] = np.delete(chunk_param["chunk_values"],x,axis=0)
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
		if np.max(chunk_param["chunk_values"]) < 0.02:
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
	#correlation = corrcoef(list, list2)[0][1]
	from scipy.stats import pearsonr
	correlation = pearsonr(list,list2)[1]
	return correlation


#calculate the SSD
def fn_SSD (listA, listB=[]):
	import numpy as np
	if listB == []:
		for x in range(len(listA)):
			listB.append(0.)
	data = np.array(listA) - np.array(listB)
	result = np.sum(np.abs((np.mean(data)-data)))
	return result


#calculate the rico between the first and last point
def fn_rico (list, vclist):
	return (list[len(list)-1] - list[0])/(len(vclist))


#filter to be applied on peak index and chunk_max BEFORE INTEGRATION
def fn_noise_filter(chunk_peak_ind, chunk_max):
	import numpy as np
	max = np.max(chunk_max)
	noise_list = []
	for x in chunk_peak_ind:
		if chunk_max[x] < 0.005:
			noise_list.append(chunk_max[x])
			noise_list.append(-chunk_max[x])
	limit = np.std(noise_list)*3
	temp = []
	for x in chunk_peak_ind:
		if chunk_max[x] > limit:
			temp.append(x)
	return temp, limit


#function for reading the title file
def fn_read_title(dir):
	if fn_check_dir(dir, "title"):
		title_line = open(dir + r"\title", 'r').readlines()[0]
		if (title_line.find("-") != -1):
			sample_name = title_line[:(title_line.find("-") -1)]
			extra_info = title_line[(title_line.find("-") +2):]
			if "µ" in extra_info:
				x = 1
				temp_order = []
				while len(title_line) != (title_line.find("µ")+x) and title_line[title_line.find("µ")+x] not in [" ", "-"]:
					temp_order.append(title_line[title_line.find("µ")+x])
					x +=1
				order = []
				for x in temp_order:
					order.append({"1": "a-%spyr.", "2": "b-%spyr.", "3": "a-%sfur.", "4": "b-%sfur."}[x] %sample_name[:sample_name.find("ose")+1])

			else:
				order = []
		else:
			sample_name = title_line
			extra_info = ""
			order = []
	else:
		sample_name = "unknown"
		extra_info = "unknown"
		order = []
	return sample_name, extra_info, order


#calculate the significance of all functions
def fn_sign(chunk):
	import numpy as np
	sign = []
	for x in range(len(chunk["chunk_values"])):
		sign.append([x, np.trapz(chunk["chunk_values"][x])])
	sign.sort(key=lambda x: x[1],reverse=True)
	chunk["chunk_sign"] = sign
	return chunk

"""

def fn_compare_fn(x,y):
	import numpy as np
	zx = (x - np.mean(x)) / np.std(x, ddof=1)
	zy = (y - np.mean(y)) / np.std(y, ddof=1)
	r = np.sum(zx * zy) / (len(x) - 1)
	return r**2


def fn_compare_fn(x_list, y_list): #using rsquared
	import math
	n = len(x_list)
	x_bar = sum(x_list)/n
	y_bar = sum(y_list)/n
	x_std = math.sqrt(sum([(xi-x_bar)**2 for xi in x_list])/(n-1))
	y_std = math.sqrt(sum([(yi-y_bar)**2 for yi in y_list])/(n-1))
	zx = [(xi-x_bar)/x_std for xi in x_list]
	zy = [(yi-y_bar)/y_std for yi in y_list]
	r = sum(zxi*zyi for zxi, zyi in zip(zx, zy))/(n-1)
	if math.isnan(r**2):
		r=0.99
	return r**2
"""

#compare two functions - used for database reference search
def fn_compare_fn(curve1, curve2):
	import numpy as np
	import math
	#here you can play with the diff types of correlations
	corr = np.trapz(abs(np.array(curve1) - np.array(curve2)))/max(abs(np.trapz(curve1)), abs(np.trapz(curve2)))
	if math.isnan(corr):
		corr = 0.0
	if corr > 1.0:
		corr = 1.0
	return 1.0-corr



####################################################################################################"
def fn_vclist(dir):
	vclist = []
	if (fn_check_dir(dir[:dir.find('pdata')], r'\vclist')):
		vclist_file = open(dir[:dir.find('pdata')] + r'\vclist', 'r').readlines()
		for x in vclist_file:
			vclist.append(int(x))
	return vclist

def fn_fqlist(dir, B0_hz):
	fqlist = []
	fqlist_ppm = []
	if (fn_check_dir(dir[:dir.find('pdata')], r'\fq0list')):
		fqlist_file = open(dir[:dir.find('pdata')] + r'\fq0list', 'r').readlines()
		for x in range(len(fqlist_file)):
			if x != 0:
				fqlist.append(float(fqlist_file[x]))
				fqlist_ppm.append(float(fqlist_file[x]) / B0_hz)
	return fqlist, fqlist_ppm

def fn_parameters(dic, dic2, dic3):
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	# SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
	SW_hz = float(dic['procs']['SW_p'])
	SW_ppm = SW_hz / B0_hz
	duplet_ppm = 15 / B0_hz  # from Karplus
	chunk_num = int(int(dic3[dic3.find(r'$TD=') + 5:dic3.find(r'$TD=') + 7]) / 13)
	return B0_hz, SW_ppm, SW_hz, duplet_ppm, chunk_num

def fn_max_curve(chunk):
	import numpy as np
	chunk_max = []
	for x in np.array(chunk).T:
		chunk_max.append(np.max(x))
	return chunk_max
	
#make an unique version of a list
def fn_unique(list):
	unique = []
	[unique.append(item) for item in list if item not in unique]
	return unique
	

#calculate the integration curves
def fn_integrate_new(chunk, chunk_integrals, chunk_peak_ind, SW_ppm):
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
	
	#filter out the bad ones
	remove = []
	for x in range(len(chunk_peak_ind)):
		#different filter conditions
		if np.max(chunk_values[x]) < 0.015:
			remove.append(x)
			
			
			
	remove = sorted(fn_unique(remove), reverse=True)
	for x in remove:
		chunk_values = np.delete(chunk_values,x,axis=0)
		chunk_integrals.pop(x)
		chunk_peak_ind.pop(x)
		chunk_peak_ind_ppm.pop(x)
	return chunk_values, chunk_integrals, chunk_peak_ind, chunk_peak_ind_ppm

#find the subplot number
def fn_calc_plots (list):
	number = len(list)
	dict = {"1": 111, "2": 211, "3":311, "4":221,"5":321,"6":321,"7":331,"8":331,"9":331}
	if number > 9:
		return "error"
	else:
		return dict[str(number)]