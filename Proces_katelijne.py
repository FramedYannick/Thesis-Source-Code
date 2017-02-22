
def katelijne(printlabel, Settings):
	import nmrglue as ng						#NMR software
	import numpy as np

	katelijne_lijst = []

	sugar_list = [["a-Glucopyr.", r"D:\DATA\Katelijne2011\glucose_700", [21,22,23,24,25,26,27,28,29,30]], ["b-Glucopyr.", r"D:\DATA\Katelijne2011\glucose_700", [41,42,43,44,45,46,47,48,49,50]], ["a-Rhamnopyr.", r"D:\DATA\Katelijne2011\rhamnose_700", [3,4,5,6,7,8,9,10,11,12]], ["b-Rhamnopyr.", r"D:\DATA\Katelijne2011\rhamnose_700", [23,24,25,26,27,28,29,30,31,32]], ["a-Galactopyr.", r"D:\DATA\Katelijne2011\galactose_700", [3,4,5,6,7,8,9,10,11,12]], ["b-Galactopyr.", r"D:\DATA\Katelijne2011\galactose_700", [23,24,25,26,27,28,29,30,31,32]], ["a-Mannose.", r"D:\DATA\Katelijne2011\mannose_700", [3,4,5,6,7,8,9,10,11,12]], ["b-Mannose.", r"D:\DATA\Katelijne2011\mannose_700", [23,24,25,26,27,28,29,30,31,32]]]
	for sugar_id in sugar_list:
		sugar = sugar_id[0]
		dir = sugar_id[1]
		list = sugar_id[2]
		from GUI_mainframe import update_GUI
		update_GUI("Performing Katelijne analysis on sugar %s\n\nUsing %s" %(sugar, str(list)), printlabel)

		vclist = [10,20,30,40,50,60,70,80,90,100]
		data1 = []
		data2 = []

		for x in list:
			dir_exp = dir + '\\' + str(x) + r"\pdata\1"
			dic, data = ng.bruker.read_pdata(dir_exp)
			mixingtime = (open(dir_exp + r"\title").readlines()[0])[(open(dir_exp + r"\title").readlines()[0]).find('ms')-2:(open(dir_exp + r"\title").readlines()[0]).find('ms')]
			mixingtime = int(mixingtime)
			if mixingtime == 0:
				mixingtime = 100
			data1.append([mixingtime,data])
		data1.sort(key=lambda x: x[0], reverse=False)
		for x in data1:
			data2.append(x[1])

		# collect the parameters and convert to ppm
		dic2 = open(dir_exp[:dir_exp.find('pdata')] + r'\acqus', 'r').read()
		B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
		SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
		SW_hz = float(dic['procs']['SW_p'])
		SW_ppm = SW_hz / B0_hz
		SO1_ppm = SO1_hz / B0_hz
		duplet_ppm = 14/B0_hz

		from Class import Chunk
		temp = Chunk(data2, sugar, 100, SW_ppm, duplet_ppm, vclist, printlabel, Settings)
		temp.fn_plot()



		katelijne_lijst.append(temp)
	return katelijne_lijst






