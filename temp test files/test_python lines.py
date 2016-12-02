
import nmrglue as ng						#NMR software
import matplotlib.pyplot as plt				#for plotting
import tkinter as tk						#for GUI
import numpy as np
dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\DATABASE\2\pdata\1")
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