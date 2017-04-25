"""
GUI designed by Dandois for a mainframe around the python processing module

"""

import tkinter as tk
from Class import Experiment, Database, Chunk, Values, Curve

def update_GUI(text,label):
	if str(label) not in ["testing", "ignore"]:
		text += "\n"*(5-text.count('\n'))
		label.set(text)
	elif str(label) == "testing":
		print(text)


class app_tk(tk.Tk):
	def __init__(self,parent):
		tk.Tk.__init__(self,parent)
		self.parent = parent
		self.entry = tk.Entry(self)
		self.grid()
		for i in range(Settings["GUI_width"] + 1):
			self.grid_columnconfigure(i, weight=1, uniform="foo")
		self.database = []
		self.experiment = []
		self.comparison = []
		self.initialize()

	def initialize(self):

########################################################################## EXPERIMENT

		#experiment tekst label
		self.experiment_label_text = tk.StringVar()
		self.experiment_label_text.set("Experiment:")
		label = tk.Label(self,textvariable=self.experiment_label_text,anchor="w")
		label.grid(column=0,row=0,columnspan=2,sticky="EW")

		#browse button
		button_browse_exp = tk.Button(self,text=u"Browse",command=self.OnButtonBrowse_exp, anchor="center")
		button_browse_exp.grid(column=Settings["GUI_width"],row=1, sticky="EWNS")

		#browse label
		self.experiment_label = tk.StringVar()
		self.experiment_label.set("Current directory:  " + Settings["Experiment_Directory"])
		label = tk.Label(self,textvariable=self.experiment_label,anchor="w",fg=Settings["Foreground"],bg=Settings["Background"])
		label.grid(column=0,row=1,columnspan=Settings["GUI_width"],sticky="EW")

########################################################################## DATABASE

		# database tekst label
		self.database_label_text = tk.StringVar()
		self.database_label_text.set("Database:")
		label = tk.Label(self, textvariable=self.database_label_text, anchor="w")
		label.grid(column=0, row=3, columnspan=2, sticky="EWNS")

		# browse button
		button_browse_data = tk.Button(self, text=u"Browse", command=self.OnButtonBrowse_data,  anchor="center")
		button_browse_data.grid(column=Settings["GUI_width"], row=4, sticky="EWNS")

		# browse label
		self.database_label = tk.StringVar()
		self.database_label.set("Current directory:  " + Settings["Database_Directory"])
		label = tk.Label(self, textvariable=self.database_label, anchor="w", fg=Settings["Foreground"],
						 bg=Settings["Background"])
		label.grid(column=0, row=4, columnspan=Settings["GUI_width"], sticky="EW")

########################################################################## STATUSLABELS and LOAD FUNCTIONS

		# custom printlabel
		self.labelVariableRead = tk.StringVar()
		global printlabel
		self.printlabel, printlabel = self.labelVariableRead, self.labelVariableRead
		label = tk.Label(self, textvariable=self.labelVariableRead, anchor="w", fg=Settings["Foreground"], bg=Settings["Background"])
		label.grid(column=0, row=6, columnspan=Settings["GUI_width"], rowspan=5, sticky="EWNS")
		update_GUI("Set up experiment or database for usage.", self.printlabel)

		# plots tekst label
		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("Program status:")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=Settings["GUI_width"]-3, row=12, columnspan=2, sticky="EW")

		# experiment status label
		self.status_exp_label_text = tk.StringVar()
		self.status_exp_label_text.set("Experiment")
		self.status_exp_label = tk.Label(self, textvariable=self.status_exp_label_text, anchor="center", bg="red", font = "Verdana 10 bold")
		self.status_exp_label.grid(column=Settings["GUI_width"]-3, row=13, columnspan=2, sticky="EW")
		self.check_exp_status()

		button_load_exp = tk.Button(self, text=u"Load", command=self.experiment_load, anchor="center")
		button_load_exp.grid(column=Settings["GUI_width"]-1, row=13, sticky="EWNS", columnspan=2)

		# database status label
		self.status_data_label_text = tk.StringVar()
		self.status_data_label_text.set("Database")
		self.status_data_label = tk.Label(self, textvariable=self.status_data_label_text, anchor="center", bg="red", font="Verdana 10 bold")
		self.status_data_label.grid(column=Settings["GUI_width"]-3, row=14, columnspan=2, sticky="EW")
		self.check_data_status()

		button_load_data = tk.Button(self, text=u"Load", command=self.database_load, anchor="center")
		button_load_data.grid(column=Settings["GUI_width"]-1, row=14, sticky="EWNS")
		button_load_data = tk.Button(self, text=u"Compile", command=self.database_compile, anchor="center")
		button_load_data.grid(column=Settings["GUI_width"], row=14, sticky="EWNS")


		button_compare = tk.Button(self, text=u"Run DB Comparison", command=self.experiment_compare, anchor="center")
		button_compare.grid(column=Settings["GUI_width"] - 1, row=15, sticky="EWNS", columnspan=2)


