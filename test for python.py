import nmrglue as ng						#NMR software
import matplotlib.pyplot as plt				#for plotting
import tkinter as tk						#for GUI
import numpy as np

dic, data = ng.bruker.read_pdata(r"D:\DATA\master2016\Test\3\pdata\1")


File = open(r"C:\Users\Yannick\Documents\_Documenten\UGent\Thesis\text.txt",'a')
File.write(str(dic))