def find_LCC (x, a, b, c, d):
	#find the current list in the temp file
	import os
	cwd = os.getcwd()
	dir = cwd + r"\temp.p"
	from pickle import load
	arrays = load( open(dir,"rb"))
	return x

def write_LCC (arrays):
	import os
	cwd = os.getcwd()
	dir = cwd + r"\temp.p"
	from pickle import dump
	dump(arrays, open(dir, "wb"))

array = [[1,5,3,6],[4,5,89,5,9,5],[5,9,8,9,8]]
write_LCC(array)
