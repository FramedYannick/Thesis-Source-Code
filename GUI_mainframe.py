"""
GUI designed by Dandois for a mainframe around the python processing module

"""

import tkinter as tk
import config
from Peak_writer import fn_peak_xml
from Peak_writer import fn_peak_plotter



class app_tk(tk.Tk):
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        global dir
        dir = config.Default_Directory
        self.grid()
        self.entry = tk.Entry(self)
        self.entry.grid(column=0,row=0,columnspan=4,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)

        #browse button
        button = tk.Button(self,text=u"Browse",command=self.OnButtonBrowse)
        button.grid(column=4,row=1)
        #browse label
        self.labelVariable1 = tk.StringVar()
        self.labelVariable1.set("Current directory:  " + dir)
        label = tk.Label(self,textvariable=self.labelVariable1,anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=4,sticky="EW")

        #read data
        buttonread = tk.Button(self,text=u"Read Peaks",command=self.OnButtonRead)
        buttonread.grid(column=4,row=2)
        #custom peak finder label
        self.labelVariableRead = tk.StringVar()
        if "pdata" not in dir:
            self.labelVariableRead.set("Please select your working Directory")
        else:
            self.labelVariableRead.set("Ready to read preprocessed data...")
        label = tk.Label(self,textvariable=self.labelVariableRead,anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=4,columnspan=4,rowspan=4,sticky="EW")

        #custom settings button
        buttons = tk.Button(self, text=u"Settings", command=self.OnButtonSettings)
        buttons.grid(column=4, row=8)


        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        #self.geometry(self.geometry())
        self.geometry('{}x{}'.format(500,250))
        self.entry.focus_set()
        self.entry.selection_adjust(0)

        for x in range(4):
            self.grid_columnconfigure(x, weight=1,uniform='foo')
        global printlabel
        printlabel = self.labelVariableRead

    def OnButtonBrowse(self):                                           #browse button to get correct dir
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        global dir
        dir = filedialog.askdirectory(initialdir=dir)
        self.labelVariable1.set("current directory:  " + dir)
        #check for the xml file
        from Read_data import fn_check_dir as check_dir
        if "pdata" not in dir:
            self.labelVariableRead.set("Please use xf2; apk and abs preprocessed data from topspin...")
        else:
            self.labelVariableRead.set("Ready to read preprocessed data...")
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonRead(self):
        print('not doing good')
        import Read_data as rd
        rd.fn_read_data(dir,self.labelVariableRead)
        #############################################################################CODE CALL

        self.labelVariableRead.set("Reading DATA")
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonSettings(self):
        import subprocess
        subprocess.call(['notepad.exe','config.py'])                    #might change to proper GUI later
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnPressEnter(self,event):
        entry = self.entry.get()
        self.entry.delete(0,'end')
        exec(entry)
        self.entry.focus_set()
        self.entry.selection_adjust(0)

if __name__ == "__main__":
    app = app_tk(None)
    app.title('TOCSY Matching')
    app.mainloop()