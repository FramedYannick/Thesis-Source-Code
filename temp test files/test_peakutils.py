
#temp test file for optimal peak picking algorithm

import nmrglue as ng
import numpy as np
import matplotlib.pyplot as plt
import config
from detect_peaks import detect_peaks


dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\Test_500\2\pdata\1")

data = data[:10]

data = data/np.max(data)
print(data)

##########################################################################################
row = []
for x in range(len(data[0])):
    column = []
    for y in range(len(data)):
        column.append(data[y][x])
    row.append(np.max(column))

data = row


##########################################################################################
#for x in range(len(data)):
#	if data[x] < 0.:
#		data[x] = 0.

import peakutils
ind = peakutils.indexes(data,thres=0.)
print(str(len(ind)) + " " + str(ind))
temp = []
for x in ind:
	temp.append(abs(data[x]))
limit = np.mean(temp)*4
print(limit)
ind_temp = []
for x in ind:
	if data[x] > limit:
		ind_temp.append(x)
ind = ind_temp


print(str(len(ind)) + " " + str(ind))






##########################################################################################












indexes_names = ["peakutils"]
indexes_values = [ind]

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
colors = ['ro', 'bo', 'go', 'co', 'mo', 'yo', 'ko', 'r^', 'b^', 'g^', 'c^', 'm^', 'y^', 'k^', 'r*', 'b*', 'g*', 'c*',
          'm*', 'y*', 'k*', 'rd', 'bd', 'gd', 'cd', 'md', 'yd', 'kd', 'rD', 'bD', 'gD', 'cD', 'mD', 'yD', 'kD', ]
ax.plot(data, 'b-')
#ax.plot(y2, 'r-')
for y in range(len(indexes_names)):
	ydata = []
	for x in range(len(indexes_values[y])):
		ydata.append(data[indexes_values[y][x]]+0.0001*y)
	ax.plot(indexes_values[y],ydata, colors[y], label=str(indexes_names[y]))
plt.legend()
plt.show()
