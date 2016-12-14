"""""
designed by Dandois to contain all plotting functions

"""


#find the subplot number
def fn_calc_plots (list):
	number = len(list)
	dict = {"1": 111, "2": 211, "3":311, "4":221,"5":321,"6":321,"7":331,"8":331,"9":331}
	if number > 9:
		return "error"
	else:
		return dict[str(number)]


#show the curves for integral limits
def fn_plot_integrals(dict_param, data):
	import matplotlib.pyplot as plt
	num = fn_calc_plots(data)
	a = plt.figure(1)
	for y in range(len(data)): #loop per chunk
		ax = plt.subplot(num+y) #new subplot
		if len(dict_param["order"]) == 0:
			ax.set_title("%s - chunk %s" %(dict_param["sample_name"], str(y+1)))
		else:
			ax.set_title(dict_param["chunk_param"][y]["sample_name"])
		for x in range(len(data[y])):
			plt.plot(data[y][x], label=x)
		integral= []
		for q in range(len(data[0][0])):
			integral.append(0)
		for inte in dict_param["chunk_param"][y]["chunk_integrals"]:
			x1,x2 = inte[0], inte[1]
			for val in range(x2-x1):
				integral[x1+val] = 1
		plt.plot(integral,label="integral")
		#plt.legend()
	plt.show()
	return


#show the curves that must be compared to the database - chunk_param; order and mtlist must be set in the dict_param
def fn_plot_curves(dict_param):
	import matplotlib.pyplot as plt
	num = fn_calc_plots(dict_param["chunk_param"])
	for z in range(len(dict_param["chunk_param"])):
		x = dict_param["chunk_param"][z]
		ax = plt.subplot(num+z)
		if len(dict_param["order"]) == 0:
			ax.set_title("%s - chunk %s" %(dict_param["sample_name"], str(z+1)))
		else:
			ax.set_title(x["sample_name"])
		for y in range(len(x["chunk_values"])):
			plt.plot(dict_param["mtlist"], x["chunk_values"][y], label=x["chunk_peak_ind_ppm"][y])
	plt.show()
	return


#show multiple chunks to be compaired against eachother - should be a list of chunk_param
def fn_plot_chunks(chunk_list, mtlist=[0.00863415, 0.0172683, 0.02590245, 0.0345366, 0.04317075, 0.0518049, 0.06043905, 0.0690732, 0.07770735000000001, 0.0863415, 0.09497565, 0.1036098, 0.11224395000000001]):
	import matplotlib.pyplot as plt
	num = fn_calc_plots(chunk_list)
	for z in range(len(chunk_list)):
		x = chunk_list[z]
		ax = plt.subplot(num+z)
		ax.set_title(x["sample_name"])
		for y in range(len(x["chunk_values"])):
			plt.plot(mtlist, x["chunk_values"][y], label=(x["sample_name"][y] + " " + str(x["chunk_peak_ind_ppm"][y])))
	plt.show()
	return