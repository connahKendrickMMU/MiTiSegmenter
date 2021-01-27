# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 15:18:07 2021

@author: conna
"""
import tkinter as tk
from tkinter import *  
LARGEFONT =("Helvetica", 20)

class StartPage(tk.Frame): 
    def __init__(self, parent, controller):  
        tk.Frame.__init__(self, parent) 
          
        # label of frame Layout 2 
        label = Label(self, text ="MiTiSegmenter", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10)  
   
        button1 = Button(self, text ="Load Image Stack", 
        command = lambda : controller.LoadImagesSelected(StackOptions,False)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        ## button to show frame 2 with text layout2 
        button2 = Button(self, text ="Load Raw Image", 
        command = lambda : controller.LoadImagesSelected(StackOptions,True)) 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
        
        ## button to show frame 2 with text layout2 
        button3 = Button(self, text ="Generate info file", 
        command = lambda : controller.show_frame(generateInfoFile)) 
        button3.grid(row = 3, column = 1, padx = 10, pady = 10) 

class StackOptions(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Image Stack Options", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Seperate Scanned objects",command = lambda : controller.show_frame(ThresAndCellStack)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button2 = Button(self, text ="Generate unprocessed image stacks",command = lambda : controller.ExportUnProcessedStack(True)) 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
        
        # button to show frame 2 with text 
        button2 = Button(self, text ="Seperate Trays",command = lambda : controller.show_frame(SeperateTrays)) 
        button2.grid(row = 3, column = 1, padx = 10, pady = 10) 
   
class SeperateTrays(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Seperate trays", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Separate Trays", 
                            command = lambda : controller.show_frame(StartPage)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(StackOptions)) 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
        

class ThresAndCellStack(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Tray removal", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
        
        self.cellBar = Scale(self, from_=1, to=255, orient=HORIZONTAL, label="Cel-shade Base Value", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustCellBase) 
        self.cellBar.grid(row=2,column=0,sticky = NW) 
        self.cellBar.set(controller.cellBase)
        
        self.thresholdBar = Scale(self, from_=0, to=255, orient=HORIZONTAL, label="Threshold Value Max", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustThresholdMax) 
        self.thresholdBar.grid(row=3,column=0,sticky = W) 
        self.thresholdBar.set(controller.thresholdMax) 
        
        self.thresholdBarMin = Scale(self, from_=0, to=255, orient=HORIZONTAL, label="Threshold Value Min", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustThresholdMin) 
        self.thresholdBarMin.grid(row=4,column=0,sticky = W) 
        self.thresholdBarMin.set(controller.thresholdMin)

        # button to show frame 2 with text 
        BckButton = Button(self, text ="Back", command = lambda : controller.show_frame(StackOptions)) 
        BckButton.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        NxtButton = Button(self, text ="Next", command = lambda : controller.show_frame(LabelImages)) 
        NxtButton.grid(row = 1, column = 2, padx = 10, pady = 10) 
        
        CellHelpButton = Button(self, text ="Help", command = lambda : controller.ShowCellHelp()) 
        CellHelpButton.grid(row = 2, column = 1, padx = 10, pady = 10) 
        
        ThresHelpButton = Button(self, text ="Help", command = lambda : controller.ShowThresHelp()) 
        ThresHelpButton.grid(row = 3, column = 1, padx = 10, pady = 10) 
    
    def adjustThresholdMax(self,val):
        if int(val) <= self.thresholdMin: 
            self.thresholdBar.set(self.thresholdMin+1) 
        else:
            self.thresholdMax = int(val)
        self.refreshImages() 
        
    def adjustThresholdMin(self,val):
        if int(val) >= self.thresholdMax:
            self.thresholdBarMin.set(self.thresholdMax-1)
        else:
            self.thresholdMin = int(val)
        self.refreshImages()
        
class LabelImages(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Labeling Options", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Numbered", 
                            command = lambda : controller.show_frame(Export)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Import CSV label file", 
                            command = lambda : controller.show_frame(TrayStack)) 
        button2.grid(row = 1, column = 2, padx = 10, pady = 10) 
        
        button2 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(ThresAndCellStack)) 
        button2.grid(row = 1, column = 3, padx = 10, pady = 10)

class TrayStack(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="CSV labeling", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Next", 
                            command = lambda : controller.show_frame(Export)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Apply Tray", 
                            command = lambda : controller.show_frame(Export)) 
        button2.grid(row = 1, column = 2, padx = 10, pady = 10)   
        
        button2 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(LabelImages)) 
        button2.grid(row = 1, column = 3, padx = 10, pady = 10)   
        
class Export(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Export objects", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Export", 
                            command = lambda : controller.exportTiffStacks()) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(LabelImages)) 
        button2.grid(row = 1, column = 2, padx = 10, pady = 10)   