
#temp test file for optimal peak picking algorithm

import nmrglue as ng
import numpy as np
import matplotlib.pyplot as plt
import config
from detect_peaks import detect_peaks


dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\Test_500\2\pdata\1")

if len(data) > 10:
	data = data[9]
else:
	data = data[len(data)]

data = data/np.max(data)
print(data)

vthres = 0.01
hthres = 2

"""
#cheating with the zero!!!
for x in range(len(data)):
	if data[x] < vthres:
		data[x] = 0
"""


##########################################################################################
from scipy.signal import find_peaks_cwt
ind = find_peaks_cwt(data,np.arange(1,15))

ind_temp = []
for x in ind:
	if data[x] > vthres:
		ind_temp.append(x)
ind = ind_temp

print(str(len(ind)) + " " + str(ind))
##########################################################################################
from peakdetect import peakdetect
ind2 = peakdetect(data, lookahead=100)

ind2 = ind2[0]
for x in range(len(ind2)):
	ind2[x] = ind2[x][0]
ind_temp = []
for x in ind2:
	if data[x] > vthres:
		ind_temp.append(x)
ind2 = ind_temp



print(str(len(ind2)) + " " + str(ind2))
##########################################################################################
from detect_peaks import detect_peaks
ind3 = detect_peaks(data, mph=vthres)


print(str(len(ind3)) + " " + str(ind3))
##########################################################################################
import peakutils
ind4 = peakutils.indexes(data,thres=0.)
print(str(len(ind4)) + " " + str(ind4))
ind_temp = []
for x in ind4:
	if data[x] > vthres:
		ind_temp.append(x)
ind4 = ind_temp


print(str(len(ind4)) + " " + str(ind4))











indexes_names = ["scipy", "peakdetect", "detect_peaks", "peakutils"]
indexes_values = [ind,ind2,ind3,ind4]

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
colors = ['ro', 'bo', 'go', 'co', 'mo', 'yo', 'ko', 'r^', 'b^', 'g^', 'c^', 'm^', 'y^', 'k^', 'r*', 'b*', 'g*', 'c*',
          'm*', 'y*', 'k*', 'rd', 'bd', 'gd', 'cd', 'md', 'yd', 'kd', 'rD', 'bD', 'gD', 'cD', 'mD', 'yD', 'kD', ]
ax.plot(data, 'b-')
for y in range(len(indexes_names)):
	ydata = []
	for x in range(len(indexes_values[y])):
		ydata.append(data[indexes_values[y][x]]+0.0001*y)
	ax.plot(indexes_values[y],ydata, colors[y], label=str(indexes_names[y]))
plt.legend()
plt.show()
