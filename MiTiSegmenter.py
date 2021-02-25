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


# our file
from PopUpClasses import *
from Frames import *
####### version info #######
# python 3.6 # tkinter # PIL # numpy = 1.16.2 # cv2 = 4.1.1 # os # open3d = 0.8.0.0 # random   
####### Build exe ####### 
# need add path to dask.yaml and distribution.yaml in you python Lib/site-packages/(dask or distribution)

class MiTiSegmenter(tk.Tk): 
    # initialisation 
    def __init__(self, *args, **kwargs): 
        tk.Tk.__init__(self, *args, **kwargs) 
        tk.report_callback_exception = self.showError
        self.thresholdMax = 255  
        self.thresholdMin = 0
        self.blobMinSizeVal = 15
        self.downsampleFactor = 1
        self.cellBase = 1
        self.usedThres =(0,0)
        self.gridSize = (0,0)
        self.gridCenter = (0,0)
        self.gridRotation = 0
        self.viewThresholdVar = 1#IntVar() 
        self.viewCellVar = 1 #IntVar()
        self.layers = []
        self.traySize = 50
        self.trayCSV = [] 
        self.imagePaths =[]
        self.workingPath = "" 
        self.RawPath = ""
        self.blobCenterOfMass = []
        self.TL = 0 
        self.TR = 0
        self.BL = 0
        self.BR = 0
        self.blobbed = False
        self.slides = [0,0,0]
        self.imageStack = None 
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 
        self.frames = {}   
        for F in (StartPage, StackOptions, SeperateTrays, SeperateTrays, ThresAndCellStack, LabelImages, TrayStack,  TrayAlign, Export):
            frame = F(container, self) 
            self.frames[F] = frame  
            frame.grid(row = 0, column = 0, sticky ="nsew") 
        self.show_frame(StartPage) 
    
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 
    
    def LoadImagesSelected(self, cont, Raw = False):
        completed = True
        if Raw == True:
            completed = self.loadRawStack()
        else:
            completed = self.loadImages()
        if completed == True:
            frame = self.frames[cont] 
            frame.tkraise()
        
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
        self.wait_window(self.resTrayPopUp.top)  
        self.resTrayPopUp = self.resTrayPopUp.value
        self.resTrayPopUp = self.resTrayPopUp.split("*")
        for i in range(len(self.resTrayPopUp)):
            print("tray="+self.resTrayPopUp[i]+";")
            if self.resTrayPopUp[i] == ' ': 
                self.trayCSV.append(None)
            elif self.resTrayPopUp[i] == '':
                print("blankspace")
            else: 
                tray = np.loadtxt(self.resTrayPopUp[i], delimiter=',',dtype='U')
                print(tray)
                self.trayCSV.append(tray)
        print(self.trayCSV)
        for i in range(len(self.layers)):
            # setup base layers
            self.putGridOnImage(np.zeros((self.imageStack.shape[1],self.imageStack.shape[2])), self.layers[i])
        self.refreshImages()
    
    def deleteTray(self,listboxValues): 
        if listboxValues.size() > 0:
            self.layers.pop(listboxValues.curselection()[0])
            listboxValues.delete(listboxValues.curselection()[0])
            self.refreshImages
         
    def addTray(self, listbox):
        listbox.insert(END,"tray part: " + "_" +str(self.slides[2]))
        
    def exportTrays(self, listbox): 
        items = listbox.get(0, END)
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
        
        
    def applyTray(self,listboxValues):  
        onTray = False
        self.layers = [] 
        listboxValues.delete(0,listboxValues.size())
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
                print(i)
                print(self.imageStack.shape[0]-1)
                if onTray == True or i == self.imageStack.shape[0]-1: 
                    onTray = False 
                    self.layers.append(trayStart + (trayCount//2))
                    trayStart = 0
                    trayCount = 0
            tempim = cv.putText(temp,("Checking for objects image " + str(i+1) + ' / ' + str(self.imageStack.shape[0])) + ' ' +str(onTray),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(255,255,55),2) 
            cv.imshow("Applying stack please wait, we use these images to check for breaks between the removed trays, e.g. all black = no tray .",tempim) 
            cv.waitKey(1)
        cv.destroyAllWindows()
        self.gridSize = []
        temp = self.imageStack[0,:,:].astype('uint8')
        for i in range(len(self.layers)): 
            self.gridSize.append(( ((temp.shape[0]//10)*9)//2, ((temp.shape[1]//10)*3)//2))
        for i in range(len(self.layers)):
            listboxValues.insert(END,"tray : "+ str(i+1) + "_" +str(self.layers[i]))
        self.refreshImages()
        
    '''def cellShade(self):
        self.imageStack = self.imageStack-(self.imageStack%self.cellBase)
        self.usedThres = (self.usedThres[0],1)
        self.refreshImages()'''
    
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
        self.thresholdMax = int(val)
        self.refreshImages() 
        
    def adjustThresholdMin(self,val):
        self.thresholdMin = int(val)
        self.refreshImages()
        
    def adjustGridRotation(self,val):
        self.gridRotation = int(val) 
        self.refreshImages()
        
    def adjustGridSizeHor(self, val): 
        for i in range(len(self.layers)):     
            if self.layers[i] < self.topBar.get() + self.traySize and self.layers[i] > self.topBar.get() - self.traySize: 
                self.gridSize[i] = (int(val),self.gridSize[i][1])
        self.refreshImages()
    
    def adjustGridSizeVert(self, val): 
        for i in range(len(self.layers)):     
            if self.layers[i] < self.topBar.get() + self.traySize and self.layers[i] > self.topBar.get() - self.traySize:
                self.gridSize[i] = (self.gridSize[i][0],int(val)) 
        self.refreshImages()
    
    '''def applyThreshold(self): 
        if self.imageStack is None: 
            return
        self.imageStack[self.imageStack <= self.thresholdMin] = 0    
        self.imageStack[self.imageStack >= self.thresholdMax] = 0 
        self.viewThresholdVar.set(0) 
        self.usedThres = (1,self.usedThres[1])
        self.refreshImages()'''
        
    def refreshImages(self):  
        if self.imageStack is None: 
            return
        self.updateFront(self.slides[0])
        self.updateSide(self.slides[1])
        self.updateTop(self.slides[2])
    
    '''def blobDetection(self): 
        if self.imageStack is None:
            return  
        self.imageStack[self.imageStack != 0] = 255 
        self.imageStack = measure.label(self.imageStack)
        #self.imageStack = morphology.remove_small_objects(self.imageStack, min_size=(self.blobMinSizeVal*self.blobMinSizeVal*self.blobMinSizeVal))
        self.blobbed = True
        self.refreshImages()'''
    
    '''def organiseBlobs(self, unique): 
        numOn = 0 
        for i in range(unique.shape[0]):
            self.imageStack[self.imageStack == unique[i]] == numOn 
            numOn = numOn + 1'''
    
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

    def ExportUnProcessedStack(self, processed = False):
        print("check this function is now correct")
        savepath = os.path.join(self.workingPath,"ExportImages")
        #img_size = (self.imageStack.shape[1]*self.downsampleFactor)*(self.imageStack.shape[2]*self.downsampleFactor)
        image = open(self.RawPath)
        maxV = np.iinfo(self.bitType).max
        for i in range(self.imageStack.shape[0]): 
            img = np.fromfile(image, dtype = self.bitType, count = self.img_size)
            img.shape = (self.img_sizeXY)
            #img = img * (np.iinfo(self.bitType).max/img.max())
            img = (((img-0.0)/(maxV-0.0))*255).astype("uint8")
            #infoFile.write(os.path.join(savepath,str(i).zfill(6)+".tiff") + " " + str(self.pixelSizeZ*i) +"\n") 
            cv.imwrite(savepath+'/'+str(i).zfill(6)+".tiff", img)
            self.imagePaths.append(savepath+'/'+str(i).zfill(6)+".tiff")
        image.close()
        if processed == True:
            showinfo("Stack Saved!","Unprocessed stack saved to:\n"+savepath)
    
    def DeleteTempStack(self):
        for i in range(len(self.imagePaths)):
            os.remove(self.imageOaths[i])
        self.imagePaths = []
        
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
                 #print("check this +1 doenst break anything")
                 infoFile.write('"' + dirName + self.imagePaths[o] +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[bounds[i][0]]) +"\n") 
                 print("create a flag for raw image loads that cycles through the file again")
                 img = None
                 #print(self.RawPath)
                 if self.RawPath:
                     print(self.imagePaths[o])
                     img = cv.imread(self.imagePaths[o],0).astype("uint8")
                     #print(img)
                     #print(img.shape)
                     img  = img[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
                     #print(bounds[p][2],bounds[p][3], bounds[p][4],bounds[p][5])
                     #print(img)
                 else:
                     print(self.workingPath + '/' + self.imagePaths[o])
                     img = cv.imread(self.workingPath + '/' + self.imagePaths[o],0).astype("uint8")[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
                 #print(img)
                 #print(imType)
                 if imType == 1: #processed 
                     img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.processSingleTray(img) 
                 elif imType == 2: # segmentation 
                     img  = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#img * (self.processSingleTray(img)//255)
                     img[img >= 1] = 255
                 print(img)
                 
                 if(self.RawPath):
                     print("in raw the images have different path")
                     cv.imwrite(self.workingPath + '/' + 'blobstacks'+'/'+ str(blobName) + '/' + dirName +'/' + dirName + os.path.basename(self.imagePaths[o]), img)
                 else:
                     print(self.workingPath + '/' + 'blobstacks'+'/'+ str(blobName) + '/' + dirName +'/' + dirName + self.imagePaths[o])
                     cv.imwrite(self.workingPath + '/' + 'blobstacks'+'/'+ str(blobName) + '/' + dirName +'/' + dirName + self.imagePaths[o], img)
            infoFile.close()
    
    def exportTiffStacks(self):
         if self.imageStack is None: 
             return
         self.resPopUp = GenerateTiffStackWindow(self.master) 
         self.wait_window(self.resPopUp.top)  
         self.resPopUp.value = self.resPopUp.value.split(';')
         generateRaw = int(self.resPopUp.value[0])
         generatePro = int(self.resPopUp.value[1])
         generateMod = int(self.resPopUp.value[2])
         generateSeg = int(self.resPopUp.value[3]) 
         if self.RawPath:
             self.ExportUnProcessedStack()
         if os.path.isdir(self.workingPath + '/'+"blobstacks") == False:
             os.mkdir(self.workingPath + '/'+"blobstacks")
         shape = self.imageStack.shape
         self.imageStack = None 
         stack = None
         bounds = [] 
         blobCenters = [] 
         gridCenters = [] 
         gridNames = []
         TrayToBlob = []
         for i in range(shape[0]): 
             print("\r loading img : "+str(i) + " of " + str(shape[0]),end=" ")
             if self.RawPath:
                 img = cv.imread(self.imagePaths[i],0)
             else:
                 img = cv.imread(self.workingPath+'/'+self.imagePaths[i],0)
             #if self.downsampleFactor > 1:
                #img = cv.resize(img,(shape[2]//self.downsampleFactor,shape[1]//self.downsampleFactor))
             tempim = cv.cvtColor(img,cv.COLOR_GRAY2RGB)
             tempim = cv.putText(tempim,("processing image " + str(i+1) + ' / ' + str(shape[0]) + " this may take a while"),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
             cv.imshow("loading",tempim) 
             cv.waitKey(1)
             start = 0
             img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
             if img.max() > 0: 
                 if stack is None: 
                     start = i
                     stack = img
                 else:
                     if len(stack.shape) < 3:
                         stack = np.stack((img,stack))
                     else: 
                         stack = np.concatenate((stack, img.reshape((1,img.shape[0],img.shape[1]))))
                         
                         if i == shape[0]-1:
                             print("set the stack to 1 ")
                             stack[stack != 0] = 1 
                             print("remove small objects ")
                             stack = morphology.remove_small_objects(stack.astype(bool), min_size=(self.blobMinSizeVal)).astype("uint8")
                             print(" get the labels ")
                             stack = measure.label(stack)
                             print("get unique value ")
                             unique = np.unique(stack)
                             for o in range(unique.shape[0]):  
                                 print("\r Getting blobs  : "+str(o) + " of " + str(unique.shape[0]),end=" ")
                                 if unique[o] == 0: # background
                                     continue
                                 currentBlob = np.where(stack == unique[o])
                                 
                                 Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) # was i then start now its i again
                                 Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))#*self.downsampleFactor
                                 X = currentBlob[2].reshape((currentBlob[2].shape[0],1))#*self.downsampleFactor
                                 # padd the bound by the down sample rate
                                 if (np.amax(Z) - np.amin(Z) > self.blobMinSizeVal and np.amax(Y) - np.amin(Y) > self.blobMinSizeVal and np.amax(X) - np.amin(X) > self.blobMinSizeVal):
                                     bounds.append((np.amin(Z)+start,np.amax(Z)+start,np.amin(Y),np.amax(Y),np.amin(X),np.amax(X)))  
                                     #print(bounds)
                                     print("i think start - npmin")
                                     print("i = " + str(start) + " z start = " +str(np.amin(currentBlob[0])+start) + " z end = " + str(np.amax(currentBlob[0])+start))
                                     blobCenters.append( ( (np.amin(Z)+np.amax(Z)+(start*2))//2, (np.amin(Y)+np.amax(Y))//2, (np.amin(X)+np.amax(X))//2 ))
                             stack = None
                             start = 0
             else:
                 if stack is None:
                     continue
                 else: 
                     print("set the stack to 1 ")
                     stack[stack != 0] = 1 
                     print("remove small objects ")
                     stack = morphology.remove_small_objects(stack.astype(bool), min_size=(self.blobMinSizeVal)).astype("uint8")
                     print(" get the labels ")
                     stack = measure.label(stack)
                     print("get unique value ")
                     unique = np.unique(stack)
                     for o in range(unique.shape[0]):  
                         print("\r Getting blobs  : "+str(o) + " of " + str(unique.shape[0]),end=" ")
                         if unique[o] == 0: # background
                             continue
                         currentBlob = np.where(stack == unique[o])
                         
                         Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) # was i then start now its i again
                         Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))#*self.downsampleFactor
                         X = currentBlob[2].reshape((currentBlob[2].shape[0],1))#*self.downsampleFactor
                         # padd the bound by the down sample rate
                         if (np.amax(Z) - np.amin(Z) > self.blobMinSizeVal and np.amax(Y) - np.amin(Y) > self.blobMinSizeVal and np.amax(X) - np.amin(X) > self.blobMinSizeVal):
                             bounds.append((np.amin(Z)+start,np.amax(Z)+start,np.amin(Y),np.amax(Y),np.amin(X),np.amax(X)))  
                             #print(bounds)
                             print("i think start - npmin")
                             print("i = " + str(start) + " z start = " +str(np.amin(currentBlob[0])+start) + " z end = " + str(np.amax(currentBlob[0])+start))
                             blobCenters.append( ( (np.amin(Z)+np.amax(Z)+(start*2))//2, (np.amin(Y)+np.amax(Y))//2, (np.amin(X)+np.amax(X))//2 ))
                     stack = None
                     start = 0
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
         if self.RawPath:
                  self.DeleteTempStack()
         
    def ViewImagePreviews(self,img, viewThres, viewCell, downSample, downFactor, thresMax, thresMin, cell, final = False):
        if viewCell == 1: 
           img = img-(img%cell)
        if viewThres == 1: 
            img[img >= thresMax] = 0   
            img[img <= thresMin] = 0
        if final == True:
            img[img > 0] == 255
        return img.astype("uint8")
    
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
        angle = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return int(qx),int(qy)
    
    def putGridOnImage(self,temp, val): 
        for i in range(len(self.layers)): 
            if self.layers[i] < int(val) + self.traySize and self.layers[i] > int(val) - self.traySize:
                print("need redo scale bars")
                #self.ScaleGridBarV.set(self.gridSize[i][1]) 
                #self.ScaleGridBarH.set(self.gridSize[i][0])
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
        temp = self.imageStack[int(val)-1,:,:]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB)
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        temp = self.putGridOnImage(temp,val)
        if self.blobbed == True:
            temp[temp >= 1] = 255
        cv.imshow("top", temp)

    def generateInfoFile(self):  
        self.resPopUp = InfoWindow(self.master) 
        self.wait_window(self.resPopUp.top)  
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
            return False
        self.blobbed = False
        self.imageStack = None
        self.workingPath = os.path.dirname(path)
        print(self.workingPath)
        self.RawPath = path
        self.resPopUp = DownsampleWindow(self.master) 
        self.wait_window(self.resPopUp.top)
        dsample = self.resPopUp.value 
        if len(dsample) < 1: 
            dsample = 1
            return False
        self.downsampleFactor = int(dsample)
        self.resPopUp = RawInfoWindow(self.master) 
        self.wait_window(self.resPopUp.top)  
        resolution = self.resPopUp.value.split(";") 
        if len(resolution) < 4: 
            return False
        resolution[0] = int(resolution[0])
        resolution[1] = int(resolution[1])
        resolution[2] = int(resolution[2])
        resolution[3] = int(resolution[3])
        height = resolution[2]
        #print(resolution)
        self.bitType = np.uint8
        if(resolution[3] == 16):
            self.bitType = np.uint16
        elif(resolution[3] == 32):
            self.bitType = np.uint32
        elif(resolution[3] == 64):
            self.bitType = np.uint64
        image = open(path)
        self.imageStack = np.zeros((resolution[2],resolution[1]//self.downsampleFactor,resolution[0]//self.downsampleFactor), dtype = "uint8")
        self.img_size = resolution[0] * resolution[1]
        self.img_sizeXY = (resolution[1],resolution[0])
        img_res = (resolution[0]//self.downsampleFactor,resolution[1]//self.downsampleFactor)
        maxV = np.iinfo(self.bitType).max
        for i in range(resolution[2]):
            img = np.fromfile(image, dtype = self.bitType, count = self.img_size)
            img.shape = (resolution[1],resolution[0])
            #img = img * (np.iinfo(self.bitType).max/img.max())
            
            img = (((img-0.0)/(maxV-0.0))*255).astype("uint8")
            if self.downsampleFactor > 1:
                img = cv.resize(img,img_res)
            self.imageStack[i] = img
            tempim = cv.cvtColor(self.imageStack[i],cv.COLOR_GRAY2RGB)
            tempim = cv.putText(tempim,("loading image " + str(i+1) + ' / ' + str(resolution[2])),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
            cv.imshow("loading",tempim) 
            cv.waitKey(1)
        image.close()
        cv.destroyAllWindows()
        self.imagePaths = []
        self.imagesHeightSlice = []
        self.resPopUp = InfoWindow(self.master) 
        self.wait_window(self.resPopUp.top)  
        resolution = self.resPopUp.value.split(";") 
        if len(resolution) < 3: 
            return False
        self.pixelSizeX = float(resolution[0])
        self.pixelSizeY = float(resolution[1])
        self.pixelSizeZ = float(resolution[2])
        self.offsetX = 0 
        self.offsetY = 0 
        for i in range(height):
            self.imagesHeightSlice.append(i*self.pixelSizeZ)
        self.setInitGraphs()
        return True
        
    def loadImages(self):
        path = filedialog.askdirectory() 
        if path == "": 
            return
        print("loading images")
        self.blobbed = False
        self.imageStack = None 
        paths = os.listdir(path) 
        self.workingPath = path
        infoFile = ""
        
        if len(paths) < 1: 
            showinfo("File Directory empty",path+ " : contains no files!")
            return False
                
        for i in range(len(paths)):
            if paths[i].endswith(".info"): 
                infoFile = paths[i] 
                break 
        
        if infoFile == "":
            showinfo("No Scanner info file", path + " : contains no .info file from the scanner!\nLets create one now, then reload the stack")
            self.generateInfoFile()
            return False
        
        self.resPopUp = DownsampleWindow(self.master) 
        self.wait_window(self.resPopUp.top)
        resolution = self.resPopUp.value 
        if len(resolution) < 1: 
            resolution = "1"
            return False
        
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
                return False
            self.imageStack[i] = cv.resize(cv.imread(path + '/' + self.imagePaths[i],0).astype("uint8"),(temp.shape[1]//self.downsampleFactor,temp.shape[0]//self.downsampleFactor))
            tempim = cv.cvtColor(self.imageStack[i],cv.COLOR_GRAY2RGB)
            tempim = cv.putText(tempim,("loading image " + str(i+1) + ' / ' + str(len(self.imagePaths))),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
            cv.imshow("loading",tempim) 
            cv.waitKey(1)
        cv.destroyAllWindows()
        self.setInitGraphs()
        return True
            
    def setInitGraphs(self):
        self.imgTop = self.imageStack[0,:,:]
        self.gridSize = ( ((self.imgTop.shape[0]//10)*9)//2, ((self.imgTop.shape[1]//10)*3)//2)
        
        self.gridCenter = (self.imgTop.shape[0]//2,self.imgTop.shape[1]//2)
        self.imgTop = cv.cvtColor(self.imgTop,cv.COLOR_GRAY2RGB)
        self.imgSide = self.imageStack[:,0,:]
        self.imgFront = self.imageStack[:,:,0] 

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
        # set bars for the tray align
        self.frames[TrayAlign].MoveGridY.to = self.imgTop.shape[1]
        self.frames[TrayAlign].MoveGridX.to = self.imgTop.shape[2]
        self.frames[TrayAlign].MoveGridY.set(self.imgTop.shape[1]//2)
        self.frames[TrayAlign].MoveGridX.set(self.imgTop.shape[2]//2)
        
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
        
    def updateCellHelp(self, val):
        ampCellHelp = val
        self.lCellHelp.set_ydata(self.sCellHelp-(self.sCellHelp%ampCellHelp))
        self.figCellHelp.canvas.draw_idle()
        
    def ShowCellHelp(self):
        self.figCellHelp, ax = plt.subplots()
        self.figCellHelp.canvas.set_window_title('Cell-Shade example')
        plt.subplots_adjust(bottom=0.4)
        t = np.arange(1, 255, 1)
        self.sCellHelp = t
        self.lCellHelp, = plt.plot(t, self.sCellHelp, lw=2)
        ax.margins(x=0,y=0)
        axcolor = 'lightgoldenrodyellow'
        axampCellHelp = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
        sampCellHelp = Slider(axampCellHelp, 'Cell-base', 1, 255, valinit=0)
        
        sampCellHelp.on_changed(self.updateCellHelp)
        plt.title('Cell-shading is a technique of grouping similar values. \n If you move the bar you\'ll see the bar becomes a staircase as values are grouped.\n This helps remove the human error with small values')
        plt.show()
        
    def updateThresHelp(self, val):
        ampThresHelp = val
        ampThresHelp[self.sThresHelp <= ampThresHelp] = 0
        self.lThresHelp.set_ydata(temp)
        self.figThresHelp.canvas.draw_idle()
        
    def ShowThresHelp(self):
        self.figThresHelp, ax = plt.subplots()
        self.figThresHelp.canvas.set_window_title('Thres-Shade example')
        plt.subplots_adjust(bottom=0.4)
        t = np.arange(1, 255, 1)
        self.sThresHelp = t
        self.lThresHelp, = plt.plot(t, self.sThresHelp, lw=2)
        ax.margins(x=0,y=0)
        axcolor = 'lightgoldenrodyellow'
        axampThresHelp = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
        sampThresHelp = Slider(axampThresHelp, 'Thres-base', 1, 255, valinit=0)
        
        sampThresHelp.on_changed(self.updateThresHelp)
        plt.title('Thresholes remove all values out side of a range')
        plt.show()

app = MiTiSegmenter() 
app.title("MiTiSegmenter")
app.mainloop()