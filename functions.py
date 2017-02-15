"""""
designed by Dandois for saving all the seperate small functions
#side functions as support

"""

# find the required integrals on a curve; given the peaks
def fn_integrals(chunk_max, peaks_ind, chunk_noise):
	# use the indices to find the integral limits
	integral_limits = []
	for x in peaks_ind:
		y, z = x, x  # y for the left bound; z for the right
		# while (chunk_max[y] > 0.505630659713 * chunk_max[x] and y > 2 or chunk_max[y] > chunk_noise):
		while chunk_max[y] > chunk_noise * 4:
			y = y - 1
		# while (chunk_max[z] > 0.4505630659713 * chunk_max[x] and z < len(chunk_max)-2 or chunk_max[z] > chunk_noise):
		while chunk_max[z] > chunk_noise * 4:
			z = z + 1
		integral_limits.append([y, z])

	# correct for identical integrals
	remove = []
	for x in range(len(peaks_ind) - 1):
		if integral_limits[x] == integral_limits[x + 1]:
			remove.append(x + 1)
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

	# correct for single dot integrals
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
	chunk_num = int(int(dic3[dic3.find(r'$TD=')+5:][:dic3[dic3.find(r'$TD=')+5:].find("\n")])/13)
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

def fn_compare_curves(list1, list2): #NOT OPTIMAL AT ALL - ASK DAWYNDT
	from copy import deepcopy
	from numpy import trapz
	list1_c = deepcopy(list1)
	list2_c = deepcopy(list2)
	CCF = 1.
	#sort list1 on importance
	list1_c.sort(key=lambda x: x.size,reverse=True)
	# find best comparable curve and save the data
	for x in range(min(len(list1_c), len(list2_c))):
		curve1 = list1_c[x]
		best = 0
		best_curve = 0.
		for curve2 in list2_c:
			temp = curve1.fn_compare(curve2)
			if temp > best:
				best = temp
				best_curve = curve2
		if best_curve != 0.:
			list2_c.remove(best_curve)
			CCF *= best
	list1_c = list1_c[min(len(list1), len(list2))+1:]
	# punish for the remaining curves
	tot = 1
	for x in list1_c + list2_c:
		tot += trapz(x.data)
	return CCF/tot


#file checker
def fn_check_dir(dir,file):
	import os.path
	return (os.path.isfile(dir + '\\' + file))

#folder checker
def fn_check_folders(dir):
	from glob import glob
	#reform the end of dir
	if "\\" in dir:
		dir = dir.replace("\\", "/")
	if dir[len(dir)-1] != "/":
		dir += "/"
	temp_list = glob(dir+"*/")
	dir_list = []
	for x in temp_list:
		if x[len(x)-2] == "2" and fn_check_dir(x+"pdata\\1","2ii") and fn_check_dir(x+"pdata\\1","2rr"):
			dir_list.append(x)
		if x[len(x) - 2] == "3" and fn_check_dir(x + "pdata\\1", "2ii") and fn_check_dir(x + "pdata\\1", "2rr"):
			#if a 3 is present; use the 3 instead of the 2
			dir_list.append(x)
			dir_list.remove(x[:len(x) - 2]+"2"+x[len(x) - 1:])
	return dir_list

def fn_progress_gen(num):
	string = format("Compiling database - %s%s" % (str(num * 100), r"%"))
	return string

# get the settings from the config
def fn_settings():
	Settings = {}
	import config
	Settings["Experiment_Directory"] = config.Experiment_Directory
	Settings["Database_Directory"] = config.Database_Directory

	Settings["plot_exp"] = config.plot_exp
	Settings["plot_chunk"] = config.plot_chunk
	Settings["plot_values"] = config.plot_values

	Settings["am_norm"] = config.am_norm

	Settings["gp_chunks"] = config.gp_chunks
	Settings["gp_print"] = config.gp_print

	#GUI settings - not in config
	Settings["Background"] = "blue"
	Settings["Foreground"] = "white"
	Settings["GUI_width"] = 9	#9 is the minimum!!!
	return Settings