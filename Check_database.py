"""
Designed by Dandois for a Database comparison around the python processing module

"""


def droptype(sugar, vclist=[100]):
	return(sugar['curve']['drop'])

def duplet(sugar):
	return sugar['duplet']

def find_LCC (x, a, b, c, d):
	#find the current list in the temp file
	import os
	cwd = os.getcwd()
	dir = cwd + r"\temp.p"
	from pickle import load
	arrays = load( open(dir,"rb"))
	os.remove(dir)
	return x

def write_LCC (arrays):
	import os
	cwd = os.getcwd()
	dir = cwd + r"\temp.p"
	from pickle import dump
	dump(arrays, open(dir, "wb"))


#####################################################################################

def Check_database(info_sugar, vclist):
	import numpy as np
	import matplotlib.pyplot as plt

	#load in the pre-existing database:
	from config import Database_Directory
	from pickle import load
	database = load(open(Database_Directory + r"\Database.p","rb"))

	# H1 filtering
	sugar_listh1 = []     #container for the possible sugars per H1
	for h1_peak in info_sugar[1]:   #execute for all H1's
		sugar_listh1.append([])
		for x in database:
			PCC = np.corrcoef(h1_peak['data'],x[1][0]['data'])[0][1]
			#if abs(droptype(h1_peak) - droptype(x[1][0])) < 0.15 and (duplet(h1_peak) == duplet(x[1][0])):
			if PCC > 0.9:
				x[1][0]['PCC_H1'] = PCC
				sugar_listh1[-1].append(x)
				print(PCC)

	#comparison for the other peaks with the H1 filtered decays
	#find most significant peaks
	info_sugar[2] = sorted(info_sugar[2], key=lambda x: x['integral'],reverse=True)
	for list in sugar_listh1:
		list = sorted(list, key=lambda x: x[1][0]['PCC_H1'],reverse=True)




	#print out all poss sugars for now
	for x in sugar_listh1:
		for y in x:
			print(y)