########################################################################## PLOT CHECKBOX

		# plots tekst label
		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("Required Plots")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=0, row=12, columnspan=2, sticky="EW")

		self.plot_exp_check = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Experiment PLot", variable=self.plot_exp_check, onvalue=True, offvalue=False, command=self.fn_plot_exp, anchor="w")
		if Settings["plot_exp"]: check.toggle()
		check.grid(column=0, row=13, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Plots all chunks seperate.)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=1, row=13, columnspan=2, sticky="EW")

		self.plot_chunk_check = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Chunk Plot", variable=self.plot_chunk_check, onvalue=True, offvalue=False, command=self.fn_plot_chunk, anchor="w")
		if Settings["plot_chunk"]: check.toggle()
		check.grid(column=0, row=14, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Plots chunks with database results.)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=1, row=14, columnspan=2, sticky="EW")

		self.plot_values_check = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Values Plot", variable=self.plot_values_check, onvalue=True, offvalue=False, command=self.fn_plot_values, anchor="w")
		if Settings["plot_values"]: check.toggle()
		check.grid(column=0, row=15, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Plots chunks with PPM values.)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=1, row=15, columnspan=2, sticky="EW")


		buttons = tk.Button(self, text=u"Replot", command=self.fn_replot)
		buttons.grid(column=2, row=12, sticky="EWNS")


