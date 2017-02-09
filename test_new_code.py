
from Read_data import *
from plotter import *
import database as db
import matplotlib.pyplot as plt

import numpy as np
np.seterr(all="ignore")


#for testing purpoces
if False:
	#find the best sugar for each sugar in db
	final = db.fn_load()
	for x in range(len(final)):
		best = ["name", 0]
		for y in range(len(final)):
			corr = db.fn_compare_chunk(final[x], final[y])
			if (corr > best[1]):
				best = [final[y]["sample_name"],corr]
		print(final[x]["sample_name"], best)
elif False:
	#give all CCF between al sugars
	final = db.fn_load()
	for x in range(len(final)):
		best = ["name", 0]
		for y in range(x,len(final)):
			corr = db.fn_compare_chunk(final[x], final[y])
			#if corr > 0.3 and corr != 1.0:
			print(final[x]["sample_name"], final[y]["sample_name"], corr)
elif False: #compile the entire database
	from config import Database_Directory
	db.fn_compile(Database_Directory, printlabel="testing")
elif False: #compare 2 or more sugars
	database = db.fn_load()
	a = []
	for x in database:
		if "a-Glucopyr" in x["sample_name"] or "a-Lyxopyr" in x["sample_name"]:
			a.append(x)
	for x in range(len(a)-1):
		for y in range(x+1,len(a)):
			corr = db.fn_compare_chunk(a[x], a[y])
			print(a[x]["sample_name"], a[y]["sample_name"], corr)

	from plotter import fn_plot_chunks, fn_plot_chunks_OG
	fn_plot_chunks(a)
	fn_plot_chunks_OG(a)
elif False: #normal script executed instead of function for debug
	printlabel = "testing"

	# should end up in code
	#dict_param, data = fn_read_data(r"D:\DATA\master2016\DATABASE\93\pdata\1", printlabel)
	dict_param, data = fn_read_data(r"D:\DATA\master2016\SAMPLES\22\pdata\1",printlabel)

	dict_param, data = fn_reform(dict_param, data)
	dict_param, data = fn_process_chunk(dict_param, data, printlabel)
	dict_param = fn_process_curve(dict_param, data, printlabel)

	fn_plot_integrals(dict_param,data)

	database = db.fn_load()
	result = db.fn_compare_database(dict_param, database, printlabel)
	for x in range(len(result)):
		print("%s identified as %s with a factor of %f" % (dict_param["chunk_param"][x]["sample_name"], result[x][0][0]["sample_name"], result[x][0][1]))

elif False:
	printlabel = "testing"
	fn_main_function(r"D:\DATA\master2016\SAMPLES\6\pdata\1",printlabel)
	#fn_main_function(r"D:\DATA\master2016\DATABASE\23\pdata\1", printlabel)