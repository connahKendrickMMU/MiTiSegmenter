# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 15:18:07 2021

@author: conna
"""
import tkinter as tk
from tkinter import *  
import ToolTip

from ToolTip import CreateToolTip
LARGEFONT =("Helvetica", 20)

class StartPage(tk.Frame): 
    def __init__(self, parent, controller):  
        tk.Frame.__init__(self, parent) 
        # label of frame Layout 2 
        label = Label(self, text ="MiTiSegmenter", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10)  
   
        button1 = Button(self, text ="Load Image Stack", 
        command = lambda : controller.LoadImagesSelected(StackOptions,False)) 
        button1.grid(row = 1, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button1, "Load a stack of images, such a tifs")
        
        ## button to show frame 2 with text layout2 
        button2 = Button(self, text ="Load Raw Image", 
        command = lambda : controller.LoadImagesSelected(StackOptions,True)) 
        button2.grid(row = 2, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button2, "Load a raw image. This will require you to input the XYZ scan resolution in millimetres, and the XYZ dimensions of the image volume")
        
class StackOptions(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Image Stack Options", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Seperate Scanned objects",command = lambda : controller.show_frame(ThresAndCellStack)) 
        button1.grid(row = 1, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button1,"This allows you to remove a tray holding the scanned\n objects it then seperates all the object into individual blobs")
    
        # button to show frame 2 with text 
        button2 = Button(self, text ="Generate unprocessed image stacks",command = lambda : controller.ExportUnProcessedStack(True)) 
        button2.grid(row = 2, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button2,"This splits a raw image into a stack of tif images")
        
        # button to show frame 2 with text 
        button3 = Button(self, text ="Seperate Trays",command = lambda : controller.show_frame(SeperateTrays)) 
        button3.grid(row = 3, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button3,"If using multiple trays this allows you create seperate tif stacks\n if you have a low memory machine this will help")
   
class SeperateTrays(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Seperate trays", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        listboxValues = Listbox(self) 
        listboxValues.grid(row=1, column = 0, rowspan=2, sticky = W) 
        
        # button to show frame 2 with text 
        button1 = Button(self, text ="Separate Trays", command = lambda : controller.exportTrays(listboxValues)) 
        button1.grid(row = 1, column = 3, padx = 10, pady = 10) 
        CreateToolTip(button1,"Seperate the trays")
        
        # button to add a tray
        addTray = Button(self, text ="Add Tray", command = lambda : controller.addTray(listboxValues)) 
        addTray.grid(row = 2, column = 3, padx = 10, pady = 10) 
        CreateToolTip(addTray,"Use the top slider to select the point you want one try to end\n and the next begin. You can add as many points as you like")
        
        removeTray = Button(self, text ="Remove Tray", command = lambda : self.deleteTray(listboxValues, controller)) 
        removeTray.grid(row = 2, column = 4, padx = 10, pady = 10) 
        CreateToolTip(removeTray,"Choose a try in the list and press this to remove it.")
        
        # button to show frame 3 with text 
        button2 = Button(self, text ="Back", command = lambda : controller.show_frame(StackOptions)) 
        button2.grid(row = 3, column = 3, padx = 10, pady = 10) 
        CreateToolTip(button2,"Returns to the stack options menu")
        
    def deleteTray(self,listboxValues, controller): 
        if listboxValues.size() > 0:
            #controller.layers.pop(listboxValues.curselection()[0])
            listboxValues.delete(listboxValues.curselection()[0])
            controller.refreshImages

class ThresAndCellStack(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Tray removal", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
        
        self.cellBar = Scale(self, from_=1, to=255, orient=HORIZONTAL,resolution = 1, label="Cel-shade Base Value", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustCellBase) 
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
        CreateToolTip(BckButton,"Returns to the stack options menu")
        # button to show frame 3 with text 
        NxtButton = Button(self, text ="Next", command = lambda : controller.show_frame(LabelImages)) 
        NxtButton.grid(row = 1, column = 2, padx = 10, pady = 10) 
        CreateToolTip(NxtButton,"Go to the label options menu")
        
class LabelImages(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="File naming options", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Numbered",command = lambda : controller.show_frame(Export)) 
        button1.grid(row = 1, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button1,"User does not provide a CSV file containing specimen IDs. Each discrete sample is assigned a unique ID number upon export")
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Import spreadsheets of specimen IDs",command = lambda : controller.show_frame(TrayStack)) 
        button2.grid(row = 2, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button2,"Import a comma separated variable file containing specimen IDs, formatted in an equivalent grid structure to the associated plates")
        
        button3 = Button(self, text ="Back",command = lambda : controller.show_frame(ThresAndCellStack)) 
        button3.grid(row = 3, column = 0, padx = 10, pady = 10)
        CreateToolTip(button3,"Return the the Threshold and cell shade options menu")

class TrayStack(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="CSV labeling", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Next",command = lambda : controller.show_frame(TrayAlign)) 
        button1.grid(row = 3, column = 2, padx = 10, pady = 10) 
        CreateToolTip(button1,"Move to the tray alignment")
        
        button3 = Button(self, text ="Back",command = lambda : controller.show_frame(LabelImages)) 
        button3.grid(row = 3, column = 1, padx = 10, pady = 10)   
        CreateToolTip(button3,"Return to the label images menu")
        
        listboxValues = Listbox(self) 
        listboxValues.grid(row=2, column = 0, rowspan=2, sticky = W)
        
        # button to show frame 3 with text 
        button2 = Button(self, text ="Apply Tray",command = lambda : controller.applyTray(listboxValues)) 
        button2.grid(row = 1, column = 0, padx = 10, pady = 10)   
        CreateToolTip(button2,"Automatically try to find the center of trays in the scan")
        
        removeTray = Button(self, text ="remove tray",command = lambda : self.deleteTray(listboxValues, controller)) 
        removeTray.grid(row = 1, column = 1, padx = 10, pady = 10)   
        CreateToolTip(removeTray,"Select a tray you want to delete and then press this button to remove the tray")
        
        addTray = Button(self, text ="add tray",command = lambda : controller.addTray(listboxValues)) 
        addTray.grid(row = 1, column = 2, padx = 10, pady = 10)   
        CreateToolTip(addTray,"Use the top slider and click the add tray button\n,to add this as a slice")
        
    def deleteTray(self,listboxValues, controller): 
        if listboxValues.size() > 0:
            #controller.layers.pop(listboxValues.curselection()[0])
            listboxValues.delete(listboxValues.curselection()[0])
            controller.refreshImages
        
class TrayAlign(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="CSV Alignment", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Next",command = lambda : controller.show_frame(Export)) 
        button1.grid(row = 2, column = 1, padx = 10, pady = 10) 
        CreateToolTip(button1,"Move to the export menu")
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Load CSV",command = lambda : controller.loadCSV()) 
        button2.grid(row = 1, column = 0, padx = 10, pady = 10)   
        CreateToolTip(button2,"Load a csv file for each tray in the scan")
        
        flipCSVH = Button(self, text ="Flip Tray Hor",command = lambda : controller.flipTrayHor()) 
        flipCSVH.grid(row = 1, column = 1, padx = 10, pady = 10)   
        CreateToolTip(flipCSVH,"Flip the CSV horizontally, so the top left is now the top right")
        
        flipCSVV = Button(self, text ="Flip Tray Ver",command = lambda : controller.flipTrayVer()) 
        flipCSVV.grid(row = 1, column = 2, padx = 10, pady = 10)   
        CreateToolTip(flipCSVH,"Flip the CSV Verticallly, so the top left is now the botton left")
        
        button3 = Button(self, text ="Back",command = lambda : controller.show_frame(TrayStack)) 
        button3.grid(row = 2, column = 0, padx = 10, pady = 10)   
        CreateToolTip(button3,"Return to the Tray stack menu")
        
        self.rotateBar = Scale(self, from_=0, to=360, orient=HORIZONTAL, label="Rotate Tray", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustGridRotation) 
        self.rotateBar.grid(row=3,column=0,sticky = NW) 
        self.rotateBar.set(controller.gridRotation)
        
        self.ScaleGridBarH = Scale(self, from_=0, to=280, orient=HORIZONTAL, label="Scale Tray Horizontal", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustGridSizeHor) 
        self.ScaleGridBarH.grid(row=4,column=0,sticky = W) 
        self.ScaleGridBarH.set(controller.gridSize[0]) 
        
        self.ScaleGridBarV = Scale(self, from_=0, to=280, orient=HORIZONTAL, label="Scale Tray Vertical", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.adjustGridSizeVert) 
        self.ScaleGridBarV.grid(row=5,column=0,sticky = W) 
        self.ScaleGridBarV.set(controller.gridSize[1])
        
        self.MoveGridX = Scale(self, from_=0, to=250, orient=HORIZONTAL, label="Move Tray X", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.AdjustGridCentreX) 
        self.MoveGridX.grid(row=6,column=0,sticky = W) 
        self.MoveGridX.set(0)
        
        self.MoveGridY = Scale(self, from_=0, to=250, orient=HORIZONTAL, label="Move Tray Y", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=controller.AdjustGridCentreY) 
        self.MoveGridY.grid(row=7,column=0,sticky = W) 
        self.MoveGridY.set(0)

class Export(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Export objects", font = LARGEFONT) 
        label.grid(row = 0, column = 0, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Export",command = lambda : controller.exportTiffStacks()) 
        button1.grid(row = 1, column = 0, padx = 10, pady = 10) 
        CreateToolTip(button1,"Export the object in the trays to seperate folders")
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Back",command = lambda : controller.show_frame(LabelImages)) 
        button2.grid(row = 2, column = 0, padx = 10, pady = 10)   
        CreateToolTip(button2,"Return to the label images menu")
