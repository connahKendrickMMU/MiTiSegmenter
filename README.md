# MiTiSegmentor

MiTiSegmentor is open-source software for the process of CT data to extract and generate 3D models from the scan while removing the containers. If you use the MiTiSegmentor for part of your work, please cite our paper: *****

## Retrieving the code

We provide two option to using the software a prebuilt .exe or the raw code (python3.6). 

### Prebuilt exe 

We have prebuilt the program to allow it to run on any windows-based machine, without the requirement of python. We cannot guarantee functionality on other operating systems. 

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

Using the MiTiSegmentor is easy once you follow the workflow provided. This guide provides step by step instructions on using the system as intended. We provide a sample dataset with this for you to try the system, which can be found at [Figshare](https://figshare.com/articles/Example_data_for_MitiSegmenter_software/12349847)

### Loading Data 

Once the program is launch, you will see a screen such as this: 

![MitiSegmentator](/images/launched.png) 

Firstly, we must load the data into the system for viewing. To do this got to **File** (top left) and then **Load Images** 

![File menu Load](/images/LoadMenu.png)

This will bring up a file browser window, navigate to the folder containing the scan images. The system has been designed to look for a **.info** file. The .info file will be stored with the images, such as here:  

![File Browser](/images/FileBrowser.png)

You can also see an example of what the .info file contains, as it just a standard text file, showing the pixel size, list of images in order and the distance between each layer. These are the same as the files produced from the **Avizo** program. Once navigated to the folder containing both images of .info file choose **Select Folder** on the file window. The system will then load the images into memory. Currently, to save on storage, the system downsamples the images by 4 when loading; however, as seen in options, we will be making this customisable. In-addition all output is based on the full resolution images, not the downsampled to prevent data loss.  

#### Creating a .info file 

If you use and alternative program to Avizo and do not have a .info file, the system allows you to create one prior. To create one, go to **File** and **Generate Info File**. 

![File menu Gen Info](/images/GenInfo.png) 

![Res Menu](/images/Res.png)

You will then see a second window appear, type the X, Y, Z resolution of the scan into this box with ";" separating the values, e.g. "0.095;0.095;0.095" for our example then click **ok**. Finally, a new file explorer will appear and then navigate to the image folder and press **Select Folder** the system will then generate and place a .info file in that folder.

![Data loaded](/images/DataLoaded.png) 

### Processing Data

Notice under each image we have a slider bar this lets us scroll through the slice of the image stack in the different dimensions to get a better view of the data. 

For this program, we follow a 3-step process to the workflow:
1. Segmentation 
2. Labelling 
3. Exportation 

#### Stage 1: Segmentation 

The goal of this stage is to remove background noise and any containers from the scan so only the desired object remains, as shown here:

![The Goal and the orignal data](/images/BeforeAfterSeg.png) 

Note these stages are optional, if the data is pre-processed or if you think the stage is unnecessary for your date. However, due to its scripting if you are not using that stage, set the slider to 0. These values will also change on a case by case biases, such as if you have high or low contrast settings, or base scan settings.

##### Stage 1.1: Cel-shading 

Cel-shading groups values within a range of multiple, e.g. a Cel-shade of 10 would mean all value are rounded to the nearest multiple of 10. As the amount of value can be difficult to track by eye, we apply this method to help users decide which threshold value to implement. You can view how Cel-Shading looks on the current layer by checking the **View Cel Image** checkbox. For the test sample, we use a value of 40, adjust the value using the **Cel Base Value** slider. Then apply this to the whole stack use the **Apply Cel-Shade** button.

![A Cel-Shaded Image](/images/Cel-Image.png) 

##### Stage 1.2: Thresholding

Thresholding is the standard way to remove object and background data from the scans, by work of the principal that the scanned object is denser than the objects. We provide similar capabilities  with this program, that follow the same working order as the Cel-shade options. **Threshold Value** adjusts the value used to threshold; **View Threshold Image** to see how that threshold would affect the current layer and **Apply Threshold** to apply this value throughout the stack. For the test set, we use a value of 40.

We also provide the option to apply edge detection to remove the inner parts of the objects, but this is not required in many cases. 

![A Thresholded Image](/images/Threshold.png) 

##### Stage 1.3: Blobbing 

Blobbing allows us to see which voxels are connected, thus separate each 3D object. However, this is a highly memory intensive task, downsampling and tray separation (see Working with large stacks and low powered machines) is recommended. Without methods, you may notice small chunks floating around left out by the thresholding because of this we provide the **Min Blob Size** slide which will remove chunks with less volume than the value. To blob the stack, use the **Separate the Blobs** button, this may take some time. If the program closes, it means not enough memory was available. One complete you will notice that the individual blobs will have different shades of grey to represent them.

![A Blobbed stack](/images/Blobbed.png) 

#### Stage 2: Labelling 

This stage allows the user to input CSV files to allow the exported data to be appropriately labelled, without the user having to check and label the outputs manually. If the objects do not require labelling, you can skip to stage 3. 

##### Stage 2.1 Traying 

To correctly label the blob, we need to identify how many and the centre of trays in the images stack. This is done by using the 
**Apply Traying** button. This looks for the densest layers to define a middle and gaps where no blob is present to define a gap between trays. Once this is done, the far-right image will show blue lines representing the "middle" of each tray. In-addition the left list box will have a list of the available tray layers. Note if a layer is incorrect, you can click the layer in the list box and use **Delete Tray** to remove, similarly you can add trays manually by scrolling to the layer in the leftmost window and using the **Add tray** button. 

![Stacks Layered](/images/TrayLines.png)

##### Stage 2.2 Loading CSVs 

We use a block-based approach for labelling the blobs, so a CSV is a natural choice. Microsoft Excel can be used to export the CSV, and an example is with the test data, names should be alphabetical and can include number, but without special characters.

To load the CSVs, use the **Load CSV** button on the far right. A file browser will appear, choose each CSV file in order from the highest to the lowest in the stack, by selecting the CSV and **Select File**, and a new browser will appear for each CSV. 

If this stage is successful when scrolling through the leftmost image, green grids will appear over the image. The grid will also have the four corner points labelled to identify how to orientate the trays quickly. 

##### Stage 2.3 Aligning the trays 

Trays will all share the centre X, Y and rotation as we assume the trays are stacked. To move to the centre of the trays, use the **Grid centre X** and **Grid centre Y**. The rotation should then be adjusted using the **Rotate Tray** slider. Then each tray should be individually scaled using the **Scale Tray Horizontal** and **Scale Tray Vertical** to allow the blobs to be centred in each grid square. 

For the sample data centre, we use (X) 122 (Y) 184 and a scale of 157 Horizontal and 93 vertical for the top and 102 vertical for the bottom. 

![After Alignment](/images/labels.png)

If the image is mirrored as some scanner do, you can use the functions **Flip Trays Horizontal** and **Flip Trays Vertical** int the **Edit** menu to flip the grid to enable the labels to match. 

![Edit Menu](/images/FlipEdit.png)

#### Stage 3: exporting

The final stage of the system is to export the data into separate files so that each blob will have its folder. To do this use the **File** the **Generate Tiff Stacks**

![Generate Menu](/images/GenerateMenu.png) 

This will bring up a window asking what data you would like to export: 

![Generate Window](/images/GenerateWindow.png)

We give four options, the differences seen below:
* Raw Data is the unprocessed raw data. This means for each blob they will be a tiff stack containing only that blob without any processing.
* Processed Data is the processed data, so all background (unwanted) data is removed. However, all the details, such as the blob density remains.
* Segmentation Mask is the processed data, but in binary format so 0 background and 1 is a blob. This is for future work to improve the software, and these can be used with the raw data to train segmentation networks, so human interaction will not be required.
* 3D Model is a 3D model of the blob. Note models are exported after image generation. If no images are generated, a model cannot be generated. 

![OutputDifferences](/images/OutputDifferences.png)

This may take some time to fully complete as it uses the full-size images. The stacks will be saved in the folder as the info file under the main directory called **Blobstacks**. 

![Output](/images/Output.png)

### Working with large stacks and low powered machines

As many know the stack generated by the scanner are both high-resolution and memory intensive. In addition, to getting access to these critical resources usually means scan can contain multiple objects that are not your current focus. To overcome this, we implement a secondary function to separate the different layers, although it requires the complete stack to be loaded (at any downsample size). Doing this can significantly improve the processing time and memory requirements. This will need to be adjusted on a per case bases.
![Separate Trays 1](/images/SeparateTrays1.png) 

To use this functionality, use the slider on the leftmost images (that scroll the stack from top to bottom). For our trays, we scroll to the tops of each tray and then press the **Add Tray** button. Notice now that the tray number appears in the list box on the far right. We then repeat this in between the trays, so they are now  3 values (58, 470 and in the far right box (one for the top of the top tray, one for the bottom of the bottom tray and 1 for in between the stacked trays. We take care that we do not choose a section which contains an object. 

Then we go to **File** and **Export Trays**. 

![Export trays](/images/ExportTrayMenu.png) 

The program will create separate full-resolution image stacks of the regions into subfolders, including an info file to load individual trays into the program. This may take some time. 

![Exported trays](/images/ExportedTrays.png)


## Future Additions 
We have limited available to time work on improving the software. However, we have several plans to improve the software in future use any aid in performing these updates would be appreciated.  
* Integration  of thread to improve programs response and multi-threading for increase load and output times. 
* Switch to VTK background to allow more diverse file outputs. 
* Add option for input down sampling size.
* Add an option to auto tray separation. 
* Auto segmentation to remove human interaction
