import nmrglue as ng						#NMR software
import matplotlib.pyplot as plt				#for plotting
import tkinter as tk						#for GUI
import numpy as np

dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\Sucrose_D2O\801\pdata\1")
peaks = ng.peakpick.pick(data, (0.05), diag=False, cluster=True,est_params=True)

y = 0
for x in data:
    if max(x) >y:
        y = max(x)
print(y)

#File = open(r"C:\Users\Yannick\Documents\_Documenten\UGent\Thesis\text.txt",'a')
#File.write(str(dic) + "\n \n\n\n\n\n\n\n\n" + str(peaks))