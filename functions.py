"""""
designed by Dandois for saving all the seperate small functions
#side functions as support

"""

# find the required integrals on a curve; given the peaks
def fn_integrals(chunk_max, Settings):
	import numpy as np
	from detect_peaks import detect_peaks
	# remove super low peaks (background noise)
	peaks_ind, chunk_noise = fn_noise_filter(detect_peaks(chunk_max, show=False), chunk_max)

	# find the limits
	integral_limits = []
	for x in peaks_ind:
		# original
		# use the indices to find the integral limits
		y, z = x, x  # y for the left bound; z for the right
		# while (chunk_max[y] > 0.505630659713 * chunk_max[x] and y > 2 or chunk_max[y] > chunk_noise):
		while chunk_max[y] > chunk_noise * 4:
			y = y - 1
		# while (chunk_max[z] > 0.4505630659713 * chunk_max[x] and z < len(chunk_max)-2 or chunk_max[z] > chunk_noise):
		while chunk_max[z] > chunk_noise * 4:
			z = z + 1
		integral_limits.append([y,z])

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

	# correct for single dot integrals
	for x in range(len(peaks_ind)):
		if integral_limits[x][0] == integral_limits[x][1]:
			remove.append(x)

	# remove them
	unique = []
	[unique.append(item) for item in remove if item not in unique]
	remove = sorted(unique, reverse=True)
	for x in remove:
		peaks_ind.pop(x)
		integral_limits.pop(x)

	# split them up
	if Settings["gp_splitter"] != 0. and Settings["gp_duplet_filtering"]:
		new_integral_limits = []
		new_peaks_ind = []
		for counter in range(len(integral_limits)):
			temp = integral_limits[counter]
			temp_indices_rev = np.array(detect_peaks(chunk_max[temp[0]:temp[1]], show=False, valley=True)) + temp[0]
			if temp[0] < 3250 < temp[1]:
				import matplotlib.pyplot as plt
			for y in temp_indices_rev:
				if chunk_max[y] < Settings["gp_splitter"] * chunk_max[peaks_ind[counter]]:
					new_integral_limits.append([temp[0], y])
					new_peaks_ind.append((temp[0] + y) / 2)
					temp[0] = y
			# find the index of the closest number to the x
			new_integral_limits.append(temp)
			new_peaks_ind.append((temp[0] + temp[1]) / 2)
		integral_limits = new_integral_limits
		peaks_ind = new_peaks_ind

	return integral_limits, peaks_ind, chunk_noise


#calculate the rico between the first and last point
def fn_rico (list, vclist):
	return (list[len(list)-1] - list[0])/(len(vclist))


#filter to be applied on peak index and chunk_max BEFORE INTEGRATION
def fn_noise_filter(chunk_peak_ind, chunk_max, factor=1):
	import numpy as np
	max = np.max(chunk_max)
	chunk_max = np.array(chunk_max) / max
	noise_list = []
	for x in chunk_peak_ind:
		if chunk_max[x] < 0.005:
			noise_list.append(chunk_max[x])
			noise_list.append(-chunk_max[x])
	limit = np.std(noise_list)*1*factor
	temp = []
	for x in chunk_peak_ind:
		if chunk_max[x] > limit:
			temp.append(x)
	return temp, limit*max

#alternate integral way
def fn_alt_integrals(max_curve):
	import numpy as np
	limit = np.mean(max_curve)
	temp_01, new_limit, x = [], [0,0], 0
	integral_limits, peaks_ind = [],[]
	while x < len(max_curve):
		while len(max_curve) < x and max_curve[x] < limit:
			x +=1
		new_limit[0] = x
		while len(max_curve) < x and max_curve[x] >= limit:
			x +=1
		new_limit[1] = x
		if len(max_curve) < x:
			integral_limits.append(new_limit)
			peaks_ind.append(np.mean(new_limit))
	return integral_limits, peaks_ind, limit

def fn_product(list):
	x = 1
	for y in list:
		x = x*y
	return x


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

