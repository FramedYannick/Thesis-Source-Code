"""
Designed by Dandois for a Database comparison around the python processing module

"""


def droptype(sugar, vclist=[100]):
		return(sugar['curve']['drop'])

def find_LCCC (x, a, b):
	return x


#####################################################################################

def Check_database(info_sugar,vclist):
	import numpy as np
	import matplotlib.pyplot as plt

	#load in the pre-existing database:
	from config import Database_Directory
	from pickle import load
	database = load( open(Database_Directory + r"\Database.p","rb"))

	# H1 filtering
	sugar_list = []     #container for the possible sugars
	for h1_peak in info_sugar[1]:   #execute for all H1's
		sugar_list.append([])
		drop_sugar = droptype(h1_peak)
		for x in database:
			if abs(drop_sugar - droptype(x[1][0])) < 0.15:
				sugar_list[-1].append(x)

	#comparison for the other peaks with the H1 filtered decays
	for h_peak in info_sugar[2]:
		a = 1





	print(sugar_list)

	print(vclist)