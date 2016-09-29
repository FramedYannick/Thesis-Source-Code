
#import needed modules
import nmrglue as ng						#NMR software
import matplotlib.pyplot as plt				#for plotting
import tkinter as tk						#for GUI
import numpy as np

#import needed seperate functions
from tkinter import filedialog

# import user config file
import config



#ask PATH to NMR data
root = tk.Tk()
root.title("Path to TOCSY experiment folder or processing folder")
root.withdraw()
dir = filedialog.askdirectory(initialdir = config.Default_Directory)

#read in the data from given dir
if "pdata" not in dir:
	input("Please use preprocessed data from topspin\nPress Enter to close...")
	exit()

else:
	dic, data = ng.bruker.read_pdata(dir)		#this has been processed with topspin; no math is needed

#processing of the data and dic

#collect the spectral window info
dir2 = dir[:dir.find('\pdata')]
dic2 = open(dir2+r'\acqu','r').read()
SO1_hz = float(dic2[dic2.find(r'$O1=')+5:dic2.find('##$O2')])
SW_hz = float(dic['procs']['SW_p'])


#peak picking
dataabs = abs(data)
peaks = ng.peakpick.pick(data, dataabs.mean()**2/dataabs.std())

#create the plot
cl = data.std() * 2 * 1.2 ** np.arange(10)		#make list of 10 hights to be drawn
fig = plt.figure()
fig.set_size_inches(15,15)
ax = fig.add_subplot(111)
ax.contour(data, cl, colors='blue')
fig.savefig(r'C:\Users\Yannick\Documents\_Documenten\UGent\Thesis\pic.png',dpi=1000)


print(data)
print(len(data)*len(data[1]))
print(peaks)
print(len(peaks))
input("Press Enter to close...")