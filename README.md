# MiTiSegmentor
MiTiSegmentor is an open source software for the process of CT data to extract and generate 3D models from the Scan while removing the containers. If you use the MiTiSegmentor for part of your work please cite our paper: *****

## Retieving the code
We provide two option to using the software a pre-built .exe or the raw code (python3.6). 

### Prebuilt exe 
We have prebuilt the program to allow it to run on any windows based machine, without the requirement of python. We cannot guarantee funtionality on othe roperating systems. 

The file can be downloaded at: ***** 

To launch simply double click as with any application. 

### Raw Code 

We provide the raw code to allow for ease of use and to allow modification for other uses. All the code can be obtained from this repository.  
The code requires: 
* Python 3.6
* TKinter 
* PIL 7.0.0
* Numpy 1.16.2 
* Opencv-python (CV2) 4.1.1 
* Os 
* Open3d 0.8.0.0 
* Random 
* Pandas 1.0.1 
* Skimage 0.16.2 
We use spyder with anaconda to launch the code.

## Using MiTiSegmentor
Uing the MitiSegmentor is easy once you follow the workflow provided. This guide provides step by step instructions on using the system as intended. We provide a smaple dataset with this for you to try the system, which can be found at: *****

### Loading Data 
Once the program is launch you will seen a screen such as this: 
![MitiSegmentator](/images/launched.png) 

Firstly we must load the data into the system for viewing. To do this got to **File**(top left) and then **Load Images** 
![File menu Load](/images/LoadMenu.png)

This will bring up a file browser window, navigate to the folder contain the scan images. The system has been designed to look for a **.info** file. The .info file will be stored with the images, such as here:  
![File Browser](/images/FileBrowser.png)

You can also see an example of what the .info file contains,as it justa standard text file, showing the pixel size, list of images in order and the distance between each layer. These are the same as the files produced from the **Avizo** program. Once navigated to the folder containing both images of .info file choose **Select Folder** on th file window. The system will then load the images into memory. Currently to save on storage the system downsamples the images by 4 when loading, howver as seen in options we will be making this customisable. In-addtion all output are base off the full resolution images not the downsampled to prevent data loss. 

Once the images have finished loading, you may need to wait a few minutes, the app will change to look similar to this: 

#### Creating a .info file 
If you use and alternative program to Avizo and do not have a .info file, the system allows you to create one prior. To create one go to **File** and **Generate Info File**. 
![File menu Gen Info](/images/GenInfo.png) 
![Res Menu](/images/Res.png)
You will then see a second window appear type the X,Y,Z resolution of the scan into this box with ";" seperating the values e.g. "0.01;0.01;0.01" then click **ok**. Finally a new file explorer will appear and then navigate to the image folder and press **Select Folder** the system will then generate and place a .info file in that folder.
![Data loaded](/images/DataLoaded.png) 

### Processing Data 
Notice under each image we have a slider bar this lets us scroll through the slice of the image stack in the different dimensions to get a better view of the data. 

For this program we follow a 3 step process to the work flow:
1. Segmentation 
2. Labeling 
3. Exportation 

#### Stage 1: Segmentation 

The goal of this stage is to remove background noise and any containers from the scan so only the desired object remains, as shown here: 
![Data Seg](/images/DataSeg.png) 

Note these stages are optional, if the data is preprocessed or if you think the stage is unnecessary for your date. However, due to its scripting if you are not using that stage set the slider to 0. These value will also change on a case by case baises, such as if you have a high or low contrast set, or base scan settings.

##### Stage 1.1: Cel-shading 

Cel-shading groups values within a range of multiple, e.g. a Cel-shade of 10 would mean all value are rounded to the nearest multiple of 10. As the amount of value can be difficult to track by eye we apply this method to help users make a desion of which threshold value to implement. You can view how Cel-Shading looks on the current layer by checking the **View Cel Image** check box. For the test smaple we use a value of 40, to adjust the value use the **Cel Base Value** slider. T then apply this to the whole stack use the **Apply Cel-Shade** button.

##### Stage 1.2: Thresholding

Thresholding is the standard way to remove object and background data from the scans, by work of the principal that the scanned object is denser then the objects. We provide similar capaiblitiess with this program, that follow the same working order as the Cel-shade options. **Threshold Value** adjusts the value used to threshold; **View Threshold Image** to see how that threshold would affect the current layer and **Apply Threshold** to apply this value throughout the stack. For the test set we use a value of 100.

We also provid the option to apply egde detection to remove the inner parts of the objects, but this is not required in many cases. 

##### Stage 1.3: Blobbing 

### Stage 2: Labeling 

This stage allows the user to input CSV file to allow the exported data to be labelled properly, without the user ahving to manually check and labeel the outputs. If the objects do not require labeling, you can skip to stage 3.

### Working with large stacks and low powered machines
As many know the stack generated by the scanner are both high-resoltuion and memory intentsive. In-addition, to getting acces to these key resources usually means scan can contain multiple object that are not your current focus. To over come this we implement a secondary function to separate the different layers, although it require the complete stack to be loaded (at any downsample size). Doing this can significantly improve the processing time and memory requirements. This will need to be adjusted on a per case biases.
![Separate Trays 1](/images/SeparateTrays1.png) 

To use this functionality use the slider on the leftmost images (that scroll the stack from top to bottom). For our trays we scroll to the tops of each tray and then press the **Add Tray** button. Notice now that the tray number appears in the list box on the far right. We then repeat this inbetween the trays so they are now  5 values in the far right box (one for the top of the top tray, one for the bottom of the bottom tray and 3 for inbetween the four stacked trays. We take care that we do not choose a section which contains an object. 
![Separate Trays 2](/images/SeparateTrays2.png) 

The we go to **File** and **Export Trays**. 
![Export trays](/images/ExportTrayMenu.png) 

The program will create seperate full-resolution image stacks of the regions into subfolders, including an info file to load individual trays into the program, this maybe take some time. 
![Exported trays](/images/ExportedTrays.png)

### Labeling Data

### Exporting Data

## Future Additions 
We have limited available to time work on improving the software. However, we have several plans to improve the software infuture use any aid in performing these update would be appreciated.  
* Intergation of thread to improve programs response and multi-threading for increase load and output times. 
* Switch to VTK background to allow more diverse file outputs. 
* Add option for input downsampling size.
* Add option to auto tray separation.
