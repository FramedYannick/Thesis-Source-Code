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

	# create the database dump file
	pickle.dump(final_database, open(Database_Directory + r"\Database.p", "wb"))

	#temporary add an extra txt file
	if str(printlabel) == "testing":
		file = open(Database_Directory + r"\Database.txt", "a")
		for x in final_database:
			file.write(str(x) + "\n")
	return

def fn_load(printlabel):
	#load in the pre-existing database:
	from config import Database_Directory
	from pickle import load
	database = load(open(Database_Directory + r"\Database.p","rb"))
	return database

#run function for testing purpoce
from config import Database_Directory
fn_compile(Database_Directory)
