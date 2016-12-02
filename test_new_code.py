
from Read_data import *
from functions import fn_calc_plots
import matplotlib.pyplot as plt

printlabel = "testing"

#should end up in code
dict_param, data = fn_read_data(r"D:\DATA\master2016\DATABASE\12\pdata\1",printlabel)
#dict_param, data = fn_read_data(r"D:\DATA\master2016\SAMPLES\2\pdata\1",printlabel)



a = plt.figure(1)
for x in range(len(data)):
	plt.plot(data[x][:int(len(data[x])/2)], label=x)
plt.title(dict_param["sample_name"])
plt.show()
#plt.legend()



#should end up in code
dict_param, data = fn_reform(dict_param,data)
dict_param, data = fn_process_chunk(dict_param, data, printlabel)
dict_param = fn_process_curve(dict_param, data, printlabel)


#show the curves for integral limits
num = fn_calc_plots(data)
for y in range(len(data)): #loop per chunk
	ax = plt.subplot(num+y) #new subplot
	ax.set_title("%s - chunk %s" %(dict_param["sample_name"], str(y+1)))
	for x in range(len(data[y])):
		plt.plot(data[y][x], label=x)
	integral= []
	for q in range(len(data[0][0])):
		integral.append(0)
	for inte in dict_param["chunk_param"][y]["chunk_integrals"]:
		x1,x2 = inte[0], inte[1]
		for val in range(x2-x1):
			integral[x1+val] = 1
	plt.plot(integral,label="integral")
	#plt.legend()
plt.show()

#show the curves that must be compared to the database
num = fn_calc_plots(dict_param["chunk_param"])
for z in range(len(dict_param["chunk_param"])):
	x = dict_param["chunk_param"][z]
	ax = plt.subplot(num+z)
	ax.set_title("Chunk %s" %str(z+1))
	for y in range(len(x["chunk_values"])):
		plt.plot(dict_param["mtlist"], x["chunk_values"][y], label=x["chunk_peak_ind_ppm"][y])
plt.show()
