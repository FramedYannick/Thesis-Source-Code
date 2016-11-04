"""
Designed by Dandois for a Database comparison around the python processing module

"""


def droptype(sugar, vclist=[100]):
	return(sugar['curve']['drop'])

def duplet(sugar):
	return sugar['duplet']

def find_LCC (x, a, b):
	return x


#####################################################################################

def Check_database(info_sugar, vclist):
	import numpy as np
	import matplotlib.pyplot as plt

	#load in the pre-existing database:
	from config import Database_Directory
	from pickle import load
	database = load( open(Database_Directory + r"\Database.p","rb"))

	# H1 filtering
	sugar_listh1 = []     #container for the possible sugars per H1
	for h1_peak in info_sugar[1]:   #execute for all H1's
		sugar_listh1.append([])
		for x in database:
			if abs(droptype(h1_peak) - droptype(x[1][0])) < 0.15 and (duplet(h1_peak) == duplet(x[1][0])):
				sugar_listh1[-1].append(x)

	#comparison for the other peaks with the H1 filtered decays
	for h_peak in info_sugar[2]:
		a = 1



	#print out all poss sugars for now
	for x in sugar_listh1:
		for y in x:
			print(y)
	print(vclist)