########################################################################## SETTINGS CHECKBOX

		# AM tekst label
		self.am_label_text = tk.StringVar()
		self.am_label_text.set("Quick Settings")
		label = tk.Label(self, textvariable=self.am_label_text, anchor="w")
		label.grid(column=3, row=12, columnspan=2, sticky="EW")

		self.am_ccm = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Alternate CCM", variable=self.am_ccm, onvalue=True, offvalue=False, command=self.fn_am_ccm, anchor="w")
		if Settings["am_norm"]: check.toggle()
		check.grid(column=3, row=13, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Uses Fréchet method for curve comparison.)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=4, row=13, columnspan=2, sticky="EW")

		self.plot_integration = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Integration limits", variable=self.plot_integration, onvalue=True, offvalue=False, command=self.fn_plot_integration, anchor="w")
		if Settings["plot_integration"]: check.toggle()
		check.grid(column=3, row=14, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Shows the integration limits in a double data plot)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=4, row=14, columnspan=2, sticky="EW")

		self.gp_chunk = tk.BooleanVar()
		check = tk.Checkbutton(self, text="Custom Chunks", variable=self.gp_chunk, onvalue=True, offvalue=False,command=self.fn_gp_chunks, anchor="w")
		if Settings["gp_chunks"]: check.toggle()
		check.grid(column=3, row=15, columnspan=1, sticky="EW")

		self.checkbox_label_text = tk.StringVar()
		self.checkbox_label_text.set("(Set custom chunks for database comparison - use Exp. Plot!)")
		label = tk.Label(self, textvariable=self.checkbox_label_text, anchor="w")
		label.grid(column=4, row=15, columnspan=2, sticky="EW")

		# custom settings button
		buttons = tk.Button(self, text=u"Default settings", command=self.OnButtonSettings)
		buttons.grid(column=5, row=12, sticky="EWNS")


	########################################################################## BUTTON FUNCTIONS

	def OnButtonBrowse_exp(self):
		from tkinter import filedialog
		root = tk.Tk()
		root.withdraw()
		dir = filedialog.askdirectory(initialdir=Settings["Experiment_Directory"])
		self.experiment_label.set("Current directory:  " + dir)
		Settings["Experiment_Directory"] = dir
		if "pdata" not in dir:
			update_GUI("Please use xf2; apk and abs preprocessed data from topspin...",self.printlabel)
		else:
			update_GUI("Ready to read experiment data...\nDon't forget to reload experiment!!!",self.printlabel)
		self.check_exp_status()
		self.change_exp_status("orange")
		self.entry.focus_set()
		self.entry.selection_adjust(0)

	def OnButtonBrowse_data(self):
		from tkinter import filedialog
		root = tk.Tk()
		root.withdraw()
		dir = filedialog.askdirectory(initialdir=Settings["Database_Directory"])
		self.database_label.set("Current directory:  " + dir)
		Settings["Database_Directory"] = dir
		self.check_data_status()
		self.entry.focus_set()
		self.entry.selection_adjust(0)

	def OnButtonSettings(self):
		import subprocess
		subprocess.call(['notepad.exe','config.py'])
		update_GUI("Please restart the program to apply settings.",self.printlabel)
		self.entry.focus_set()
		self.entry.selection_adjust(0)

	def fn_replot(self):
		from Class import Experiment, Database
		if type(self.experiment) == Experiment:
			if Settings["plot_exp"] and self.status_exp == "green":
				self.experiment.fn_plot()
			if Settings["plot_chunk"] and len(self.comparison) != 0:
				for x in range(len(self.comparison)):
					#create chunk list for plotting
					temp_list = []
					for y in range(3):
						temp_list.append(self.comparison[x][1][y][1])
					self.experiment.chunks[x].fn_plot(temp_list)
			if Settings["plot_values"] and self.status_exp == "green":
				for x in self.experiment.chunks:
					x.content.fn_plot()
			if Settings["plot_integration"] and self.status_exp == "green":
				for x in self.experiment.chunks:
					x.fn_plot_int()
		else:
			update_GUI("Can't do replotting without the experiment loaded.", self.printlabel)

	########################################################################## CHECK FUNCTIONS - switch Settings between True and False as storage

	def fn_plot_exp(self):
		Settings["plot_exp"] = self.plot_exp_check.get()
	def fn_plot_chunk(self):
		Settings["plot_chunk"] = self.plot_chunk_check.get()
	def fn_plot_values(self):
		Settings["plot_values"] = self.plot_values_check.get()
	def fn_am_ccm(self):
		Settings["am_norm"] = self.am_ccm.get()
	def fn_plot_integration(self):
		Settings["plot_integration"] = self.plot_integration.get()
	def fn_gp_chunks(self):
		Settings["gp_chunks"] = self.gp_chunk.get()

	########################################################################## STATUS FUNCTIONS

	def change_exp_status(self, color):
		self.status_exp_label.configure(bg=color)
		self.status_exp = color

	def change_data_status(self, color):
		self.status_data_label.configure(bg=color)
		self.status_data = color

	def check_exp_status(self):
		if type(self.experiment) == list:
			from functions import fn_check_dir
			if "pdata" in Settings["Experiment_Directory"] and fn_check_dir(Settings["Experiment_Directory"], "auditp.txt"):
				self.change_exp_status("blue")
			else:
				self.change_exp_status("red")
		else:
			self.change_exp_status("green")

	def check_data_status(self):
		if type(self.database) == list:
			from functions import fn_check_dir
			status = fn_check_dir(Settings["Database_Directory"], "Database.p")
			if status:
				self.change_data_status("blue")
			else:
				self.change_data_status("red")
		else:
			if self.database.status:
				self.change_data_status("green")
			else:
				self.change_data_status("orange")


	########################################################################## EXPERIMENT & DATABASE FUNCTIONS

	def experiment_load(self):
		from Class import Experiment
		self.experiment = Experiment(Settings["Experiment_Directory"], self.printlabel,Settings)
		self.check_exp_status()

	def database_load(self):
		from Class import Database
		self.database = Database(Settings["Database_Directory"], self.printlabel,Settings)
		self.check_data_status()

	def database_compile(self):
		from Class import Database
		self.database = Database(Settings["Database_Directory"], self.printlabel,Settings)
		self.database.fn_compile()
		self.check_data_status()

	def experiment_compare(self):
		from Class import Experiment
		if self.status_exp == self.status_data == "green" and type(self.experiment) == Experiment and Settings["gp_duplet_filtering"]:
			if Settings["gp_chunks"]:
				from tkinter import simpledialog
				Settings["gp_chunks_list"] = simpledialog.askstring("Custom chunks","Required Chunks?", initialvalue=str(Settings["gp_chunks_list"]).replace("[", "").replace("]", ""), parent=self)
				if Settings["gp_chunks_list"] == None:
					Settings["gp_chunks_list"] = []
			else:
				Settings["gp_chunks_list"] = []
			self.database.fn_override_settings(Settings)
			self.comparison = self.experiment.fn_compare(self.database)
			from functions import fn_result_printer
			text = fn_result_printer(self.comparison, Settings["gp_print"])
			update_GUI(text, self.printlabel)
		else:
			if not Settings["gp_duplet_filtering"]:
				update_GUI("Cannot run database comparison without Green status.\nPlease ensure both experiment and Database are loaded.", self.printlabel)
			else:
				update_GUI("Please enable duplet filtering in the config file.\nthe database only supports duplet filtering enabled data.", self.printlabel)



if __name__ == "__main__":
	from functions import fn_settings
	Settings = fn_settings()
	app = app_tk(None)
	app.title('2D-SEL TOCSY Matching')
	app.mainloop()
