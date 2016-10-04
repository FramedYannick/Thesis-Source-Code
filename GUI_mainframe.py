"""
GUI designed by Dandois for a mainframe around the python processing module

"""

import tkinter as tk
import config

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
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)

        #browse button
        button = tk.Button(self,text=u"Browse",command=self.OnButtonClick1)
        button.grid(column=4,row=1)
        #browse label
        self.labelVariable1 = tk.StringVar()
        self.labelVariable1.set("Current directory:  " + dir)
        label = tk.Label(self,textvariable=self.labelVariable1,anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=4,sticky="EW")

        #custom peak finder button
        button2 = tk.Button(self,text=u"Custom peaks?",command=self.OnButtonClick2)
        button2.grid(column=4,row=2)
        #custom peak finder label
        self.labelVariable2 = tk.StringVar()
        self.labelVariable2.set("No peaks found yet.")
        label = tk.Label(self,textvariable=self.labelVariable2,anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=2,columnspan=4,sticky="EW")

        #analyse present peaks.xml
        buttons = tk.Button(self, text=u"Analyse Peaks", command=self.OnButtonClicks)
        buttons.grid(column=4, row=8)

        #custom settings button
        buttons = tk.Button(self, text=u"Settings", command=self.OnButtonClicks)
        buttons.grid(column=4, row=8)


        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        #self.geometry(self.geometry())
        self.geometry('{}x{}'.format(500,250))
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonClick1(self):                                           #browse button to get correct dir
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        global dir
        dir = filedialog.askdirectory(initialdir=dir)
        self.labelVariable1.set("current directory:  " + dir)
        #check for the xml file
        from Read_data import fn_check_xml as check_xml
        if (check_xml(dir)):
            self.labelVariable2.set("Use BRUKER peaks or custom find.")
        else:
            self.labelVariable2.set("No peaks found - use Topspin or custom peaks")

        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonClick2 (self):
        import Peak_finder as pf
        result = pf.peaker(dir)
        self.labelVariable2.set("Using Custom peaks from NMRGlue")
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnButtonClicks (self):
        import subprocess
        subprocess.call(['notepad.exe','config.py'])                    #might change to proper GUI later
        self.entry.focus_set()
        self.entry.selection_adjust(0)

    def OnPressEnter(self,event):
        self.labelVariable1.set("enter")
        self.entry.focus_set()
        self.entry.selection_adjust(0)




if __name__ == "__main__":
    app = app_tk(None)
    app.title('TOCSY Matching')
    app.mainloop()