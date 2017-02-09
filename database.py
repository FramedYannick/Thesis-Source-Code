"""""
designed by Dandois for all database interactions

"""

def fn_compile(dir, printlabel="testing"):
	from GUI_mainframe import update_GUI
	from glob import glob
	import Read_data as rd
	import pickle
	from config import Database_Directory

	#check if database exist and prompt user
	from functions import fn_check_dir
	if fn_check_dir(Database_Directory, "Database.p"):
		import tkinter.messagebox as mg
		if printlabel == "testing":
			import tkinter as tk
			crap = tk.Tk()
			crap.withdraw()
		override = mg.askyesno("Delete", "Override current database?\nIf you are missing items the database will not be complete.")
		if not override:
			update_GUI("Not performing database compilation.", printlabel)
			return

	#read in all present folders
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
	final_database = []
	progress = round(0.000000,1)
	for y in range(len(dir_list)):
		if round(y/len(dir_list),1) != progress:
			progress = round(y / len(dir_list), 1)
			update_GUI("Compiling database - %s%s" %(str(progress*100),r"%"),printlabel)
		#update_GUI(dir_list[y],"testing")
		#perform sugar analysis
		dict_param, data = rd.fn_read_data(dir_list[y]+"\\pdata\\1", "ignore")
		dict_param, data = rd.fn_reform(dict_param,data)
		dict_param, data = rd.fn_process_chunk(dict_param, data, "ignore")
		dict_param = rd.fn_process_curve(dict_param, data, "ignore")

		for x in dict_param["chunk_param"]:
			final_database.append(x)
	update_GUI("Compiling database - Finished", printlabel)
	# create the database dump file
	pickle.dump(final_database, open(Database_Directory + r"\Database.p", "wb"))

	#temporary add an extra txt file
	if str(printlabel) == "testing":
		file = open(Database_Directory + r"\Database.txt", "a")
		for x in final_database:
			file.write(str(x) + "\n")
	return

def fn_load():
	#load in the pre-existing database:
	from config import Database_Directory
	from pickle import load
	from functions import fn_check_dir
	if (fn_check_dir(Database_Directory, r"\Database.p")):
		database = load(open(Database_Directory + r"\Database.p","rb"))
	else:
		database = "no file"
	return database

#compare two chunks and give them a correlation coefficient
def fn_compare_chunk(chunk1, chunk2):
	import numpy as np
	#get the significance levels for the peaks
	from functions import fn_sign
	chunk1 = fn_sign(chunk1)

	from copy import deepcopy
	temp2 = deepcopy(chunk2["chunk_values"])
	CCF = 1#/(abs(len(chunk1["chunk_values"])-len(chunk2["chunk_values"]))+1)
	#find most fitting function for the most sign curve of chunk1
	from functions import fn_SSD
	for x in range(len(chunk1["chunk_sign"][:len(temp2)])):
		if chunk1["chunk_sign"][1] != 0.0:
			curve1 = chunk1["chunk_values"][chunk1["chunk_sign"][x][0]]
			alpha1 = chunk1["peak_info"][x]["alpha"]
			best = [0,0] #curve, SSD
			for y in range(len(temp2)):
				curve2 = temp2[y]
				alpha2 = chunk2["peak_info"][y]["alpha"]
				from functions import fn_compare_fn
				corr = fn_compare_fn(curve1, curve2)
				if corr > best[1]:
					best = [y,corr]
			np.delete(temp2, best[0], axis=0)
			CCF = CCF*(best[1])
	return (CCF)

def fn_compare_database(dict_param, database, printlabel):
	from GUI_mainframe import update_GUI
	if str(database) == "no file":
		#raise error or something
		update_GUI("no file present", printlabel)
	else:
		#run the code for each chunk with index X
		dict_results = []
		for x in range(len(dict_param["chunk_param"])):
			chunk_results = []
			#compare against each chunk in the database
			for y in range(len(database)):
				corr = fn_compare_chunk(dict_param["chunk_param"][x], database[y])
				chunk_results.append([database[y], corr])
			chunk_results.sort(key=lambda x: x[1],reverse=True)
			dict_results.append(chunk_results)
	return dict_results

