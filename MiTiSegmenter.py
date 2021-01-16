import traceback 
import tkinter.messagebox
import tkinter as tk
from tkinter import filedialog
from tkinter import * 
from tkinter.messagebox import showinfo
from skimage import measure, morphology
import math
import numpy as np  
import cv2 as cv
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
import open3d as o3d 
import shutil


# our files
from PopUpClasses import *

####### version info #######
# python 3.6 # tkinter # PIL # numpy = 1.16.2 # cv2 = 4.1.1 # os # open3d = 0.8.0.0 # random   
####### Build exe ####### 
# need add path to dask.yaml and distribution.yaml in you python Lib/site-packages/(dask or distribution)
class ScanOBJGenerator(): 
    # initialisation 
    def __init__(self,master): 
        master.report_callback_exception = self.showError
        self.master = master
        self.thresholdMax = 255  
        self.thresholdMin = 0
        self.blobMinSizeVal = 50
        self.downsampleFactor = 4
        self.cellBase = 1
        self.usedThres =(0,0)
        #self.imgTopSize = (0,0) 
        #self.imgSideSize = (0,0) 
        #self.imgFrontSize = (0,0) 
        self.winWidth = master.winfo_screenwidth()
        self.winHeight = master.winfo_screenheight()
        self.gridSize = (0,0)
        self.gridCenter = (0,0)
        self.gridRotation = 0
        self.viewThresholdVar = 1#IntVar() 
        self.viewCellVar = 1 #IntVar()
        self.layers = []
        self.traySize = 50
        self.trayCSV = [] 
        self.init_GUI(master) 
        self.workingPath = "" 
        self.blobCenterOfMass = []
        self.TL = 0 
        self.TR = 0
        self.BL = 0
        self.BR = 0
        self.blobbed = False
        self.slides = [0,0,0]
        
    def init_GUI(self,master):
        #main window title and size
        master.title("MiTiSegmenter") 

        self.imageStack = None 
        # tool bar
        menubar = Menu(master)  
        master.config(menu=menubar) 
        fileMenu = Menu(menubar)  
        fileMenu.add_command(label="Load Images", command=self.loadImages) 
        fileMenu.add_command(label="Load raw Stack", command=self.loadRawStack)
        fileMenu.add_command(label="Generate Point Cloud", command=self.makeAllPointCloud) 
        fileMenu.add_command(label="Generate Info File", command=self.generateInfoFile) 
        fileMenu.add_command(label="Generate Tiff Stacks", command=self.exportTiffStacks) 
        fileMenu.add_command(label="Export Trays", command=self.exportTrays)
        menubar.add_cascade(label="File", menu=fileMenu)  
        
        editMenu = Menu(menubar) 
        editMenu.add_command(label="Flip Trays Horizontal", command=self.flipTrayHor) 
        editMenu.add_command(label="Flip Trays Vertical", command=self.flipTrayVer) 
        menubar.add_cascade(label="Edit", menu=editMenu)  

        # three views front, side, top 
        #self.frontBar = None
        #self.sideBar = None
        #self.topBar = None 
        
        # thresholding          
        self.thresholdBar = Scale(master, from_=0, to=255, orient=HORIZONTAL, label="Threshold Value Max", length=self.winWidth/3.6, sliderlength=self.winHeight//100, command=self.adjustThresholdMax) 
        self.thresholdBar.grid(row=3,column=0,sticky = W) 
        self.thresholdBar.set(self.thresholdMax) 
        
        self.thresholdBarMin = Scale(master, from_=0, to=255, orient=HORIZONTAL, label="Threshold Value Min", length=self.winWidth/3.6, sliderlength=self.winHeight//100, command=self.adjustThresholdMin) 
        self.thresholdBarMin.grid(row=4,column=0,sticky = W) 
        self.thresholdBarMin.set(self.thresholdMin)

        # traying
        self.listboxValues = Listbox(master) 
        self.listboxValues.grid(row=2, column = 2, rowspan=2, sticky = W)
        
        self.applyTrayBtn = Button(master, text="Apply Traying",command=self.applyTray)
        self.applyTrayBtn.grid(row=2,column=1,sticky = N)
        
        self.removeTrayBtn = Button(master, text="Delete Tray",command=self.deleteTray)
        self.removeTrayBtn.grid(row=2, column=1,sticky=W)
        
        self.addTrayBtn = Button(master, text="Add Tray",command=self.addTray)
        self.addTrayBtn.grid(row=2, column=1,sticky=E)
        
        self.RotateGridBar = Scale(master, from_=0, to=360, orient=HORIZONTAL, label="Rotate Tray", length=self.winWidth/3, sliderlength=self.winHeight//100, command=self.adjustGridRotation) 
        self.RotateGridBar.grid(row=3,column=1,sticky = NW) 
        self.RotateGridBar.set(self.gridRotation)
        
        self.ScaleGridBarH = Scale(master, from_=0, to=360, orient=HORIZONTAL, label="Scale Tray Horizontal", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.adjustGridSizeHor) 
        self.ScaleGridBarH.grid(row=4,column=1,sticky = NW) 
        self.ScaleGridBarH.set(self.gridSize[0])
        
        self.ScaleGridBarV = Scale(master, from_=0, to=360, orient=HORIZONTAL, label="Scale Tray Vertical", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.adjustGridSizeVert) 
        self.ScaleGridBarV.grid(row=4,column=1,sticky = NE) 
        self.ScaleGridBarV.set(self.gridSize[1])
        
        self.GridMidX = Scale(master, from_=0,to=360, orient=HORIZONTAL, label="Grid Center X", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.AdjustGridCentreX)
        self.GridMidX.grid(row=5,column=1,sticky = NW)
        self.GridMidX.set(self.gridSize[0])
        
        self.GridMidY = Scale(master, from_=0,to=360, orient=HORIZONTAL, label="Grid Center Y", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.AdjustGridCentreY)
        self.GridMidY.grid(row=5,column=1,sticky = NE)
        self.GridMidY.set(self.gridSize[1])
        
        self.listbox = Listbox(master) 
        self.listbox.grid(row=2, column = 2, rowspan=2, sticky = E)  
        
        self.applyTrayBtn = Button(master, text="Load CSVs",command=self.loadCSV)
        self.applyTrayBtn.grid(row=4,column=2,sticky = N)
        
        self.blobMinSize = Scale(master, from_=0, to=100, orient=HORIZONTAL, label="Min Blob Size", length=self.winWidth/3.6, sliderlength=self.winHeight//100, command=self.minBlobSize)
        self.blobMinSize.grid(row=6, column = 0, sticky = W) 
        self.blobMinSize.set(self.blobMinSizeVal)
        
#        self.blobImage = Button(self,text="Seperate the Blobs", command=self.blobDetection)
#        self.blobImage.grid(row=6, column = 0, sticky= E)
        
        self.cellBar = Scale(master, from_=1, to=255, orient=HORIZONTAL, label="Cel-shade Base Value", length=self.winWidth/3.6, sliderlength=self.winHeight//100, command=self.adjustCellBase) 
        self.cellBar.grid(row=2,column=0,sticky = NW) 
        self.cellBar.set(self.cellBase)
        master.report_callback_exception = self.showError
        
    def showError(self, *args):
        err = traceback.format_exception(*args) 
        messagebox.showerror('Exception: ', err)
    
    def flipTrayHor(self): 
        for i in range(len(self.trayCSV)):  
                self.trayCSV[i] = np.fliplr(self.trayCSV[i])
        self.refreshImages()
                
    def flipTrayVer(self): 
        for i in range(len(self.trayCSV)):  
                self.trayCSV[i] = np.flipud(self.trayCSV[i]) 
        self.refreshImages()
                
    def loadCSV(self): 
        if len(self.layers) == 0:
            print("no layers created")
        self.resTrayPopUp = GetTrayCSVs(self.master,self.layers) 
        self.master.wait_window(self.resTrayPopUp.top)  
        self.resTrayPopUp = self.resTrayPopUp.value
        self.resTrayPopUp = self.resTrayPopUp.split("*")
        for i in range(len(self.resTrayPopUp)):
            if self.resTrayPopUp[i] == ' ': 
                self.trayCSV.append(None)
            elif self.resTrayPopUp[i] == '':
                print("blankspace")
            else: 
                tray = np.loadtxt(self.resTrayPopUp[i], delimiter=',',dtype='U')
                print(tray)
                self.trayCSV.append(tray)
        self.refreshImages()
    
    def deleteTray(self): 
        if self.listboxValues.size() > 0:
            self.layers.pop(self.listboxValues.curselection()[0])
            self.listboxValues.delete(self.listboxValues.curselection()[0])
            self.refreshImages
         
    def addTray(self):
        self.listbox.insert(END,"tray part: " + "_" +str(self.topBar.get()))
        
    def exportTrays(self): 
        items = self.listbox.get(0, END)
        numOfOutputs = len(items)
        # create the folders 
        lastOn = 0
        for i in range(numOfOutputs): 
            if os.path.exists(self.workingPath+'/tray' + str(i)) == False:
                os.mkdir(self.workingPath+'/tray' + str(i))
            numberOfFrames = int(items[i].split('_')[1]) 
            infoFile = open(self.workingPath+'/tray' + str(i) +'/' + "a_info.info","w") 
            infoFile.write("pixelsize " + str(self.pixelSizeX)  + " " + str(self.pixelSizeY) +"\n") 
            infoFile.write("offset " + str(self.offsetX) + " " + str(self.offsetY) + "\n") 
            startLast = lastOn
            for o in range(lastOn, numberOfFrames): 
                shutil.copyfile(self.workingPath+'/' + self.imagePaths[o],self.workingPath+'/tray' + str(i)+ '/' +self.imagePaths[o]) 
                infoFile.write('"' + self.imagePaths[o] +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[startLast]) +"\n")
                lastOn = o
            infoFile.close()
        
    def applyTray(self):  
        onTray = False
        self.layers = [] 
        self.listboxValues.delete(0,self.listboxValues.size())
        trayStart = 0
        trayCount = 0
        for i in range(0,self.imageStack.shape[0]): 
            temp = self.imageStack[i,:,:].astype('uint8') 
            temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
            if np.where(temp>0)[0].shape[0] > self.blobMinSizeVal*10:
                if onTray == False: 
                    onTray = True
                    trayStart = i 
                else: 
                    trayCount = trayCount+1 
            else: 
                if onTray == True: 
                    onTray = False 
                    self.layers.append(trayStart + (trayCount//2))
                    trayStart = 0
                    trayCount = 0
        self.gridSize = []
        temp = self.imageStack[0,:,:].astype('uint8')
        for i in range(len(self.layers)): 
            self.gridSize.append(( ((temp.shape[0]//10)*9)//2, ((temp.shape[1]//10)*3)//2))
        for i in range(len(self.layers)):
            self.listboxValues.insert(END,"tray : "+ str(i+1) + "_" +str(self.layers[i]))
        self.refreshImages()
        
    def cellShade(self):
        self.imageStack = self.imageStack-(self.imageStack%self.cellBase)
        self.usedThres = (self.usedThres[0],1)
        self.refreshImages()
    
    def removeblobDensity(self): 
        for i in range(self.imageStack.shape[0]): 
            print("\rprocessing image : " + str(i) + " of " + str(self.imageStack.shape[0]),end=" ")
            img = self.imageStack[i].astype('uint8')
            img = cv.Canny(img,self.threshold,255) 
            img[img != 0] == 1 
            self.imageStack[i] = self.imageStack[i] * img
        self.refreshImages()
    
    def AdjustGridCentreY(self, val): 
        self.gridCenter = (self.gridCenter[0],int(val)) 
        self.refreshImages()
        
    def AdjustGridCentreX(self, val): 
        self.gridCenter = (int(val),self.gridCenter[1])
        self.refreshImages()
    
    def minBlobSize(self,val):
        self.blobMinSizeVal = int(val)
    
    def adjustCellBase(self,val): 
        self.cellBase = int(val) 
        self.refreshImages()
    
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
        
    def adjustGridRotation(self,val):
        self.gridRotation = int(val) 
        self.refreshImages()
        
    def adjustGridSizeHor(self, val): 
        for i in range(len(self.layers)):     
            if self.layers[i] < self.topBar.get() + self.traySize and self.layers[i] > self.topBar.get() - self.traySize: 
                self.gridSize[i] = (int(val),self.gridSize[i][1])
                #print(self.gridSize[i])
        self.refreshImages()
    
    def adjustGridSizeVert(self, val): 
        for i in range(len(self.layers)):     
            if self.layers[i] < self.topBar.get() + self.traySize and self.layers[i] > self.topBar.get() - self.traySize:
                self.gridSize[i] = (self.gridSize[i][0],int(val)) 
        self.refreshImages()
    
    def applyThreshold(self): 
        if self.imageStack is None: 
            return
        self.imageStack[self.imageStack <= self.thresholdMin] = 0    
        self.imageStack[self.imageStack >= self.thresholdMax] = 0 
        self.viewThresholdVar.set(0) 
        self.usedThres = (1,self.usedThres[1])
        self.refreshImages()
        
    def refreshImages(self):  
        if self.imageStack is None: 
            return
        #self.frontSlider(self.frontBar.get()) 
        #self.sideSlider(self.sideBar.get())
        #self.topSlider(self.topBar.get())
        self.updateFront(self.slides[0])
        self.updateSide(self.slides[1])
        self.updateTop(self.slides[2])
    
    def blobDetection(self): 
        if self.imageStack is None:
            return  
        self.imageStack[self.imageStack != 0] = 255 
        self.imageStack = measure.label(self.imageStack) 
        self.imageStack = morphology.remove_small_objects(self.imageStack, min_size=self.blobMinSizeVal)
        self.blobbed = True
        self.refreshImages()
    
    def organiseBlobs(self, unique): 
        numOn = 0 
        for i in range(unique.shape[0]):
            self.imageStack[self.imageStack == unique[i]] == numOn 
            numOn = numOn + 1
    
    def generate3DModel(self,img,path):
        if img is None: 
            return 
        try:
            verts, faces, normals, values = measure.marching_cubes_lewiner((img != 0), 0)#fit this into the model from open3d
            faces=faces+1
            verts  = verts- (verts.min(axis=0)+verts.max(axis=0))//2 
            verts[:,0] = verts[:,0]* self.pixelSizeX # meters to microns 
            verts[:,1] = verts[:,1]* self.pixelSizeY
            verts[:,2] = verts[:,2]* self.pixelSizeZ
            thefile = open(os.path.expanduser('~')+'/meshFull.obj', 'w')
            for item in verts:
              thefile.write("v {0} {1} {2}\n".format(item[0],item[1],item[2]))
            
            for item in normals:
              thefile.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))
            
            for item in faces:
              thefile.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))  
            
            thefile.close()   
             
            pcd_load = o3d.io.read_triangle_mesh(os.path.expanduser('~')+'/meshFull.obj')    
            o3d.io.write_triangle_mesh(path+'/'+"sync.ply", pcd_load)  
            os.remove(os.path.expanduser('~')+'/meshFull.obj')
        except: 
            print("file not working properly") 

    def makeAllPointCloud(self):  
         if self.imageStack is None: 
             return
         verts, faces, normals, values = measure.marching_cubes_lewiner((self.imageStack != 0), 0)#fit this into the model from open3d
         faces=faces+1
         
         thefile = open(os.path.expanduser('~')+'/meshFull.obj', 'w')
         for item in verts:
           thefile.write("v {0} {1} {2}\n".format(item[0]/self.downsampleFactor,item[1],item[2]))
        
         for item in normals:
           thefile.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))
        
         for item in faces:
           thefile.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))  
        
         thefile.close()   
         
         pcd_load = o3d.io.read_triangle_mesh(os.path.expanduser('~')+'/meshFull.obj') 
         o3d.io.write_triangle_mesh(os.path.expanduser('~')+'/sync.ply', pcd_load)  
         os.remove(os.path.expanduser('~')+'/meshFull.obj')
         
    def WriteStacks(self, i, blobName, bounds, imType):
        dirName = "Raw" 
        if imType == 1: #processed 
            dirName = "Pro"
        elif imType == 2: # segmentation  
            dirName = "Seg"
        if os.path.isdir(self.workingPath + '/'+"blobstacks" + '/' + str(blobName) + '/' + dirName) == False:
            os.mkdir(self.workingPath + '/'+"blobstacks"+ '/' + str(blobName) +'/'+dirName) 
            infoFile = open(self.workingPath + '/' + 'blobstacks'+'/' + str(blobName) +'/'+ dirName +'/' + "a_info.info","w") 
            infoFile.write("pixelsize " + str(self.pixelSizeX)  + " " + str(self.pixelSizeY) +"\n") 
            infoFile.write("offset " + str(self.offsetX) + " " + str(self.offsetY) + "\n")   
            p = i
            for o in range(bounds[i][0],bounds[i][1]+1):
                 print("check this +1 doenst break anything")
                 infoFile.write('"' + dirName + self.imagePaths[o] +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[bounds[i][0]]) +"\n") 
                 print("create a flag for raw image loads that cycles through the file again")
                 img = cv.imread(self.workingPath + '/' + self.imagePaths[o],0).astype("uint8")[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
                 if imType == 1: #processed 
                     img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.processSingleTray(img) 
                 elif imType == 2: # segmentation 
                     img  = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#img * (self.processSingleTray(img)//255)
                     img[img >= 1] = 255
                 cv.imwrite(self.workingPath + '/' + 'blobstacks'+'/'+ str(blobName) + '/' + dirName +'/' + dirName + self.imagePaths[o], img)
            infoFile.close()
    
    def exportTiffStacks(self):
         if self.imageStack is None: 
             return
         self.resPopUp = GenerateTiffStackWindow(self.master) 
         self.master.wait_window(self.resPopUp.top)  
         self.resPopUp.value = self.resPopUp.value.split(';')
         generateRaw = int(self.resPopUp.value[0])
         generatePro = int(self.resPopUp.value[1])
         generateMod = int(self.resPopUp.value[2])
         generateSeg = int(self.resPopUp.value[3]) 
         if os.path.isdir(self.workingPath + '/'+"blobstacks") == False:
             os.mkdir(self.workingPath + '/'+"blobstacks")
         self.imageStack = self.ViewImagePreviews(self.imageStack,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
         self.blobDetection()
         unique = np.unique(self.imageStack)
         bounds = [] 
         blobCenters = [] 
         gridCenters = [] 
         gridNames = []
         TrayToBlob = []
         for i in range(unique.shape[0]):  
             print("\r Getting blobs  : "+str(i),end=" ")
             if unique[i] == 0: # background 
                 continue
             currentBlob = np.where(self.imageStack == unique[i])
             Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) 
             Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))*self.downsampleFactor
             X = currentBlob[2].reshape((currentBlob[2].shape[0],1))*self.downsampleFactor
             # padd the bound by the down sample rate
             bounds.append((np.amin(Z),np.amax(Z),np.amin(Y),np.amax(Y),np.amin(X),np.amax(X)))  
             blobCenters.append( ( (np.amin(Z)+np.amax(Z))//2, (np.amin(Y)+np.amax(Y))//2, (np.amin(X)+np.amax(X))//2 ))
         if len(self.layers) > 0:
             self.flipTrayVer()
             for i in range(len(self.layers)): 
                    topInterp = np.linspace((self.TL[0],self.TL[1]),(self.TR[0],self.TR[1]),num=self.trayCSV[i].shape[0]+1,endpoint=True,dtype=('int32'))
                    bottomInterp = np.linspace((self.BL[0],self.BL[1]),(self.BR[0],self.BR[1]),num=self.trayCSV[i].shape[0]+1,endpoint=True,dtype=('int32'))
                    for o in range(self.trayCSV[i].shape[0]):
                        #interpolate between the top and bottom downward looping to fill the gaps 
                        cols1 = np.linspace(topInterp[o],bottomInterp[o],num=self.trayCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                        cols2 = np.linspace(topInterp[o+1],bottomInterp[o+1],num=self.trayCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))#0+2
                        for q in range(self.trayCSV[i].shape[1]):#cols1.shape[0]
                            X = (cols1[q][0] + cols2[q][0])//2 
                            Y = (cols1[q][1] + cols2[q][1])//2
                            gridCenters.append([self.layers[i],Y,X])
                            gridNames.append(self.trayCSV[i][o][q])
                    # create a colleration between blobs and spread sheet
                    
             for p in range(len(blobCenters)):
                  print(p)
                  dist = 999999999
                  refPoint = 0
                  #  loop round and get the lowest distance
                  for o in range(len(gridCenters)): 
                      distance = math.sqrt(
                                       (blobCenters[p][0]-gridCenters[o][0])*(blobCenters[p][0]-gridCenters[o][0]) +
                                       (blobCenters[p][1]-gridCenters[o][1])*(blobCenters[p][1]-gridCenters[o][1]) +
                                       (blobCenters[p][2]-gridCenters[o][2])*(blobCenters[p][2]-gridCenters[o][2]))
                      if dist > distance:
                          dist = distance
                          refPoint = o
                  if (refPoint in TrayToBlob) == False:
                      print("here")
                      indx = 1 
                      gotName = True
                      while(gotName):
                          print(gotName)
                          if gridNames[refPoint]+'_'+str(indx) in gridNames:
                              indx = indx+1
                          else: 
                              gridNames.append(gridNames[refPoint]+'_'+str(indx)) 
                              refPoint = len(gridNames)-1
                              gotName = False
                  TrayToBlob.append(refPoint) 
             # cycle through and create directories   
         self.flipTrayVer()
         for i in range(len(bounds)):  # was grid names
                 if len(self.layers) > 0:
                     blobName = gridNames[i]
                 else: 
                     blobName = 'blob'+ str(i)
                 print("\r making Directories  : "+str(i),end=" ")
                 if os.path.isdir(self.workingPath + '/'+"blobstacks" + '/' + str(blobName) ) == False:
                     os.mkdir(self.workingPath + '/'+"blobstacks"+ '/' + str(blobName))  
                 if generateRaw == 1: 
                     self.WriteStacks(i, blobName, bounds, 0)
                 if generatePro == 1: 
                     self.WriteStacks(i, blobName, bounds, 1)
                 if generateSeg == 1:   
                     self.WriteStacks(i, blobName, bounds, 2)
                     
         if generateMod == 1:
                  blobs = os.listdir(self.workingPath + '/' + 'blobstacks') 
                  for i in range(len(blobs)): 
                      folders = os.listdir(self.workingPath + '/' + 'blobstacks' + '/' + blobs[i])
                      for o in range(len(folders)):  
                          # folder containing the tiff stacks
                          stk = self.LoadImageStack(self.workingPath + '/' + 'blobstacks' + '/' + blobs[i]+ '/'+folders[o]) 
                          self.generate3DModel(stk,self.workingPath + '/' + 'blobstacks' + '/' + blobs[i]+ '/'+folders[o])
         
    def ViewImagePreviews(self,img, viewThres, viewCell, downSample, downFactor, thresMax, thresMin, cell):
        if viewCell == 1: 
           img = img-(img%cell)
        if viewThres == 1: 
            img[img >= thresMax] = 0   
            img[img <= thresMin] = 0
        return img
    
    def frontSlider(self,val): 
        # right image
        temp = self.imageStack[:,:,int(val)-1]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB) 

        for i in range(len(self.layers)):
            temp = cv.line(temp,pt1=(0,self.layers[i]),pt2=(temp.shape[1],self.layers[i]),color=(255,255,0),thickness=5) 
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        cv.imshow("front", temp)
    
    def sideSlider(self,val): 
        temp = self.imageStack[:,int(val)-1,:]
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        cv.imshow("side", temp)
    
    def rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.
        """ 
        angle = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return int(qx),int(qy)
    
    def putGridOnImage(self,temp, val): 
        for i in range(len(self.layers)): 
            if self.layers[i] < int(val) + self.traySize and self.layers[i] > int(val) - self.traySize:
                self.ScaleGridBarV.set(self.gridSize[i][1]) 
                self.ScaleGridBarH.set(self.gridSize[i][0])

                halfTemp = (self.gridCenter[0],self.gridCenter[1])
                self.TL = (halfTemp[0]-self.gridSize[i][0],halfTemp[1]-self.gridSize[i][1])
                self.TR = (halfTemp[0]+self.gridSize[i][0],halfTemp[1]-self.gridSize[i][1]) 
                self.BL = (halfTemp[0]-self.gridSize[i][0],halfTemp[1]+self.gridSize[i][1])
                self.BR = (halfTemp[0]+self.gridSize[i][0],halfTemp[1]+self.gridSize[i][1])
                self.TL = self.rotate(halfTemp,self.TL,self.gridRotation) 
                self.TR = self.rotate(halfTemp,self.TR,self.gridRotation) 
                self.BL = self.rotate(halfTemp,self.BL,self.gridRotation)
                self.BR = self.rotate(halfTemp,self.BR,self.gridRotation) 
                if i < len(self.trayCSV):
                    temp = cv.putText(temp,self.trayCSV[i][0][0],self.TL,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    temp = cv.putText(temp,self.trayCSV[i][self.trayCSV[i].shape[0]-1][0],self.BL,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    temp = cv.putText(temp,self.trayCSV[i][0][self.trayCSV[i].shape[1]-1],self.TR,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
                    temp = cv.putText(temp,self.trayCSV[i][self.trayCSV[i].shape[0]-1][self.trayCSV[i].shape[1]-1],self.BR,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    
                    rowsY = np.linspace((self.TL[0],self.TL[1],self.TR[0],self.TR[1]),(self.BL[0],self.BL[1],self.BR[0],self.BR[1]), num=self.trayCSV[i].shape[0]+1, endpoint=True,dtype=('int32')) 
                    rowsX = np.linspace((self.TL[0],self.TL[1],self.BL[0],self.BL[1]),(self.TR[0],self.TR[1],self.BR[0],self.BR[1]), num=self.trayCSV[i].shape[1]+1, endpoint=True,dtype=('int32')) 
                    for o in range(self.trayCSV[i].shape[0]+ 1): # creates the rows + 2 as we need the number of blocks
                        pnt1 = (rowsY[o][0],rowsY[o][1])
                        pnt2 = (rowsY[o][2],rowsY[o][3])
                        temp = cv.line(temp,pt1=pnt1,pt2=pnt2,color=(0,255,0),thickness=1)
                    for o in range(self.trayCSV[i].shape[1]+1):
                        pnt1 = (rowsX[o][0],rowsX[o][1])
                        pnt2 = (rowsX[o][2],rowsX[o][3])
                        temp = cv.line(temp,pt1=pnt1,pt2=pnt2,color=(0,255,0),thickness=3) 
                        # get the accrow values for the top row and bottom
                        topInterp = np.linspace((self.TL[0],self.TL[1]),(self.TR[0],self.TR[1]),num=self.trayCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                        bottomInterp = np.linspace((self.BL[0],self.BL[1]),(self.BR[0],self.BR[1]),num=self.trayCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                    for o in range(topInterp.shape[0]):# down
                        #interpolate between the top and bottom downward looping to fill the gaps 
                        cols = np.linspace(topInterp[o],bottomInterp[o],num=self.trayCSV[i].shape[0]+1,endpoint=True,dtype=('int32')) #inter top i and bottom i by the shape 
                        for q in range(cols.shape[0]):
                            # draw circle at cols 
                            temp = cv.circle(temp,(cols[q][0],cols[q][1]),2,(255,0,0)) 
        return temp
    
    def topSlider(self,val): 
        # left image
        temp = self.imageStack[int(val)-1,:,:]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB)
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        temp = self.putGridOnImage(temp,val)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        cv.imshow("top", temp)

    '''def image_resize(self,image, width = None, height = None, inter = cv.INTER_AREA): 
        # by thewaywewere https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv accessed 11/11/19
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]
        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image
        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)
        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))
        # resize the image
        resized = cv.resize(image, dim, interpolation = inter)
        # return the resized image
        return resized'''
    
    def generateInfoFile(self):  
        self.resPopUp = InfoWindow(self.master) 
        self.master.wait_window(self.resPopUp.top)  
        resolution = self.resPopUp.value.split(";") 
        if len(resolution) < 3: 
            print("do error")
            return
        path = filedialog.askdirectory(title = "select image dir")  
        paths = os.listdir(path)
        infoFile = open(path+"/a_info.info","w") 
        infoFile.write("pixelsize " + resolution[0] + " " + resolution[1]+"\n") 
        infoFile.write("offset 0 0\n") 
        for i in range(len(paths)):
            if (paths[i].lower().endswith("tif") or paths[i].lower().endswith("jpg") or paths[i].lower().endswith("png")):
                infoFile.write('"' + paths[i]+'" ' + str(float(resolution[2])*i) +"\n") 
        infoFile.close()
    
    def LoadImageStack(self, path):
        imgstk = None 
        paths = os.listdir(path) 
        infoFile = ""
        if len(paths) < 1: 
            showinfo("File Directory empty",path+ " : contains no files!")
            return imgstk
        for i in range(len(paths)):
            if paths[i].endswith(".info"): 
                infoFile = paths[i] 
                break 
        if infoFile == "":
            showinfo("No Scanner info file", path + " : contains no .info file from the scanner!")
            return imgstk
        
        info = open(path+'/'+infoFile,'r') 
        
        info = info.readlines()
        
        imagePaths = [] 
        imagesHeightSlice = []
        pixelSizeX = 0 
        pixelSizeY = 0 
        pixelSizeZ = 0
        offsetX = 0 
        offsetY = 0 
        
        for i in range(len(info)): 
            temp = info.pop(0)
            if temp.startswith('p'): 
                temp = temp.split(" ") 
                pixelSizeX = float(temp[1])
                pixelSizeY = float(temp[2])
            elif temp.startswith('o'):
                temp = temp.split(" ") 
                offsetX = float(temp[1])
                offsetY = float(temp[2])
            elif temp.startswith('"'):
                temp = temp.replace('"','') 
                temp = temp.split(" ") 
                imagePaths.append(temp[0])
                imagesHeightSlice.append(float(temp[1]))  
        imgstk = None
        if os.path.exists(path + '/' + imagePaths[0]):
            temp = cv.imread(path + '/' + imagePaths[0],0).astype("uint8")   
            imgstk = np.zeros((len(imagePaths),temp.shape[0],temp.shape[1])).astype("uint8")
            for i in range(len(imagePaths)):
                imgstk[i] = cv.imread(path + '/' + imagePaths[i],0).astype("uint8")
        else: 
            imgstk = np.zeros((10,10,10)) 
            print("this is an error")
        pixelSizeZ = imagesHeightSlice[1]
        return imgstk
        
    def loadRawStack(self):
        path = filedialog.askopenfilename(filetypes = (("raw files","*.raw"),("all files","*.*")))
        print(path)
        if path == "": 
            # file loading canceled
            return
        print("loading images")
        self.blobbed = False
        self.imageStack = None
        self.workingPath = os.path.dirname(path)
        self.resPopUp = RawInfoWindow(self.master) 
        self.master.wait_window(self.resPopUp.top)  
        resolution = self.resPopUp.value.split(";") 
        if len(resolution) < 4: 
            print("do error")
            return
        resolution[0] = int(resolution[0])
        resolution[1] = int(resolution[1])
        resolution[2] = int(resolution[2])
        resolution[3] = int(resolution[3])
        print(resolution)
        bitType = np.uint8
        if(resolution[3] == 16):
            bitType = np.uint16
        elif(resolution[3] == 32):
            bitType = np.uint32
        elif(resolution[3] == 64):
            bitType = np.uint64
        image = open(path)
        self.imageStack = np.zeros((resolution[2],resolution[1],resolution[0]), dtype = "uint8")
        img_size = resolution[0] * resolution[1]
        for i in range(resolution[2]):
            img = np.fromfile(image, dtype = bitType, count = img_size)
            img.shape = (resolution[1],resolution[0])
            img = img * (255/img.max())
            self.imageStack[i] = img
            #cv.imshow("front", img)
            #cv.waitKey(1)
            #img = img.astype("uint8")
        image.close()
        self.imagePaths = []
        self.imagesHeightSlice = []
        self.pixelSizeX = resolution[0] 
        self.pixelSizeY = resolution[1] 
        self.pixelSizeZ = resolution[2]
        self.offsetX = 0 
        self.offsetY = 0 
        for i in range(resolution[2]):
            self.imagesHeightSlice.append(i*self.pixelSizeZ)
        self.setInitGraphs()
        
    def loadImages(self):
        path = filedialog.askdirectory() 
        if path == "": 
            # file loading canceled
            return
        print("loading images")
        self.blobbed = False
        self.imageStack = None 
        paths = os.listdir(path) 
        self.workingPath = path
        infoFile = ""
        
        if len(paths) < 1: 
            showinfo("File Directory empty",path+ " : contains no files!")
            return 
                
        for i in range(len(paths)):
            if paths[i].endswith(".info"): 
                infoFile = paths[i] 
                break 
        
        if infoFile == "":
            showinfo("No Scanner info file", path + " : contains no .info file from the scanner!")
            return
        
        self.resPopUp = DownsampleWindow(self.master) 
        self.master.wait_window(self.resPopUp.top)
        resolution = self.resPopUp.value 
        if len(resolution) < 1: 
            resolution = "1"
            return
        
        self.downsampleFactor = int(resolution)
        info = open(path+'/'+infoFile,'r')  
        info = info.readlines()
        
        self.imagePaths = [] 
        self.imagesHeightSlice = []
        self.pixelSizeX = 0 
        self.pixelSizeY = 0 
        self.pixelSizeZ = 0
        self.offsetX = 0 
        self.offsetY = 0 
        print("this code is a duplicat as load image stack, calle the load stack be change to add if downsampling")
        for i in range(len(info)): 
            temp = info.pop(0)
            if temp.startswith('p'): 
                temp = temp.split(" ") 
                self.pixelSizeX = float(temp[1])
                self.pixelSizeY = float(temp[2])
            elif temp.startswith('o'):
                temp = temp.split(" ") 
                self.offsetX = float(temp[1])
                self.offsetY = float(temp[2])
            elif temp.startswith('"'):
                temp = temp.replace('"','') 
                temp = temp.split(" ") 
                self.imagePaths.append(temp[0])
                self.imagesHeightSlice.append(float(temp[1])) 
        self.pixelSizeZ = self.imagesHeightSlice[1]
        temp = cv.imread(path + '/' + self.imagePaths[0],0).astype("uint8")   
        self.imageStack = np.zeros((len(self.imagePaths),temp.shape[0]//self.downsampleFactor,temp.shape[1]//self.downsampleFactor)).astype("uint8")
        for i in range(len(self.imagePaths)):        
            print("\rprocessing image : " + str(i) + " of " + str(len(self.imagePaths)),end=" ")
            if os.path.isfile(path + '/' + self.imagePaths[i]) == False: 
                showinfo("Image not found", path + '/' + self.imagePaths[i] + " : does not exist check the file if at this location")
                return
            self.imageStack[i] = cv.resize(cv.imread(path + '/' + self.imagePaths[i],0).astype("uint8"),(temp.shape[1]//self.downsampleFactor,temp.shape[0]//self.downsampleFactor))
            tempim = cv.cvtColor(self.imageStack[i],cv.COLOR_GRAY2RGB)
            tempim = cv.putText(tempim,(str(i+1) + ' / ' + str(len(self.imagePaths))),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
            cv.imshow("top",tempim) 
            cv.waitKey(1)
        # get the bottom image (default in the scan)
        self.setInitGraphs()
            
    def setInitGraphs(self):
        self.imgTop = self.imageStack[0,:,:]
        #self.imgTopSize = self.imgTop.shape
        self.gridSize = ( ((self.imgTop.shape[0]//10)*9)//2, ((self.imgTop.shape[1]//10)*3)//2)
        
        self.ScaleGridBarH = Scale(self.master, from_=0, to=(self.imgTop.shape[0]//2), orient=HORIZONTAL, label="Scale Tray Horizontal", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.adjustGridSizeHor) 
        self.ScaleGridBarH.grid(row=4,column=1,sticky = NW) 
        self.ScaleGridBarH.set(self.gridSize[0])
        
        self.ScaleGridBarV = Scale(self.master, from_=0, to=(self.imgTop.shape[0]//2), orient=HORIZONTAL, label="Scale Tray Vertical", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.adjustGridSizeVert) 
        self.ScaleGridBarV.grid(row=4,column=1,sticky = NE) 
        self.ScaleGridBarV.set(self.gridSize[1])
        
        self.GridMidX = Scale(self.master, from_=0,to=(self.imgTop.shape[0]), orient=HORIZONTAL, label="Grid center X", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.AdjustGridCentreX)
        self.GridMidX.grid(row=5,column=1,sticky = NW)
        self.GridMidX.set(self.imgTop.shape[0]//2)
        
        self.GridMidY = Scale(self.master, from_=0,to=(self.imgTop.shape[1]), orient=HORIZONTAL, label="Grid center Y", length=self.winWidth/6, sliderlength=self.winHeight//100, command=self.AdjustGridCentreY)
        self.GridMidY.grid(row=5,column=1,sticky = NE)
        self.GridMidY.set(self.imgTop.shape[1]//2)
        
        self.gridCenter = (self.imgTop.shape[0]//2,self.imgTop.shape[1]//2)
        
        self.imgTop = cv.cvtColor(self.imgTop,cv.COLOR_GRAY2RGB)
        #cv.imshow("top",self.imgTop)
        
        self.imgSide = self.imageStack[:,0,:]
        #self.imgSideSize = self.imgSide.shape
        #self.imgSide = cv.cvtColor(self.imgSide,cv.COLOR_GRAY2RGB) 
        #cv.imshow("side", self.imgSide)
        
        self.imgFront = self.imageStack[:,:,0] 
        #self.imgFrontSize = self.imgFront.shape
        #self.imgFront = cv.cvtColor(self.imgFront,cv.COLOR_GRAY2RGB)
        #cv.imshow("front", self.imgFront)
        
        # bars for showing scale
        #self.frontBar = Scale(self.master, from_=1, to=self.imageStack.shape[2], orient=HORIZONTAL, length=self.winWidth/3, sliderlength=self.winHeight//100, command=self.frontSlider)
        #self.frontBar.grid(row=1,column=2)
        #self.frontBar.set(self.imageStack.shape[2]//2)
        #self.sideBar = Scale(self.master, from_=1, to=self.imageStack.shape[1], orient=HORIZONTAL, length=self.winWidth/3, sliderlength=self.winHeight//100, command=self.sideSlider)
        #self.sideBar.grid(row=1,column=1) 
        #self.sideBar.set(self.imageStack.shape[1]//2)
        #self.topBar = Scale(self.master, from_=1, to=self.imageStack.shape[0], orient=HORIZONTAL, length=self.winWidth/3, sliderlength=self.winHeight//100, command=self.topSlider)
        #self.topBar.grid(row=1,column=0) 
        #self.topBar.set(self.imageStack.shape[0]//2)
        
        
        ####### new code #######
        color = 'lightgoldenrodyellow'
        self.figFront, self.axFront = plt.subplots()
        self.figFront.canvas.set_window_title('Front slice')
        plt.subplots_adjust(bottom=0.25)
        self.lFront = plt.imshow(self.imgFront)
        self.axFront.margins(x=0)
        axes = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=color)
        self.frontSlide= Slider(axes, 'Front', 0, self.imageStack.shape[2]-1, valinit=0, valstep=1 )
        self.frontSlide.on_changed(self.updateFront)
        
        self.figSide, self.axSide = plt.subplots()
        self.figSide.canvas.set_window_title('Side slice')
        plt.subplots_adjust(bottom=0.25)
        self.lSide = plt.imshow(self.imgSide)
        self.axSide.margins(x=0)
        axes2 = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=color)
        self.sideSlide = Slider(axes2, 'Side Slices', 0, self.imageStack.shape[1], valinit=0, valstep=1 )
        self.sideSlide.on_changed(self.updateSide)
        
        self.figTop, self.axTop = plt.subplots()
        self.figTop.canvas.set_window_title('Top slice')
        plt.subplots_adjust(bottom=0.25)
        self.lTop = plt.imshow(self.imgTop)
        self.axTop.margins(x=0)
        axes3 = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=color)
        self.topSlide = Slider(axes3, 'Top Slices', 0, self.imageStack.shape[0]-1, valinit=0, valstep=1 )
        self.topSlide.on_changed(self.updateTop)
        
    def updateFront(self, val):
        self.slides[0] = int(val)
        temp = self.imageStack[:,:,int(val)-1]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB) 

        for i in range(len(self.layers)):
            temp = cv.line(temp,pt1=(0,self.layers[i]),pt2=(temp.shape[1],self.layers[i]),color=(255,255,0),thickness=5) 
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        self.lFront.set_data(temp)
        self.figFront.canvas.draw_idle()
        
    def updateSide(self, val):
        self.slides[1] = int(val)
        temp = self.imageStack[:,int(val)-1,:]
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        self.lSide.set_data(temp)
        self.figSide.canvas.draw_idle()
        
    def updateTop(self, val):
        self.slides[2] = int(val)
        temp = self.imageStack[int(val)-1,:,:]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB)
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        temp = self.putGridOnImage(temp,int(val))
        if self.blobbed == True:
            temp[temp >= 1] = 255
        self.lTop.set_data(temp)
        self.figTop.canvas.draw_idle()
root = tk.Tk()
app = ScanOBJGenerator(root) 
root.mainloop()