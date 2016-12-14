
from Read_data import *
from plotter import *
import database as db
import matplotlib.pyplot as plt

import numpy as np
np.seterr(all="ignore")


#for testing purpoces
if False:
	#run function for testing purpoce
	final = db.fn_load()
	for x in range(len(final)):
		best = ["name", 0]
		for y in range(len(final)):
			corr = db.fn_compare_chunk(final[x], final[y])
			if (corr > best[1]):
				best = [final[y]["sample_name"],corr]
		print(final[x]["sample_name"], best)

elif False: #compile the entire database
	from config import Database_Directory
	db.fn_compile(Database_Directory, printlabel="testing")
elif False: #compare xylose and glucose
	database = db.fn_load()
	a = []
	for x in database:
		if "b-Gluc" in x["sample_name"] or "b-Xyl" in x["sample_name"]:
			a.append(x)
	from plotter import fn_plot_chunks
	fn_plot_chunks(a)
	import matplotlib.pyplot as plt
	plt.figure()
	for x in range(len(a)):
		for y in a[x]["chunk_values"]:
			plt.plot(y,["r-","g-","b-","o-"][x],label=a[x]["sample_name"])
	plt.legend()
	plt.show()
elif False: #normal script executed instead of function for debug
	printlabel = "testing"

	# should end up in code
	dict_param, data = fn_read_data(r"D:\DATA\master2016\DATABASE\93\pdata\1", printlabel)
	#dict_param, data = fn_read_data(r"D:\DATA\master2016\SAMPLES\22\pdata\1",printlabel)

	dict_param, data = fn_reform(dict_param, data)
	dict_param, data = fn_process_chunk(dict_param, data, printlabel)
	dict_param = fn_process_curve(dict_param, data, printlabel)

	fn_plot_integrals(dict_param,data)

	database = db.fn_load()
	result = db.fn_compare_database(dict_param, database, printlabel)
	for x in range(len(result)):
		print("%s identified as %s with a factor of %f" % (dict_param["chunk_param"][x]["sample_name"], result[x][0]["sample_name"], result[x][1]))

elif True:
	printlabel = "testing"
	fn_main_function(r"D:\DATA\master2016\SAMPLES\32\pdata\1",printlabel)
	#fn_main_function(r"D:\DATA\master2016\DATABASE\93\pdata\1", printlabel)