def fn_parameters(dic, dic2, dic3, pp):
	B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
	B0_hz = round(B0_hz, 2)
	SW_hz = float(dic['procs']['SW_p'])
	SW2_hz = float(dic3[dic3.find(r'$SW_h=')+ 7 :][:dic3[dic3.find(r'$SW_h=')+7:].find("\n")])
	SW_ppm = SW_hz / B0_hz
	duplet_ppm = 0.1
	off = ((dic["procs"]["SF"]-B0_hz)*10**6)/B0_hz
	chunk_num = int(int(dic3[dic3.find(r'$TD=')+5:][:dic3[dic3.find(r'$TD=')+5:].find("\n")])/13)
	if pp == "dipsigpphzsbs":
		SW2_ppm = SW2_hz / B0_hz
		return B0_hz, SW_ppm, SW2_ppm, SW_hz, duplet_ppm, chunk_num, off
	else:
		return B0_hz, SW_ppm, SW_hz, duplet_ppm, chunk_num, off

def fn_max_curve(chunk):
	import numpy as np
	chunk_max = []
	for x in np.array(chunk).T:
		chunk_max.append(np.max(x))
	return chunk_max

def fn_sum_curve(chunk):
	import numpy as np
	data = np.array(chunk[0])
	for x in chunk[1:]:
		data += (np.array(x))
	data = data/max(data)
	return data
	
#make an unique version of a list
def fn_unique(list):
	unique = []
	[unique.append(item) for item in list if item not in unique]
	return unique
	

#calculate the integration curves
def fn_integrate(chunk, chunk_integrals, chunk_peak_ind, SW_ppm, SO1, pp):
	import numpy as np
	chunk_values = []
	for y in range(len(chunk_peak_ind)):  # loop over all indices
		x = chunk_peak_ind[y]
		#chunk_peak_ind_ppm.append((len(chunk[0]) - x) / len(chunk[0]) * SW_ppm + SO1 -0.5*SW_ppm)
		temp = []
		for row in chunk:
			temp.append(np.trapz(row[chunk_integrals[y][0]:chunk_integrals[y][1]]))
		chunk_values.append(temp)
	
	#filter out the bad ones
	remove = []
	for x in range(len(chunk_peak_ind)):
		# different filter conditions
		if np.max(chunk_values[x]) < 0.01:
			remove.append(x)

	remove = sorted(fn_unique(remove), reverse=True)
	for x in remove:
		chunk_values = np.delete(chunk_values,x,axis=0)
		chunk_integrals.pop(x)
		chunk_peak_ind.pop(x)
	return chunk_values, chunk_integrals, chunk_peak_ind

#find the subplot number
def fn_calc_plots (list):
	number = len(list)
	dict = {"1": 111, "2": 211, "3":311, "4":221,"5":321,"6":321,"7":331,"8":331,"9":331}
	if number > 9:
		return "error"
	else:
		return dict[str(number)]

def euc_dist(pt1,pt2):
	import math
	return math.sqrt((pt2[0]-pt1[0])*(pt2[0]-pt1[0])+(pt2[1]-pt1[1])*(pt2[1]-pt1[1]))

def fn_frechet(list1, list2, mtlist):
	res = 0.
	for x in range(len(list1)):
		val = 100.
		for y in range(x,len(list2)):
			dist = euc_dist([list1[x],mtlist[x]], [list2[y], mtlist[y]])
			if dist < val:
				val = dist
		if val > res:
			res = val
	if res == 0.:
		res = 0.000000000001
	return res*2#/max(list1+list2)

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

def fn_result_printer(result, gp_print):
	text = "Results:\n-----------------------------------"
	for x in result: #for each chunk
		for y in range(min(gp_print, len(x[1]))): #for each result in chunk
			text = text + "\n" + str(x[0]) + ": " + str(round(x[1][y][0],3)) + format("  %s" %x[1][y][1].sample_name)
		text += "\n-----------------------------------"
	return text

#convert the dendrogram to the newick format for iTOL
def getNewick(node, newick, parentdist, leaf_names):
	if node.is_leaf():
		return "%s:%.2f%s" % (leaf_names[node.id], parentdist - node.dist, newick)
	else:
		if len(newick) > 0:
			newick = "):%.2f%s" % (parentdist - node.dist, newick)
		else:
			newick = ");"
		newick = getNewick(node.get_left(), newick, node.dist, leaf_names)
		newick = getNewick(node.get_right(), ",%s" % (newick), node.dist, leaf_names)
		newick = "(%s" % (newick)
		return newick

