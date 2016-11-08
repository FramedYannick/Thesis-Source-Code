

#####################################################################gaussisan duplet filter determination
def func(list):
	import numpy as np
	import matplotlib.pyplot as plt
	total = []
	for y in list:
		mean = y[0]
		std = y[1]
		gaus = []
		for x in range(500):
			gaus.append(1/(np.sqrt(2*3.14*std**2))*np.exp(-(x-mean)**2/(2*std**2)))
			if x == (mean+std):
				print(gaus[len(gaus)-1]/max(gaus))
		#gaus = gaus/np.trapz(gaus)
		if total == []:
			total = np.array(gaus)
		else:
			total = np.add(total,gaus)
	return (total)


import numpy as np
import matplotlib.pyplot as plt

std = 50
mini = []
dist = []
for x in range(50,250,5):
	array = func([[50,std],[50+x,std]])
	a = min(array[50:50+x])/0.008
	mini.append(a)
	a = x/std
	dist.append(a)
	plt.plot(array)

plt.show()
print(mini)
print(dist)



"""
#test for linearity of the dimple - not working for extrapollation
def func(x,a,b):
	return x*a+b

from scipy.optimize import curve_fit
popt,pcov = curve_fit(func,dist,mini)

print("\n\n\n" + str(popt))
print(str(pcov) + "\n\n\n")

for x in range(len(mini)):
	print(str(dist[x])+","+str(mini[x]))
"""