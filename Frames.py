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
        button2 = Button(self, text ="Generate unprocessed image stacks",command = lambda : controller.ExportUnProcessedStack()) 
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
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(StackOptions)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Next", 
                            command = lambda : controller.show_frame(LabelImages)) 
        button2.grid(row = 1, column = 2, padx = 10, pady = 10) 

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
        
class Export(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        label = Label(self, text ="Export objects", font = LARGEFONT) 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        button1 = Button(self, text ="Export", 
                            command = lambda : controller.show_frame(Export)) 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        button2 = Button(self, text ="Back", 
                            command = lambda : controller.show_frame(LabelImages)) 
        button2.grid(row = 1, column = 2, padx = 10, pady = 10)   