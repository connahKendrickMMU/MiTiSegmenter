import tkinter as tk
import traceback 
import tkinter.messagebox
import tkinter as tk
from tkinter import filedialog
from tkinter import * 
from tkinter.messagebox import showinfo, askquestion
from skimage import measure, morphology
import math
import numpy as np  
import cv2 as cv
import os
import open3d as o3d 
import shutil
#import meshio

# our file
from PopUpClasses import *
from Frames import *

# z has be top
####### version info #######
# python 3.6 # tkinter # PIL # numpy = 1.16.2 # cv2 = 4.1.1 # os # open3d = 0.8.0.0 # random   
####### Build exe ####### 
# pyinstaller MiTiSegmenter.py --icon=logo.ico --onefile

class MiTiSegmenter(tk.Tk): 
    # initialisation 
    def __init__(self, *args, **kwargs): 
        tk.Tk.__init__(self, *args, **kwargs) 
        tk.report_callback_exception = self.showError
        self.thresholdMax = 255  
        self.thresholdMin = 0
        self.sampleMinSizeVal = 15
        self.downsampleFactor = 1
        self.cellBase = 1
        self.usedThres =(0,0)
        self.gridSize = (0,0)
        self.gridCenter = (0,0)
        self.gridRotation = 0
        self.viewThresholdVar = 1
        self.viewCellVar = 1 
        self.layers = []
        self.plateSize = 50
        self.plateCSV = [] 
        self.imagePaths =[]
        self.workingPath = "" 
        self.RawPath = ""
        self.sampleCenterOfMass = []
        self.TL = 0 
        self.TR = 0
        self.BL = 0
        self.BR = 0
        self.slides = [0,0,0]
        self.imageStack = None 
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 
        self.frames = {}   
        for F in (StartPage, StackOptions, SeparatePlates, ThresAndCellStack, LabelImages, PlateStack,  PlateAlign, Export):
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
    
    def flipPlateHor(self): 
        for i in range(len(self.plateCSV)):  
                self.plateCSV[i] = np.fliplr(self.plateCSV[i])
        self.refreshImages()
                
    def flipPlateVer(self): 
        for i in range(len(self.plateCSV)):  
                self.plateCSV[i] = np.flipud(self.plateCSV[i]) 
        self.refreshImages()
                
    def loadCSV(self): 
        if len(self.layers) == 0:
            print("no layers created")
        self.resPlatePopUp = GetPlateCSVs(self.master,self.layers) 
        self.wait_window(self.resPlatePopUp.top)  
        self.resPlatePopUp = self.resPlatePopUp.value
        self.resPlatePopUp = self.resPlatePopUp.split("*")
        for i in range(len(self.resPlatePopUp)):
            if self.resPlatePopUp[i] == ' ': 
                self.plateCSV.append(None)
            elif self.resPlatePopUp[i] == '':
                print("blankspace")
            else: 
                plate = np.loadtxt(self.resPlatePopUp[i], delimiter=',',dtype='U')
                self.plateCSV.append(plate)
        for i in range(len(self.layers)):
            # setup base layers
            self.putGridOnImage(np.zeros((self.imageStack.shape[1],self.imageStack.shape[2])), self.layers[i])
        self.refreshImages()
         
    def addPlate(self, listbox):
        listbox.insert(END,"plate part: " + "_" +str(self.slides[2]))
        # sort values 
        items = listbox.get(0, listbox.size())
        listbox.delete(0,listbox.size())
        items = list(items)
        ints = []
        for i in range(len(items)):
            if int(items[i].split("_")[1]) not in ints:
                ints.append(int(items[i].split("_")[1]))
        while(len(ints)>0):
            listbox.insert(END,"plate part: " + "_" +str(min(ints)))
            ints.remove(min(ints))
        
    def exportPlates(self, listbox): 
        items = listbox.get(0, END)
        items = list(items)
        if len(items) == 0:
            return
        items.insert(0,"plate part: " + "_" +str(0))
        items.append("plate part: " + "_" +str(self.imageStack.shape[0]))
        numOfOutputs = len(items)
        # create the folders 
        lastOn = 0
        if self.RawPath:
            image = open(self.RawPath)
        for i in range(1, numOfOutputs): 
            if os.path.exists(self.workingPath+'/plate' + str(i)) == False:
                os.mkdir(self.workingPath+'/plate' + str(i))
            numberOfFrames = int(items[i].split('_')[1]) 
            infoFile = open(self.workingPath+'/plate' + str(i) +'/' + "a_info.info","w") 
            infoFile.write("pixelsize " + str(self.pixelSizeX)  + " " + str(self.pixelSizeY) +"\n") 
            infoFile.write("offset " + str(self.offsetX) + " " + str(self.offsetY) + "\n") 
            startLast = lastOn
            if self.RawPath:
                maxV = np.iinfo(self.bitType).max
                for o in range(lastOn, numberOfFrames): 
                    img = np.fromfile(image, dtype = self.bitType, count = self.img_size)
                    img.shape = (self.img_sizeXY)
                    img = (((img-0.0)/(maxV-0.0))*255).astype("uint8")
                    cv.imshow("loading",img) 
                    cv.waitKey(1)
                    cv.imwrite(self.workingPath+'/plate' + str(i)+'/'+str(o).zfill(6)+".tiff", img) 
                    #showinfo("path = " + self.workingPath+'/plate' + str(i)+'/'+str(o).zfill(6)+".tiff")
                    infoFile.write('"' + str(i).zfill(6)+".tiff" +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[startLast]) +"\n")
                    lastOn = o
            else:
                for o in range(lastOn, numberOfFrames): 
                    shutil.copyfile(self.workingPath+'/' + self.imagePaths[o],self.workingPath+'/plate' + str(i)+ '/' +self.imagePaths[o]) 
                    
                    cv.imshow("loading",self.imageStack[o,:,:]) 
                    cv.waitKey(1)
                    infoFile.write('"' + self.imagePaths[o] +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[startLast]) +"\n")
                    lastOn = o
            infoFile.close()
        if self.RawPath:
            image.close()
        #showinfo("Exported", "The plates have been exported")
        res = askquestion("Exported", "The plates have been successfully exported as separate image stacks. Would you like to import one now?")
        if res == "yes":
            #self.__init__()
            cv.destroyAllWindows()
            self.loadImages()
            self.show_frame(StackOptions)
        
    def applyPlate(self,listboxValues):  
        onPlate = False
        self.layers = [] 
        listboxValues.delete(0,listboxValues.size())
        plateStart = 0
        plateCount = 0
        for i in range(0,self.imageStack.shape[0]): 
            temp = self.imageStack[i,:,:].astype('uint8') 
            temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
            if np.where(temp>0)[0].shape[0] > self.sampleMinSizeVal*10:
                if onPlate == False: 
                    onPlate = True
                    plateStart = i 
                else: 
                    plateCount = plateCount+1 
            else: 
                if onPlate == True: 
                    onPlate = False 
                    self.layers.append(plateStart + (plateCount//2))
                    plateStart = 0
                    plateCount = 0
                if(i == self.imageStack.shape[0]):
                    if(onPlate == True):
                        onPlate = False 
                        self.layers.append(plateStart + (plateCount//2))
                        plateStart = 0
                        plateCount = 0
            tempim = cv.putText(temp,("Checking for objects image " + str(i+1) + ' / ' + str(self.imageStack.shape[0])) + ' ' +str(onPlate),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(255,255,55),2) 
            cv.imshow("Applying stack please wait, we use these images to check for breaks between the removed plates, e.g. all black = no plate .",tempim) 
            cv.waitKey(1)
        cv.destroyWindow("Applying stack please wait, we use these images to check for breaks between the removed plates, e.g. all black = no plate .")
        self.gridSize = []
        temp = self.imageStack[0,:,:].astype('uint8')
        for i in range(len(self.layers)): 
            self.gridSize.append(( ((temp.shape[0]//10)*9)//2, ((temp.shape[1]//10)*3)//2))
        for i in range(len(self.layers)):
            listboxValues.insert(END,"plate : "+ str(i+1) + "_" +str(self.layers[i]))
        self.refreshImages()
    
    def AdjustGridCentreY(self, val): 
        self.gridCenter = (self.gridCenter[0],int(val)) 
        self.refreshImages()
        
    def AdjustGridCentreX(self, val): 
        self.gridCenter = (int(val),self.gridCenter[1])
        self.refreshImages()
    
    def minBlobSize(self,val):
        self.sampleMinSizeVal = int(val)
    
    def adjustCellBase(self,val): 
        self.cellBase = int(val) 
        self.frames[ThresAndCellStack].thresholdBarMin.configure(resolution = self.cellBase)
        self.frames[ThresAndCellStack].thresholdBar.configure(resolution = self.cellBase)
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
            # was self.topbar
            if self.layers[i] < self.slides[2] + self.plateSize and self.layers[i] > self.slides[2] - self.plateSize: 
                self.gridSize[i] = (int(val),self.gridSize[i][1])
        self.refreshImages()
    
    def adjustGridSizeVert(self, val): 
        for i in range(len(self.layers)):     
            if self.layers[i] < self.slides[2] + self.plateSize and self.layers[i] > self.slides[2] - self.plateSize:
                self.gridSize[i] = (self.gridSize[i][0],int(val)) 
        self.refreshImages()
        
    def refreshImages(self):  
        if self.imageStack is None: 
            return
        self.updateFront(self.slides[0])
        self.updateSide(self.slides[1])
        self.updateTop(self.slides[2])

    def generate3DModel(self,img,path,folders):
        if img is None: 
            return 
        try:
            print(folders)
            """if folders == "Processed_files" or folders == "Segmentation_masks":
                #img = morphology.remove_small_objects(img.astype(bool), min_size=(self.sampleMinSizeVal)).astype("uint8")
                # biggest blob only
                img[img != 0] == 1
                img = measure.label(img)
                rand_un = np.unique(img,return_counts=True)
                max_val = 0
                for i in range(len(rand_un[0])):
                    if rand_un[0][i] != 0:
                        if rand_un[1][i] > max_val:
                            max_val = rand_un[0][i]
                img[img != max_val] = 0"""
            # Pass xyz to Open3D.o3d.geometry.PointCloud and visualize
            print("make point cloud")
            pcd = o3d.geometry.PointCloud()
            print("point cloud obj")
            pcd.points = o3d.utility.Vector3dVector(np.argwhere(img != 0))
            print("point cloud object")
            #o3d.visualization.draw_geometries([pcd])
            #print("visualise")
            pcd.estimate_normals()
            print("get normals")
            distances = 1# pcd.compute_nearest_neighbor_distance() worked out to 1.000013808319598
            print("get distance")
            avg_dist = distances#np.mean(distances)
            print(avg_dist)
            radius = 3 * avg_dist
            print("make mesh")
            bpa_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd,o3d.utility.DoubleVector([radius, radius * 2]))
            print("save mesh")
            """poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=5, width=0, scale=1, linear_fit=True)[0]
            bbox = pcd.get_axis_aligned_bounding_box()
            p_mesh_crop = poisson_mesh.crop(bbox)"""# slow
            o3d.io.write_triangle_mesh(path+'/'+os.path.basename(os.path.dirname(path))+".ply", poisson_mesh)
            #o3d.io.write_point_cloud("../../test_data/sync.ply", pcd)
            """verts, faces, normals, values = measure.marching_cubes_lewiner((img != 0), 0)#fit this into the model from open3d
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
             
            #pcd_load = o3d.io.read_triangle_mesh(os.path.expanduser('~')+'/meshFull.obj')    
            mesh = meshio.read(os.path.expanduser('~')+'/meshFull.obj')
            print(os.path.basename(os.path.dirname(path)))
            #o3d.io.write_triangle_mesh(path+'/'+os.path.basename(os.path.dirname(path))+".ply", pcd_load)  
            mesh.write(path+'/'+os.path.basename(os.path.dirname(path))+".ply")
            os.remove(os.path.expanduser('~')+'/meshFull.obj')"""
        except Exception as e: 
            print("file not working properly")
            print(e)

    def ExportUnProcessedStack(self, processed = False):
        savepath = os.path.join(self.workingPath,"ExportImages")
        if os.path.isdir(savepath) == False:
            os.mkdir(savepath)
        if self.RawPath:
            image = open(self.RawPath)
        else:
            showinfo("What!","You are already using an image stack!")
        maxV = np.iinfo(self.bitType).max
        for i in range(self.imageStack.shape[0]): 
            img = np.fromfile(image, dtype = self.bitType, count = self.img_size)
            img.shape = (self.img_sizeXY)
            img = (((img-0.0)/(maxV-0.0))*255).astype("uint8")
            cv.imwrite(savepath+'/'+str(i).zfill(6)+".tiff", img) 
            #showinfo("box","path = " + savepath+'/'+str(i).zfill(6)+".tiff")
            self.imagePaths.append(savepath+'/'+str(i).zfill(6)+".tiff")
        image.close()
        if processed == True:
            cv.destroyAllWindows()
            showinfo("Stack Saved!","Unprocessed stack saved to:\n"+savepath)
    
    def DeleteTempStack(self):
        for i in range(len(self.imagePaths)):
            os.remove(self.imageOaths[i])
        self.imagePaths = []
        
    '''def makeAllPointCloud(self):  
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
         #pcd_load = o3d.io.read_triangle_mesh(os.path.expanduser('~')+'/meshFull.obj') 
         #o3d.io.write_triangle_mesh(os.path.expanduser('~')+'/sync.ply', pcd_load)  
         mesh = meshio.read(os.path.expanduser('~')+'/meshFull.obj')
         mesh.write(path+'/'+os.path.basename(os.path.dirname(path))+".ply")
         os.remove(os.path.expanduser('~')+'/meshFull.obj')'''
         
    def WriteStacks(self, i, sampleName, bounds, imType):
        dirName = "Raw_files" 
        if imType == 1: #processed 
            dirName = "Processed_files"
        elif imType == 2: # segmentation  
            dirName = "Segmentation_masks"
        if os.path.isdir(self.workingPath + '/'+"MiTiSegmenter" + '/' + str(sampleName) + '/' + dirName) == False:
            os.mkdir(self.workingPath + '/'+"MiTiSegmenter"+ '/' + str(sampleName) +'/'+dirName)
        infoFile = open(self.workingPath + '/' + 'MiTiSegmenter'+'/' + str(sampleName) +'/'+ dirName +'/' + "a_info.info","w") 
        infoFile.write("pixelsize " + str(self.pixelSizeX)  + " " + str(self.pixelSizeY) +"\n") 
        infoFile.write("offset " + str(self.offsetX) + " " + str(self.offsetY) + "\n")   
        p = i
        for o in range(bounds[i][0],bounds[i][1]+1):
             infoFile.write('"' + dirName + self.imagePaths[o] +'" ' + str(self.imagesHeightSlice[o]-self.imagesHeightSlice[bounds[i][0]]) +"\n") 
             img = None
             if self.RawPath:
                 img = cv.imread(self.imagePaths[o],0).astype("uint8")
                 img  = img[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
             else:
                 img = cv.imread(self.workingPath + '/' + self.imagePaths[o],0).astype("uint8")[bounds[p][2]:bounds[p][3], bounds[p][4]:bounds[p][5]]
             if imType == 1: #processed 
                 img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
             elif imType == 2: # segmentation 
                 img  = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
                 img[img >= 1] = 255
             if(self.RawPath):
                 cv.imwrite(self.workingPath + '/' + 'MiTiSegmenter'+'/'+ str(sampleName) + '/' + dirName +'/' + dirName + os.path.basename(self.imagePaths[o]), img)
             else:
                 cv.imwrite(self.workingPath + '/' + 'MiTiSegmenter'+'/'+ str(sampleName) + '/' + dirName +'/' + dirName + self.imagePaths[o], img)
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
         if os.path.isdir(self.workingPath + '/'+"MiTiSegmenter") == False:
             os.mkdir(self.workingPath + '/'+"MiTiSegmenter")
         shape = self.imageStack.shape
         self.imageStack = None 
         stack = None 
         bounds = [] 
         sampleCenters = [] 
         gridCenters = [] 
         gridNames = []
         PlateToBlob = []
         start = 0
         for i in range(shape[0]):
             if self.RawPath:
                 img = cv.imread(self.imagePaths[i],0)
             else:
                 img = cv.imread(self.workingPath+'/'+self.imagePaths[i],0)
             tempim = cv.cvtColor(img,cv.COLOR_GRAY2RGB)
             tempim = cv.putText(tempim,("processing image " + str(i+1) + ' / ' + str(shape[0]) + " this may take a while"),(0,30),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
             cv.imshow("loading",tempim) 
             cv.waitKey(1)
             
             img = self.ViewImagePreviews(img,1,1,False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
             if img.max() > 0: 
                 if stack is None: 
                     start = i
                     print("start is " +str(start))
                     stack = img
                 else:
                     if len(stack.shape) < 3:
                         stack = np.stack((img,stack))
                     else: 
                         stack = np.concatenate((stack, img.reshape((1,img.shape[0],img.shape[1]))))
                         if i == shape[0]-1:
                              stack[stack != 0] = 1 
                              stack = morphology.remove_small_objects(stack.astype(bool), min_size=(self.sampleMinSizeVal)).astype("uint8")
                              stack = measure.label(stack)
                              unique = np.unique(stack)
                              for o in range(unique.shape[0]):  
                                  if unique[o] == 0: # background
                                      continue
                                  currentBlob = np.where(stack == unique[o])
                                  Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) # was i then start now its i again
                                  Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))#*self.downsampleFactor
                                  X = currentBlob[2].reshape((currentBlob[2].shape[0],1))#*self.downsampleFactor
                                  # padd the bound by the down sample rate
                                  if (np.amax(Z) - np.amin(Z) > self.sampleMinSizeVal and np.amax(Y) - np.amin(Y) > self.sampleMinSizeVal and np.amax(X) - np.amin(X) > self.sampleMinSizeVal):
                                      print("added padd")
                                      bounds.append((np.amin(Z)-self.downsampleFactor+start,np.amax(Z)+self.downsampleFactor+start,np.amin(Y)-self.downsampleFactor,np.amax(Y)+self.downsampleFactor,np.amin(X)-self.downsampleFactor,np.amax(X)+self.downsampleFactor))  
                                      sampleCenters.append( ( (np.amin(Z)+np.amax(Z)+(start))//2, (np.amin(Y)+np.amax(Y))//2, (np.amin(X)+np.amax(X))//2 ))
                              stack = None
                              start = 0
             else:
                 if stack is None:
                     continue
                 else: 
                     print("first end " +str(i))
                     stack[stack != 0] = 1 
                     stack = morphology.remove_small_objects(stack.astype(bool), min_size=(self.sampleMinSizeVal)).astype("uint8")
                     stack = measure.label(stack)
                     unique = np.unique(stack)
                     for o in range(unique.shape[0]):  
                         if unique[o] == 0: # background
                             continue
                         currentBlob = np.where(stack == unique[o])
                         
                         Z = currentBlob[0].reshape((currentBlob[0].shape[0],1)) # was i then start now its i again
                         Y = currentBlob[1].reshape((currentBlob[1].shape[0],1))#*self.downsampleFactor
                         X = currentBlob[2].reshape((currentBlob[2].shape[0],1))#*self.downsampleFactor
                         # padd the bound by the down sample rate
                         #print("save sample "+ str(start))
                         if (np.amax(Z) - np.amin(Z) > self.sampleMinSizeVal and np.amax(Y) - np.amin(Y) > self.sampleMinSizeVal and np.amax(X) - np.amin(X) > self.sampleMinSizeVal):
                             bounds.append((np.amin(Z)+start,np.amax(Z)+start,np.amin(Y),np.amax(Y),np.amin(X),np.amax(X)))  
                             sampleCenters.append( ( (np.amin(Z)+np.amax(Z)+(start))//2, (np.amin(Y)+np.amax(Y))//2, (np.amin(X)+np.amax(X))//2 ))
                     stack = None
         if len(self.layers) > 0:
             self.flipPlateVer()
             for i in range(len(self.layers)): 
                    topInterp = np.linspace((self.TL[0],self.TL[1]),(self.TR[0],self.TR[1]),num=self.plateCSV[i].shape[0]+1,endpoint=True,dtype=('int32'))
                    bottomInterp = np.linspace((self.BL[0],self.BL[1]),(self.BR[0],self.BR[1]),num=self.plateCSV[i].shape[0]+1,endpoint=True,dtype=('int32'))
                    for o in range(self.plateCSV[i].shape[0]):
                        #interpolate between the top and bottom downward looping to fill the gaps 
                        cols1 = np.linspace(topInterp[o],bottomInterp[o],num=self.plateCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                        cols2 = np.linspace(topInterp[o+1],bottomInterp[o+1],num=self.plateCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))#0+2
                        for q in range(self.plateCSV[i].shape[1]):#cols1.shape[0]
                            X = (cols1[q][0] + cols2[q][0])//2 
                            Y = (cols1[q][1] + cols2[q][1])//2
                            gridCenters.append([self.layers[i],Y,X])
                            gridNames.append(self.plateCSV[i][o][q])
                    # create a colleration between samples and spread sheet
             for p in range(len(sampleCenters)):
                  dist = 999999999
                  refPoint = 0
                  #  loop round and get the lowest distance
                  for o in range(len(gridCenters)): 
                      distance = math.sqrt(
                                       (sampleCenters[p][0]-gridCenters[o][0])*(sampleCenters[p][0]-gridCenters[o][0]) +
                                       (sampleCenters[p][1]-gridCenters[o][1])*(sampleCenters[p][1]-gridCenters[o][1]) +
                                       (sampleCenters[p][2]-gridCenters[o][2])*(sampleCenters[p][2]-gridCenters[o][2]))
                      if dist > distance:
                          dist = distance
                          refPoint = o
                  if (refPoint in PlateToBlob) == False:
                      indx = 1 
                      gotName = True
                      while(gotName):
                          if gridNames[refPoint]+'_'+str(indx) in gridNames:
                              indx = indx+1
                          else: 
                              gridNames.append(gridNames[refPoint]+'_'+str(indx)) 
                              refPoint = len(gridNames)-1
                              gotName = False
                  PlateToBlob.append(refPoint) 
         self.flipPlateVer()
         #print("bounds = " + str(len(bounds)))
         for i in range(len(bounds)):  # was grid names
                 if len(self.layers) > 0:
                     sampleName = gridNames[i]
                 else: 
                     sampleName = 'sample'+ str(i)
                 print(self.workingPath + '/'+"MiTiSegmenter" + '/' + str(sampleName))
                 if os.path.isdir(self.workingPath + '/'+"MiTiSegmenter" + '/' + str(sampleName) ) == False:
                     os.mkdir(self.workingPath + '/'+"MiTiSegmenter"+ '/' + str(sampleName))  
                 if generateRaw == 1: 
                     self.WriteStacks(i, sampleName, bounds, 0)
                 if generatePro == 1: 
                     self.WriteStacks(i, sampleName, bounds, 1)
                 if generateSeg == 1:   
                     self.WriteStacks(i, sampleName, bounds, 2)

         if generateMod == 1:
                  samples = os.listdir(self.workingPath + '/' + 'MiTiSegmenter') 
                  for i in range(len(samples)): 
                      folders = os.listdir(self.workingPath + '/' + 'MiTiSegmenter' + '/' + samples[i])
                      for o in range(len(folders)):  
                          # folder containing the tiff stacks
                          stk = self.LoadImageStack(self.workingPath + '/' + 'MiTiSegmenter' + '/' + samples[i]+ '/'+folders[o]) 
                          self.generate3DModel(stk,self.workingPath + '/' + 'MiTiSegmenter' + '/' + samples[i]+ '/'+folders[o],folders[0])
         if self.RawPath:
                  self.DeleteTempStack()
         showinfo("Completed processing", "Outputs are saved at "+self.workingPath + '/' + 'MiTiSegmenter')
         cv.destroyAllWindows()
         self.show_frame(StartPage)
         
    def ViewImagePreviews(self,img, viewThres, viewCell, downSample, downFactor, thresMax, thresMin, cell, final = False):
        if viewCell == 1: 
           img = img-(img%cell)
        if viewThres == 1: 
            img[img >= thresMax] = 0   
            img[img <= thresMin] = 0
        if final == True:
            img[img > 0] == 255
        return img.astype("uint8")
    
    def rotate(self, origin, point, angle):
        angle = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return int(qx),int(qy)
    
    def putGridOnImage(self,temp, val): 
        for i in range(len(self.layers)): 
            if self.layers[i] < int(val) + self.plateSize and self.layers[i] > int(val) - self.plateSize:
                #print("need redo scale bars")
                self.frames[PlateAlign].ScaleGridBarH.set(self.gridSize[i][0]) 
                self.frames[PlateAlign].ScaleGridBarV.set(self.gridSize[i][1]) 
                halfTemp = (self.gridCenter[0],self.gridCenter[1])
                self.TL = (halfTemp[0]-self.gridSize[i][0],halfTemp[1]-self.gridSize[i][1])
                self.TR = (halfTemp[0]+self.gridSize[i][0],halfTemp[1]-self.gridSize[i][1]) 
                self.BL = (halfTemp[0]-self.gridSize[i][0],halfTemp[1]+self.gridSize[i][1])
                self.BR = (halfTemp[0]+self.gridSize[i][0],halfTemp[1]+self.gridSize[i][1])
                self.TL = self.rotate(halfTemp,self.TL,self.gridRotation) 
                self.TR = self.rotate(halfTemp,self.TR,self.gridRotation) 
                self.BL = self.rotate(halfTemp,self.BL,self.gridRotation)
                self.BR = self.rotate(halfTemp,self.BR,self.gridRotation) 
                if i < len(self.plateCSV):
                    temp = cv.putText(temp,self.plateCSV[i][0][0],self.TL,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    temp = cv.putText(temp,self.plateCSV[i][self.plateCSV[i].shape[0]-1][0],self.BL,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    temp = cv.putText(temp,self.plateCSV[i][0][self.plateCSV[i].shape[1]-1],self.TR,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2) 
                    temp = cv.putText(temp,self.plateCSV[i][self.plateCSV[i].shape[0]-1][self.plateCSV[i].shape[1]-1],self.BR,cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    rowsY = np.linspace((self.TL[0],self.TL[1],self.TR[0],self.TR[1]),(self.BL[0],self.BL[1],self.BR[0],self.BR[1]), num=self.plateCSV[i].shape[0]+1, endpoint=True,dtype=('int32')) 
                    rowsX = np.linspace((self.TL[0],self.TL[1],self.BL[0],self.BL[1]),(self.TR[0],self.TR[1],self.BR[0],self.BR[1]), num=self.plateCSV[i].shape[1]+1, endpoint=True,dtype=('int32')) 
                    for o in range(self.plateCSV[i].shape[0]+ 1): # creates the rows + 2 as we need the number of blocks
                        pnt1 = (rowsY[o][0],rowsY[o][1])
                        pnt2 = (rowsY[o][2],rowsY[o][3])
                        temp = cv.line(temp,pt1=pnt1,pt2=pnt2,color=(0,255,0),thickness=1)
                    for o in range(self.plateCSV[i].shape[1]+1):
                        pnt1 = (rowsX[o][0],rowsX[o][1])
                        pnt2 = (rowsX[o][2],rowsX[o][3])
                        temp = cv.line(temp,pt1=pnt1,pt2=pnt2,color=(0,255,0),thickness=3) 
                        # get the accrow values for the top row and bottom
                        topInterp = np.linspace((self.TL[0],self.TL[1]),(self.TR[0],self.TR[1]),num=self.plateCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                        bottomInterp = np.linspace((self.BL[0],self.BL[1]),(self.BR[0],self.BR[1]),num=self.plateCSV[i].shape[1]+1,endpoint=True,dtype=('int32'))
                    for o in range(topInterp.shape[0]):# down
                        #interpolate between the top and bottom downward looping to fill the gaps 
                        cols = np.linspace(topInterp[o],bottomInterp[o],num=self.plateCSV[i].shape[0]+1,endpoint=True,dtype=('int32')) #inter top i and bottom i by the shape 
                        for q in range(cols.shape[0]):
                            # draw circle at cols 
                            temp = cv.circle(temp,(cols[q][0],cols[q][1]),2,(255,0,0)) 
        return temp

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
                #print(temp[1])
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
        #print(path)
        if path == "": 
            return False
        self.imageStack = None
        self.workingPath = os.path.dirname(path)
        #print(self.workingPath)
        self.RawPath = path
        self.resPopUp = DownsampleWindow(self.master) 
        self.wait_window(self.resPopUp.top)
        dsample = self.resPopUp.value 
        if len(dsample) < 1: 
            dsample = 1
            #print(dsample)
            return False
        self.downsampleFactor = int(dsample)
        self.resPopUp = RawInfoWindow(self.master) 
        self.wait_window(self.resPopUp.top)  
        resolution = self.resPopUp.value.split(";") 
        if len(resolution) < 4: 
            #print("false res")
            return False
        resolution[0] = int(resolution[0])
        resolution[1] = int(resolution[1])
        resolution[2] = int(resolution[2])
        resolution[3] = int(resolution[3])
        height = resolution[2]
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
        cv.destroyWindow("loading")
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
        
    def loadImages(self, path=""):
        if path =="":
            path = filedialog.askdirectory() 
        if path == "": 
            return
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
            showinfo("No Scanner info file", path + " : contains no .info file from the scanner! Let's create one now, then reload the stack. "+
                    "An info file contains the information used to rebuild the scan images, so both the image names and the real-world distance"+
                    " between each scan. It also holds how big the width and height of each pixel is. Using this, we can reconstruct the scan and build a to-scale 3D model.")
            self.generateInfoFile()
            return self.loadImages(path=path)
        
        self.resPopUp = DownsampleWindow(self.master) 
        self.wait_window(self.resPopUp.top)
        resolution = self.resPopUp.value 
        print(resolution)
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
        #print("this code is a duplicat as load image stack, calle the load stack be change to add if downsampling")
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
        cv.destroyWindow("loading")
        self.setInitGraphs()
        return True
            
    def setInitGraphs(self):
        self.imgTop = self.imageStack[0,:,:]
        self.gridSize = ( ((self.imgTop.shape[0]//10)*9)//2, ((self.imgTop.shape[1]//10)*3)//2)
        self.gridCenter = (self.imgTop.shape[0]//2,self.imgTop.shape[1]//2)
        self.imgTop = cv.cvtColor(self.imgTop,cv.COLOR_GRAY2RGB)
        self.imgSide = self.imageStack[:,0,:]
        self.imgFront = self.imageStack[:,:,0] 
        cv.namedWindow("Z",cv.WINDOW_KEEPRATIO)
        r = 300/self.imgFront.shape[1]
        cv.resizeWindow("Z", 300,int(self.imgFront.shape[0]*r));
        cv.createTrackbar("image", "Z" , self.imageStack.shape[2]//2, self.imageStack.shape[2]-1, self.updateFront) 
        self.updateFront(self.imageStack.shape[2]//2)
        cv.moveWindow("Z",0,0)
        
        cv.namedWindow("X",cv.WINDOW_KEEPRATIO)
        r = 300/self.imgSide.shape[1]
        cv.resizeWindow("X", 300,int(self.imgSide.shape[0]*r));
        cv.createTrackbar("image", "X" , self.imageStack.shape[1]//2, self.imageStack.shape[1]-1, self.updateSide) 
        self.updateSide(self.imageStack.shape[1]//2)
        cv.moveWindow("X",300,0)
        
        cv.namedWindow("Y",cv.WINDOW_KEEPRATIO)
        r = 300/self.imgTop.shape[1]
        cv.resizeWindow("Y", 300,int(self.imgTop.shape[0]*r));
        cv.createTrackbar("image", "Y" , self.imageStack.shape[0]//2, self.imageStack.shape[0]-1, self.updateTop) 
        self.updateTop(self.imageStack.shape[0]//2)
        cv.moveWindow("Y",600,0)
        
        cv.waitKey(1)
        self.frames[PlateAlign].MoveGridY.configure(to = self.imgTop.shape[0]*2)
        self.frames[PlateAlign].MoveGridX.configure(to = self.imgTop.shape[1]*2)
        self.frames[PlateAlign].MoveGridY.set(self.imgTop.shape[0])
        self.frames[PlateAlign].MoveGridX.set(self.imgTop.shape[1])
        
    def updateFront(self, val):
        self.slides[0] = int(val)
        temp = self.imageStack[:,:,int(val)-1]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB) 
        for i in range(len(self.layers)):
            temp = cv.line(temp,pt1=(0,self.layers[i]),pt2=(temp.shape[1],self.layers[i]),color=(255,255,0),thickness=5) 
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        cv.imshow("Z",temp)
        cv.waitKey(1)
        
    def updateSide(self, val):
        self.slides[1] = int(val)
        temp = self.imageStack[:,int(val)-1,:]
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        cv.imshow("X",temp)
        cv.waitKey(1)
        
    def updateTop(self, val):
        self.slides[2] = int(val)
        temp = self.imageStack[int(val)-1,:,:]
        temp = cv.cvtColor(temp,cv.COLOR_GRAY2RGB)
        temp = self.ViewImagePreviews(temp,1,1,True,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)#self.ViewImagePreviews(temp,self.viewThresholdVar.get(),self.viewCellVar.get(),False,self.downsampleFactor,self.thresholdMax,self.thresholdMin,self.cellBase)
        temp = self.putGridOnImage(temp,int(val))
        cv.imshow("Y",temp)
        cv.waitKey(1)

app = MiTiSegmenter() 
app.title("MiTiSegmenter")
app.mainloop()