#perform cluster analysis on a given database
def fn_cluster_analysis(data):
	data.fn_compile()
	title = []
	matrix = []
	for z in range(len(data.content)):
		x = data.content[z]
		comp = x.fn_compare(data, False)
		temp = []
		for q in range(len(comp)):
			y = comp[q]
			temp.append(y[0])
			if (0.99 > y[0] > 0.7) and z < q and True:
				print(y[0])
				x.fn_plot(y[1], r"$\delta$: " + str(round(y[0],2)), format("C:/Users/yannick/Documents/_Documenten/UGent/Thesis/Statistics/Cluster analysis/Frechet/%s.png" %(x.sample_name.replace(".","") +" - " + y[1].sample_name.replace(".",""))))
			if z != q and y[0] == 1.0:
				raise ValueError('PAAADUUUUUMMMmmmmm TSSSSsssss... This is a boeboe.')
		matrix.append(temp)
		title.append(x.sample_name)
	print(title)
	#symitrize the matrix
	for x in range(len(matrix)):
		for y in range(len(matrix[0])):
			matrix[x][y] = (matrix[x][y] + matrix[y][x]) / 2
			matrix[y][x] = matrix[x][y]
	#print the entire matrix
	for x in matrix:
		print(x)
	import numpy as np, matplotlib.pyplot as plt, scipy.cluster.hierarchy as hca

	a = hca.linkage(matrix, "average")
	plt.figure()
	b = hca.dendrogram(a, leaf_font_size=15., labels=title, orientation='left')
	plt.show()
	tree = hca.to_tree(a, False)
	res = getNewick(tree, "", tree.dist, title)
	print(res)
	for x in matrix:
		for y in x:
			print(y)
	return matrix

def fn_p3d_reform(data):
	data_new = []
	for x in range(13):
		data_new.append([])
		for x in range(len(data)):
			data_new[len(data_new) - 1].append([])
	for f1 in range(len(data)):
		for f2 in range(13):
			f3 = data[f1][f2]
			data_new[f2][f1] = f3
	return data_new

# takes the diagonal from a 2d TOCSY
def fn_p3d_diagonal(data, SW_ppm, SW2_ppm, SO1_ppm):
	diag = []
	len1 = len(data[0])
	len2 = len(data)
	for x in range(len(data)):
		temp_ppm = (len2 - x) / len2 * SW2_ppm + SO1_ppm - 0.5 * SW2_ppm
		diag.append(data[x][int((SO1_ppm - temp_ppm - 0.5 * SW_ppm) / SW_ppm * len1 + len1)])
	import matplotlib.pyplot as plt
	"""
	plt.figure()
	ax = plt.subplot()
	plt.plot(diag)
	ax.set_ylabel("Intensity (rel.)")
	ax.set_xlabel("Data point")
	plt.show()
	"""
	return diag

def ppm_from_index(index, SO1_ppm, SW_ppm, res):
	return (res - index) / res * SW_ppm + SO1_ppm - 0.5 * SW_ppm

def index_from_ppm(ppm, SO1_ppm, SW_ppm, res):
	return int((SO1_ppm - ppm - 0.5 * SW_ppm) / SW_ppm * res + res)

# get the settings from the config
def fn_settings():
	Settings = {}
	import config
	Settings["Experiment_Directory"] = config.Experiment_Directory
	Settings["Database_Directory"] = config.Database_Directory

	Settings["plot_exp"] = config.plot_exp
	Settings["plot_chunk"] = config.plot_chunk
	Settings["plot_values"] = config.plot_values
	Settings["plot_diagonal"] = config.plot_diagonal
	Settings["plot_integration"] = config.plot_integration

	Settings["am_norm"] = config.am_norm
	Settings["am_min"] = config.am_min

	Settings["gp_chunks"] = config.gp_chunks
	Settings["gp_chunks_list"] = []
	Settings["gp_print"] = config.gp_print
	Settings["gp_threshold"] = config.gp_threshold
	Settings["gp_splitter"] = config.gp_splitter
	Settings["gp_duplet_filtering"] = config.gp_duplet_filtering

	#GUI settings - not in config
	Settings["Background"] = "blue"
	Settings["Foreground"] = "white"
	Settings["GUI_width"] = 9	#9 is the minimum!!!
	return Settings

