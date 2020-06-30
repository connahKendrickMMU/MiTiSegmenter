from tkinter import filedialog
from tkinter import * 
from PIL import Image, ImageTk  
from tkinter.messagebox import showinfo 
from skimage import measure, morphology 
import math
import numpy as np  
import cv2 as cv
import os
import open3d as o3d 
import pandas as pd
import shutil
import time

# our files
from PopUpClasses import *

####### version info #######
# python 3.6 # tkinter # PIL # numpy = 1.16.2 # cv2 = 4.1.1 # os # open3d = 0.8.0.0 # random   

class ScanOBJGenerator(Tk): 
    # initialisation 
    def __init__(self): 
        super().__init__()  
        self.threshold = 40  
        self.blobMinSizeVal = 50
        self.downsampleFactor = 4
        self.cellBase = 40
        self.usedThres =(0,0)
        self.imgTopSize = (0,0) 
        self.imgSideSize = (0,0) 
        self.imgFrontSize = (0,0) 
        self.maxSize =self.winfo_screenwidth()//3 
        self.gridSize = (0,0)
        self.gridCenter = (0,0)
        self.gridRotation = 0
        self.viewThresholdVar = IntVar() 
        self.viewCellVar = IntVar()
        self.layers = []
        self.traySize = 50
        self.trayCSV = [] 
        self.init_GUI() 
        self.workingPath = "" 
        self.blobCenterOfMass = []
        self.TL = 0 
        self.TR = 0
        self.BL = 0
        self.BR = 0
        self.blobbed = False
    def init_GUI(self):
        #main window title and size
        self.title("MiTiSegmenter") 
        self.minsize(self.winfo_screenwidth(),self.winfo_screenheight())
        self.imageStack = None 
        # tool bar
        menubar = Menu(self)  
        self.config(menu=menubar) 
        fileMenu = Menu(menubar)  
        fileMenu.add_command(label="Load Images", command=self.loadImages) 
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
        self.panalFront = None 
        self.panalSide = None 
        self.panalTop = None 
        self.frontBar = None
        self.sideBar = None
        self.topBar = None 
        
        # thresholding          
        self.thresholdBar = Scale(self, from_=0, to=255, orient=HORIZONTAL, label="Threshold Value", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=self.adjustThreshold) 
        self.thresholdBar.grid(row=3,column=0,sticky = W) 
        self.thresholdBar.set(self.threshold)
        
        self.viewThresholdCheck = Checkbutton(self,text="View Threshold Image", variable = self.viewThresholdVar, command=self.refreshImages) 
        self.viewThresholdCheck.grid(row=4, column = 0, sticky = NE)  
          
        self.applyThresholdBtn = Button(self,text="Apply Threshold",command=self.applyThreshold)
        self.applyThresholdBtn.grid(row=3,column=0,sticky = E) 

        # traying
        self.listboxValues = Listbox(self) 
        self.listboxValues.grid(row=2, column = 2, rowspan=2, sticky = W)
        
        self.applyTrayBtn = Button(self, text="Apply Traying",command=self.applyTray)
        self.applyTrayBtn.grid(row=2,column=1,sticky = N)
        
        self.removeTrayBtn = Button(self, text="Delete Tray",command=self.deleteTray)
        self.removeTrayBtn.grid(row=2, column=1,sticky=W)
        
        self.addTrayBtn = Button(self, text="Add Tray",command=self.addTray)
        self.addTrayBtn.grid(row=2, column=1,sticky=E)
        
        self.RotateGridBar = Scale(self, from_=0, to=360, orient=HORIZONTAL, label="Rotate Tray", length=self.winfo_screenwidth()/3, sliderlength=self.winfo_screenheight()//100, command=self.adjustGridRotation) 
        self.RotateGridBar.grid(row=3,column=1,sticky = NW) 
        self.RotateGridBar.set(self.gridRotation)
        
        self.ScaleGridBarH = Scale(self, from_=0, to=360, orient=HORIZONTAL, label="Scale Tray Horizontal", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.adjustGridSizeHor) 
        self.ScaleGridBarH.grid(row=4,column=1,sticky = NW) 
        self.ScaleGridBarH.set(self.gridSize[0])
        
        self.ScaleGridBarV = Scale(self, from_=0, to=360, orient=HORIZONTAL, label="Scale Tray Vertical", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.adjustGridSizeVert) 
        self.ScaleGridBarV.grid(row=4,column=1,sticky = NE) 
        self.ScaleGridBarV.set(self.gridSize[1])
        
        self.GridMidX = Scale(self, from_=0,to=360, orient=HORIZONTAL, label="Grid Center X", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.AdjustGridCentreX)
        self.GridMidX.grid(row=5,column=1,sticky = NW)
        self.GridMidX.set(self.gridSize[0])
        
        self.GridMidY = Scale(self, from_=0,to=360, orient=HORIZONTAL, label="Grid Center Y", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.AdjustGridCentreY)
        self.GridMidY.grid(row=5,column=1,sticky = NE)
        self.GridMidY.set(self.gridSize[1])
        
        self.listbox = Listbox(self) 
        self.listbox.grid(row=2, column = 2, rowspan=2, sticky = E)  
        
        self.applyTrayBtn = Button(self, text="Load CSVs",command=self.loadCSV)
        self.applyTrayBtn.grid(row=4,column=2,sticky = N)
        
        # blobing 
        self.removeDensity = Button(self,text="Remove Blob Interior", command=self.removeblobDensity) 
        self.removeDensity.grid(row=4, column = 0, sticky = NW)
        
        self.blobMinSize = Scale(self, from_=0, to=100, orient=HORIZONTAL, label="Min Blob Size", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=self.minBlobSize)
        self.blobMinSize.grid(row=5, column = 0, sticky = W) 
        self.blobMinSize.set(self.blobMinSizeVal)
        
        self.blobImage = Button(self,text="Seperate the Blobs", command=self.blobDetection)
        self.blobImage.grid(row=5, column = 0, sticky= E)
        
        self.cellBar = Scale(self, from_=0, to=255, orient=HORIZONTAL, label="Cel-shade Base Value", length=self.winfo_screenwidth()/3.6, sliderlength=self.winfo_screenheight()//100, command=self.adjustCellBase) 
        self.cellBar.grid(row=2,column=0,sticky = NW) 
        self.cellBar.set(self.cellBase)
        
        self.viewCellCheck = Checkbutton(self,text="View Cel Image", variable = self.viewCellVar, command=self.refreshImages) 
        self.viewCellCheck.grid(row=2,column=0,sticky = SE)#  row=2,column=0,sticky = SE
        
        self.applyCellBtn = Button(self,text="Apply Cel-Shade",command=self.cellShade)
        self.applyCellBtn.grid(row=2,column=0,sticky = E) 
    
    def flipTrayHor(self): 
        for i in range(len(self.trayCSV)):  
                self.trayCSV[i] = np.fliplr(self.trayCSV[i])
        self.refreshImages()
                
    def flipTrayVer(self): 
        for i in range(len(self.trayCSV)):  
                self.trayCSV[i] = np.flipud(self.trayCSV[i]) 
        self.refreshImages()
                
    def loadCSV(self): 
        #print("create checkbox that gets the path of each of the csv s, : cannot be in a file name") 
        if len(self.layers) == 0:
            print("no layers created")

        self.resTrayPopUp = GetTrayCSVs(self,self.layers) 
        self.wait_window(self.resTrayPopUp.top)  
        self.resTrayPopUp = self.resTrayPopUp.value
        self.resTrayPopUp = self.resTrayPopUp.split("*")
        for i in range(len(self.resTrayPopUp)):
            #print(self.resTrayPopUp[i])
            if self.resTrayPopUp[i] == ' ': 
                self.trayCSV.append(None)
            elif self.resTrayPopUp[i] == '':
                print("blankspace")
            else: 
                tray = pd.read_csv(self.resTrayPopUp[i],header=None)
                tray = np.array(tray.values)  
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
        trayCount = 0
        onTray = False
        self.layers = [] 
        self.listboxValues.delete(0,self.listboxValues.size())
        maxValue = 0
        layer = 0
        loopRate = self.downsampleFactor
        if loopRate == 0: 
            loopRate = 1
        for i in range(0,self.imageStack.shape[0],loopRate): 
            temp = self.imageStack[i,:,:].astype('uint8')
            #print(np.where(temp>0)[0].shape) 
            if np.where(temp>0)[0].shape[0] > self.blobMinSizeVal*10: 
                if onTray == False: 
                    onTray = True
                    trayCount = trayCount + 1 
                if np.where(temp>0)[0].shape[0] > maxValue: 
                    maxValue = np.where(temp>0)[0].shape[0]
                    layer = i
            elif onTray == True: 
                self.layers.append(layer) 
                layer = 0 
                maxValue = 0
                onTray = False 
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
    
    def adjustThreshold(self,val): 
        self.threshold = int(val)
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
        self.imageStack[self.imageStack <= self.threshold] = 0  
        self.viewThresholdVar.set(0) 
        self.usedThres = (1,self.usedThres[1])
        self.refreshImages()
        
    def refreshImages(self):  
        if self.imageStack is None: 
            return
        self.frontSlider(self.frontBar.get()) 
        self.sideSlider(self.sideBar.get())
        self.topSlider(self.topBar.get())
    
    def blobDetection(self): 
        if self.imageStack is None:
            return  
        self.imageStack[self.imageStack >= self.threshold] = 255 
        self.imageStack = measure.label(self.imageStack) 
        self.imageStack = morphology.remove_small_objects(self.imageStack, min_size=self.blobMinSizeVal)  
        self.viewThresholdVar.set(0)
        self.viewThresholdCheck.config(state="disabled")
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
            #print("file written")
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
         #o3d.visualization.draw_geometries([pcd_load])   
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
                 img = cv.imread(self.workingPath + '/' + self.imagePaths[o],0).astype("uint8")[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
                 if imType == 1: #processed 
                     img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.threshold,self.cellBase)#self.processSingleTray(img) 
                 elif imType == 2: # segmentation 
                     img  = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.threshold,self.cellBase)#img * (self.processSingleTray(img)//255)
                     img[img >= 1] = 255
                 cv.imwrite(self.workingPath + '/' + 'blobstacks'+'/'+ str(blobName) + '/' + dirName +'/' + dirName + self.imagePaths[o], img)
            infoFile.close()
    
    def exportTiffStacks(self):
         start = time.perf_counter() 
        
         if self.imageStack is None: 
             return
         self.resPopUp = GenerateTiffStackWindow(self) 
         self.wait_window(self.resPopUp.top)  
         self.resPopUp.value = self.resPopUp.value.split(';')
         generateRaw = int(self.resPopUp.value[0])
         generatePro = int(self.resPopUp.value[1])
         generateMod = int(self.resPopUp.value[2])
         generateSeg = int(self.resPopUp.value[3]) 
         #nt("do the segmentation tiffs")
         if os.path.isdir(self.workingPath + '/'+"blobstacks") == False:
             os.mkdir(self.workingPath + '/'+"blobstacks")
         unique = np.unique(self.imageStack)
         bounds = [] 
         blobCenters = [] 
         gridCenters = [] 
         gridNames = []
         for i in range(unique.shape[0]):  
             print("\r Getting blobs  : "+str(i),end=" ")
             if unique[i] == 0: # background 
                 continue
             
             currentBlob = np.where(self.imageStack == unique[i])
             Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) 
             Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))*self.downsampleFactor
             X = currentBlob[2].reshape((currentBlob[2].shape[0],1))*self.downsampleFactor  
             #bounds.append((np.amin(Z),np.amax(Z),np.amin(Y),np.amax(Y),np.amin(X),np.amax(X))) 
             # padd the bound by the down sample rate
             bounds.append((np.amin(Z)-self.downsampleFactor,np.amax(Z)+self.downsampleFactor,np.amin(Y)-self.downsampleFactor,np.amax(Y)+self.downsampleFactor,np.amin(X)-self.downsampleFactor,np.amax(X)+self.downsampleFactor))  
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
                    TrayToBlob = []
                    for i in range(len(blobCenters)):
                         dist = 999999999
                         refPoint = 0
                         #  loop round and get the lowest distance
                         for o in range(len(gridCenters)): 
                             distance = math.sqrt(
                                              (blobCenters[i][0]-gridCenters[o][0])*(blobCenters[i][0]-gridCenters[o][0]) +  
                                              (blobCenters[i][1]-gridCenters[o][1])*(blobCenters[i][1]-gridCenters[o][1]) + 
                                              (blobCenters[i][2]-gridCenters[o][2])*(blobCenters[i][2]-gridCenters[o][2])) 
                             if dist > distance: 
                                 dist = distance   
                                 refPoint = o
                         if refPoint in TrayToBlob:
                             indx = 1 
                             gotName = True
                             while(gotName): 
                                 if gridNames[refPoint]+str(indx) in gridNames:
                                     indx = indx+1
                                 else: 
                                     gridNames.append(gridNames[refPoint]+str(indx)) 
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
         end = time.perf_counter()
         print(end - start)
         
    def ViewImagePreviews(self,img, viewThres, viewCell, downSample, downFactor, thres, cell):
        #if downSample: 
            #img = np.delete(img,list(range(0,img.shape[0],downFactor)),axis=0) 
            #print("no downsample anymore")
        if viewCell == 1: 
           img = img-(img%cell)
        if viewThres == 1: 
            img[img <= thres] = 0  
        return img
    
    def frontSlider(self,val): 
        # right image
        temp = self.imageStack[:,:,int(val)-1].astype('uint8') 
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB) 

        for i in range(len(self.layers)):
            temp = cv.line(temp,pt1=(0,self.layers[i]),pt2=(temp.shape[1],self.layers[i]),color=(255,255,0),thickness=5) 
        temp = self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),True,self.downsampleFactor,self.threshold,self.cellBase)
        temp = cv.resize(temp,self.imgFrontSize) 
        if self.blobbed == True:
            temp[temp >= 1] = 255
        temp = Image.fromarray(temp) 
        self.imgFront = ImageTk.PhotoImage(image=temp) 
        self.panalFront.configure(image=self.imgFront) 
        self.panalFront.image = self.imgFront

    
    def sideSlider(self,val): 
        temp = self.imageStack[:,int(val)-1,:].astype('uint8')
        temp = self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),True,self.downsampleFactor,self.threshold,self.cellBase)
        temp = cv.resize(temp,self.imgSideSize)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        temp = Image.fromarray(temp)  
        self.imgSide = ImageTk.PhotoImage(image=temp) 
        self.panalSide.configure(image=self.imgSide) 
        self.panalSide.image = self.imgSide
    
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
                #print(self.trayCSV[i])
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
        temp = self.imageStack[int(val)-1,:,:].astype('uint8') 
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB)
        temp = self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),False,self.downsampleFactor,self.threshold,self.cellBase)
        temp = self.putGridOnImage(temp,val)                
        temp = cv.resize(temp,self.imgTopSize)  
        if self.blobbed == True:
            temp[temp >= 1] = 255
        temp = Image.fromarray(temp)  
        self.imgTop = ImageTk.PhotoImage(image=temp)  
        self.panalTop.configure(image=self.imgTop) 
        self.panalTop.image = self.imgTop

    def image_resize(self,image, width = None, height = None, inter = cv.INTER_AREA): 
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
        return resized
    
    def generateInfoFile(self):  
        self.resPopUp = InfoWindow(self) 
        self.wait_window(self.resPopUp.top)  
        #print(self.resPopUp.value)
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
                #print(path + '/' + imagePaths[i])
                imgstk[i] = cv.imread(path + '/' + imagePaths[i],0).astype("uint8")
        else: 
            imgstk = np.zeros((10,10,10)) 
            print("this is an error")
        pixelSizeZ = imagesHeightSlice[1]
        return imgstk
        
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
        
        self.resPopUp = DownsampleWindow(self) 
        self.wait_window(self.resPopUp.top)  
        #print(self.resPopUp.value)
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
            self.imageStack[i] = cv.resize(cv.imread(path + '/' + self.imagePaths[i],0).astype("uint8"),(temp.shape[1]//self.downsampleFactor,temp.shape[0]//self.downsampleFactor))
        # get the bottom image (default in the scan)
        self.imgTop = self.imageStack[0,:,:].astype('uint8')   
        self.imgTopSize = self.imgTop.shape
        self.gridSize = ( ((self.imgTop.shape[0]//10)*9)//2, ((self.imgTop.shape[1]//10)*3)//2)
        
        self.ScaleGridBarH = Scale(self, from_=0, to=(self.imgTop.shape[0]//2), orient=HORIZONTAL, label="Scale Tray Horizontal", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.adjustGridSizeHor) 
        self.ScaleGridBarH.grid(row=4,column=1,sticky = NW) 
        self.ScaleGridBarH.set(self.gridSize[0])
        
        self.ScaleGridBarV = Scale(self, from_=0, to=(self.imgTop.shape[0]//2), orient=HORIZONTAL, label="Scale Tray Vertical", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.adjustGridSizeVert) 
        self.ScaleGridBarV.grid(row=4,column=1,sticky = NE) 
        self.ScaleGridBarV.set(self.gridSize[1])
        
        self.GridMidX = Scale(self, from_=0,to=(self.imgTop.shape[0]), orient=HORIZONTAL, label="Grid center X", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.AdjustGridCentreX)
        self.GridMidX.grid(row=5,column=1,sticky = NW)
        self.GridMidX.set(self.imgTop.shape[0]//2)
        
        self.GridMidY = Scale(self, from_=0,to=(self.imgTop.shape[1]), orient=HORIZONTAL, label="Grid center Y", length=self.winfo_screenwidth()/6, sliderlength=self.winfo_screenheight()//100, command=self.AdjustGridCentreY)
        self.GridMidY.grid(row=5,column=1,sticky = NE)
        self.GridMidY.set(self.imgTop.shape[1]//2)
        
        self.gridCenter = (self.imgTop.shape[0]//2,self.imgTop.shape[1]//2)
        
        if self.imgTop.shape[0] > self.imgTop.shape[1] :
            if self.imgTop.shape[0]  > self.maxSize: 
                size = self.imgTop.shape[1]/(self.imgTop.shape[0]/self.maxSize)   
                self.imgTopSize = (int(size),self.maxSize)
        else: 
            if self.imgTop.shape[1]  > self.maxSize: 
                size = self.imgTop.shape[0]/(self.imgTop.shape[1]/self.maxSize)
                self.imgTopSize = (self.maxSize,int(size)) 
        self.imgTop = cv.resize(self.imgTop,self.imgTopSize)
        
        self.imgTop = cv.cvtColor(self.imgTop,cv.COLOR_GRAY2RGB)  
        self.imgTop = Image.fromarray(self.imgTop) 
        self.imgTop = ImageTk.PhotoImage(image=self.imgTop)  
        self.panalTop = Label(self,image=self.imgTop)
        self.panalTop.grid(row=0,column=0)
        
        self.imgSide = self.imageStack[:,0,:].astype('uint8')  
        #if self.downsampleFactor > 1: 
            #self.imgSide = np.delete(self.imgSide,list(range(0,self.imgSide.shape[0],self.downsampleFactor)),axis=0)   
        self.imgSideSize = self.imgSide.shape

        if self.imgSideSize[0] > self.imgSideSize[1]: 
            self.imgSide = self.image_resize(self.imgSide,height=self.maxSize)
        else: 
            self.imgSide = self.image_resize(self.imgSide,width=self.maxSize) 
        self.imgSideSize = self.imgSide.shape
        
        self.imgSide = cv.cvtColor(self.imgSide,cv.COLOR_GRAY2RGB) 
        self.imgSide = Image.fromarray(self.imgSide) 
        self.imgSide = ImageTk.PhotoImage(image=self.imgSide)  
        self.panalSide = Label(self,image=self.imgSide)
        self.panalSide.grid(row=0,column=1)     
        
        self.imgFront = self.imageStack[:,:,0].astype('uint8') 
        #if self.downsampleFactor > 1: 
           # self.imgFront = np.delete(self.imgFront,list(range(0,self.imgFront.shape[0],self.downsampleFactor)),axis=0) 

        self.imgFrontSize = self.imgFront.shape  
        if self.imgFrontSize[0] > self.imgFrontSize[1]: 
            self.imgFront = self.image_resize(self.imgFront,height=self.maxSize)
        else: 
            self.imgFront = self.image_resize(self.imgFront,width=self.maxSize) 
        self.imgFrontSize = self.imgFront.shape
        
        
        self.imgFront = cv.cvtColor(self.imgFront,cv.COLOR_GRAY2RGB) 
        self.imgFront = Image.fromarray(self.imgFront) 
        self.imgFront = ImageTk.PhotoImage(image=self.imgFront)  
        self.panalFront = Label(self,image=self.imgFront)
        self.panalFront.grid(row=0,column=2)
            
        # bars for showing scale
        self.frontBar = Scale(self, from_=1, to=self.imageStack.shape[2], orient=HORIZONTAL, length=self.winfo_screenwidth()/3, sliderlength=self.winfo_screenheight()//100, command=self.frontSlider)
        self.frontBar.grid(row=1,column=2)
        self.frontBar.set(self.imageStack.shape[2]//2)
        self.sideBar = Scale(self, from_=1, to=self.imageStack.shape[1], orient=HORIZONTAL, length=self.winfo_screenwidth()/3, sliderlength=self.winfo_screenheight()//100, command=self.sideSlider)
        self.sideBar.grid(row=1,column=1) 
        self.sideBar.set(self.imageStack.shape[1]//2)
        self.topBar = Scale(self, from_=1, to=self.imageStack.shape[0], orient=HORIZONTAL, length=self.winfo_screenwidth()/3, sliderlength=self.winfo_screenheight()//100, command=self.topSlider)
        self.topBar.grid(row=1,column=0) 
        self.topBar.set(self.imageStack.shape[0]//2)
root = ScanOBJGenerator() 
root.mainloop()