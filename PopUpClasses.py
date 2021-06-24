from tkinter import filedialog
from tkinter import * 
from PIL import Image, ImageTk  
from tkinter.messagebox import showinfo 

class InfoWindow(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.infoLabel=Label(top,text="Please enter file resolution with ; to separate values")
        self.infoLabel.pack()
        self.infoEntry=Entry(top)
        self.infoEntry.insert(0,"0.045043;0.045043;0.045043")
        self.infoEntry.pack()
        self.infoButton=Button(top,text='Ok',command=self.cleanup)
        self.infoButton.pack()
        top.bind('<Return>', self.cleanup)
        top.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
            self.value="1"
            self.top.destroy()
    def cleanup(self, event=None):
        self.value=self.infoEntry.get()
        self.top.destroy() 
        
class RawInfoWindow(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.infoLabel=Label(top,text="Please enter image resoltuion (width,height,layers and bit rate, scanner will provide details) \n with ; to separate values.")
        self.infoLabel.pack()
        self.infoEntry=Entry(top)
        self.infoEntry.insert(0,"2965;2361;2119;16")
        self.infoEntry.pack()
        self.infoButton=Button(top,text='Ok',command=self.cleanup)
        self.infoButton.pack()
        top.bind('<Return>', self.cleanup)
        top.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
            self.value="1"
            self.top.destroy()
    def cleanup(self, event=None):
        self.value=self.infoEntry.get()
        self.top.destroy() 

class DownsampleWindow(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.infoLabel=Label(top,text="Please enter the downsample rate or 1 for no downsampling")
        self.infoLabel.pack()
        self.infoEntry=Entry(top)
        self.infoEntry.insert(0,"2")
        self.infoEntry.pack()
        self.infoButton=Button(top,text='Ok',command=self.cleanup)
        self.infoButton.pack()
        top.bind('<Return>', self.cleanup)
        top.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
            self.value="1"
            self.top.destroy()
    def cleanup(self, event=None):
        self.value=self.infoEntry.get()
        self.top.destroy()
    
class GenerateTiffStackWindow(object): 
    def __init__(self,master):
        top=self.top=Toplevel(master)
        
        self.generateRawTiffs = IntVar()
        self.generateProcessedTiffs = IntVar() 
        self.generate3DModels = IntVar() 
        self.generateSegmentedTiffs = IntVar()
        
        self.infoLabel=Label(top,text="Please choose the options for tiff stack generation")
        self.infoLabel.pack()
        
        self.generateRawTiffsCheck = Checkbutton(top,text="Generate Raw Tiffs", variable = self.generateRawTiffs) 
        self.generateRawTiffsCheck.pack() 
        
        self.generateProcessedTiffsCheck = Checkbutton(top,text="Generate Processed Tiffs", variable = self.generateProcessedTiffs) 
        self.generateProcessedTiffsCheck.pack()
        
        self.generate3DModelCheck = Checkbutton(top,text="Generate 3D Models", variable = self.generate3DModels) 
        self.generate3DModelCheck.pack()
        
        self.generateSegmentedTiffsCheck = Checkbutton(top,text="Generate Segmented Tiffs", variable = self.generateSegmentedTiffs) 
        self.generateSegmentedTiffsCheck.pack()
        
        self.infoButton=Button(top,text='Ok',command=self.cleanup)
        self.infoButton.pack()
    def cleanup(self):
        self.value = str(self.generateRawTiffs.get()) + ";"+ str(self.generateProcessedTiffs.get()) + ";" + str(self.generate3DModels.get())+ ";" + str(self.generateSegmentedTiffs.get()) 
        self.top.destroy()
        
class GetTrayCSVs(object): 
    def __init__(self,master,trayCount):
        top=self.top=Toplevel(master)
        self.infoLabel=Label(top,text="Select directories for each trays csv, or click Ok to leave blank")
        self.infoLabel.pack()
        self.paths = "" 
        self.trayCount = trayCount
        self.fileButton=Button(top,text='get files',command=self.getCSVFiles)
        self.fileButton.pack()
        self.infoButton=Button(top,text='Ok',command=self.cleanup)
        self.infoButton.pack()
    def getCSVFiles(self):
        for i in range(len(self.trayCount)):
            temp = filedialog.askopenfilename(filetypes = (("csv files","*.csv"),("all files","*.*")))
            if temp == '': 
                temp = ' '
            self.paths = self.paths+temp+"*"  
        self.cleanup()
    def cleanup(self):
        self.value=self.paths
        self.top.destroy()
