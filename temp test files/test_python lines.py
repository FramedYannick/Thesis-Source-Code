
import nmrglue as ng						#NMR software
import matplotlib.pyplot as plt				#for plotting
import tkinter as tk						#for GUI
import numpy as np
dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\DATABASE\12\pdata\1")
#dic, data = ng.bruker.read(r"D:\DATA\master2016\Test_500\2")
peaks = ng.peakpick.pick(data, (0.05), diag=False, cluster=True,est_params=True)
fig = plt.figure()
data = data[:26]
for x in range(len(data)):
    plt.plot(data[x],label=x)

plt.legend()
plt.show()

from time import sleep
for x in range(len(data)):
    plt.plot(data[x],label=x)
    plt.legend()
    plt.show()


#File = open(r"C:\Users\Yannick\Documents\_Documenten\UGent\Thesis\text.txt",'a')
#File.write(str(dic) + "\n \n\n\n\n\n\n\n\n" + str(peaks))


#for 3d processing
data_new = []
for x in range(13):
  data_new.append([])
  for x in range(len(data)):
    data_new[len(data_new)-1].append([])

for f1 in range(len(data)):
  for f2 in range(13):
    f3 = data[f1][f2]
    data_new[f2][f1] = f3

data = data_new
SW_ppm = 4; SW2_ppm = 1; SO1_ppm = 4.9; diag = []

for x in range(len(data[0])):
    temp_ppm = (len(data[0])-x)/len(data[0])*SW2_ppm + SO1_ppm -0.5*SW2_ppm
    diag.append(data[0][x][int(((SO1_ppm-temp_ppm-0.5*SW_ppm)/SW_ppm*len(data[0][0]))+len(data[0][0]))])
    print(x, int(((SO1_ppm-temp_ppm-0.5*SW_ppm)/SW_ppm*len(data[0][0]))+len(data[0][0])))

