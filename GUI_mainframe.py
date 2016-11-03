"""
GUI designed by Dandois for a mainframe around the python processing module

"""

import tkinter as tk
import config



def update_GUI(text,label):
    text += "\n"*(5-text.count('\n'))
    label.set(text)



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
        self.entry.bind("<BackSpace>", self.OnPressBack)

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
        global printlabel
        printlabel = self.labelVariableRead
        if "pdata" not in dir:
            update_GUI("Please select your working Directory",printlabel)
        else:
            update_GUI("Ready to read preprocessed data...",printlabel)
        label = tk.Label(self,textvariable=self.labelVariableRead,anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=4,columnspan=4,rowspan=4,sticky="EW")

        #katelijne button
        buttons = tk.Button(self, text=u"Katelijne", command=self.OnButtonKatelijne)
        buttons.grid(column=4, row=7)

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
            update_GUI("Please use xf2; apk and abs preprocessed data from topspin...",printlabel)
        else:
            update_GUI("Ready to read preprocessed data...",printlabel)
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonRead(self):
        import Read_data as rd
        import Fit_curves as fc
        update_GUI("Reading DATA",printlabel)
        (vclist, data, SW_ppm, SO1_ppm) = rd.fn_read_data(dir,printlabel)
        (vclist, peaks_value_list, peaks_ppm) = rd.fn_process_peaks(vclist, data, SW_ppm, SO1_ppm, printlabel)
        fc.fn_fit_curves(vclist, peaks_value_list, peaks_ppm, printlabel)

        #############################################################################CODE CALL
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonKatelijne(self):
        import Read_data as rd
        import Fit_curves as fc
        import Proces_katelijne as pk
        update_GUI("Performing Katelijne", printlabel)
        pk.katelijne(printlabel)

        #############################################################################CODE CALL
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonSettings(self):
        import subprocess
        subprocess.call(['notepad.exe','config.py'])
        update_GUI("Please restart the program to apply settings.",printlabel)
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnPressEnter(self,event):
        entry = self.entry.get()
        self.entry.delete(0,'end')
        exec(entry)
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnPressBack(self, event):
        self.entry.delete(len(entry)-1,'end')
        self.entry.focus_set()
        self.entry.selection_adjust(0)

if __name__ == "__main__":
    app = app_tk(None)
    app.title('2D-SEL TOCSY Matching')
    app.mainloop()