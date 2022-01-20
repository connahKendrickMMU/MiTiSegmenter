# MiTiSegmenter

MiTiSegmenter is open-source software for the processing of high throughput CT data, to extract and generate 3D models of array-based objects while removing any surrounding mounting medium from the scan. If you use MiTiSegmenter for part of your work, please cite our paper: *****

## Retrieving the code

We provide two options for using the software: a prebuilt .exe or the raw code (Python3.6). 

### Prebuilt exe 

We have prebuilt the program to allow it to run on any Windows-based machine, without the requirement of Python. We cannot guarantee functionality on other operating systems. 

The file can be downloaded from the releases tab.

To launch, simply double-click as with any application. You may encounter an unknown developer warming; when first launching the application. 

### Raw Code 

We provide the raw code to allow for ease of use and to allow modification by other users. All the code can be obtained from this repository.  
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

## Using MiTiSegmenter
Please follow the video guide at: https://mmutube.mmu.ac.uk/media/MiTiSegGuide/1_kha8y1kl
Guide will require the following data: <br />
images: https://figshare.com/articles/Example_data_for_MitiSegmenter_software/12349847 <br />
Labels: https://figshare.com/articles/dataset/Example_labelling_spreadsheets_to_accompany_MiTiSegmenter/17899916 <br />
<!--Using MiTiSegmenter should be straightforward when following the workflow provided. This guide provides step-by-step instructions on using the software as intended. We provide an accompanying sample dataset as an example of array-based microCT data, which can be found at [Figshare](https://figshare.com/articles/Example_data_for_MitiSegmenter_software/12349847)

Since the easing of lockdown in the UK has begun, we have manage to get volunteers to tes the software this, has lead to improvements to the GUI  the guide below still follows the same steps, with the removal of having to press some buttons. As we are updating the GUI at a fast pace we recommend looking here: https://www.dropbox.com/s/hw9d8vre3dg12de/MiTiSegmentatorGuide.mp4?dl=0 for a step by step video.once all the tester are happy, we'll redo the whole guide, new videos are made with each update.

### Loading Data 

Once the program is launched, you will see the default screen below: 

![MitiSegmentator](/images/launched.png) 

Firstly, we must load the data into memory for viewing. To do this, go to **File** (top left) and then **Load Images** 

![File menu Load](/images/LoadMenu.png)

This will bring up a file browser window. Navigate to the folder containing the stack of scan images. By default, the system looks for a **.info** file. If you do not have a .info file go to the **Creating a .info file** section. The .info file will be stored with the images, such as here:  

![File Browser](/images/FileBrowser.png)

An example of the contents of the .info file is also shown above. It is merely a standard text file, providing the pixel size, list of images in order and the distance between each layer. The .info file is produced by **Avizo** when exporting a .tiff stack (if using alternative software, see below). Once navigated to the folder containing both images and the .info file, choose **Select folder** on the file window. The system will request a downsample ratio, we use a ratio of 4 in this example. The system will then load the images into memory. Load time will vary with the size of the dataset. For the provided dataset, this should be about 2 minutes. Currently, to save on memory storage, MiTiSegmenter downsamples the images by a factor of 4 when loading. As noted below in ‘Future Additions’, we will be making this factor customizable in future releases. However, all final outputs of MiTiSegmenter are based on the original full resolution images, not the downsampled data, in order to prevent data loss.  

#### Creating a .info file 

If you use an alternative program to Avizo and do not have an associated .info file, the file can be generated within MiTiSegmenter before the step above. To create a .info file, go to **File** and **Generate Info File**. 

![File menu Gen Info](/images/GenInfo.png) 

![Res Menu](/images/Res.png)

A second window will appear, in which the X, Y, Z resolution of the scan can be entered with a ";" separating the values, e.g. "0.095;0.095;0.095" for the example dataset. Then click **Ok**. A new file explorer will appear. Navigate to the image folder and press **Select folder**; the system will then generate and place a .info file in that folder.  Tiff should be in alpha-numerical order, with 0 padding, this is because of the way programs interpret the file orders. An example if you had 100 file your naming convention should be 0001.tif, 0002.tif etc with an extra 0 at the start.

![Data loaded](/images/DataLoaded.png) 

### Processing Data

Under each orthogonal view, a slider bar lets us scroll through the slices of the image stack in the three planes to get a better view of the data. 

For this program, the workflow follows a 3-step process:
1. Segmentation 
2. Labelling 
3. Export 

#### Stage 1: Segmentation 

The goal of this stage is to remove unwanted background noise and any mounting medium from the scan (shown below), such that only the desired objects remain masked:

![The Goal and the original data](/images/BeforeAfterSeg.png) 

Note: this ‘Segmentation’ stage is optional. If the data is pre-processed, or you otherwise deem this stage unnecessary for your data, you can skip ahead to ‘Labelling’. However, if you are not using the Cel-shading and/or Thresholding functionality (below), set their sliders to 0. 

##### Stage 1.1: Cel-shading 

Cel-shading operates by grouping values within broad ‘bins’, e.g. Cel-shading with a base value of 10 would round all greyscale values to the nearest multiple of 10. Often, the manual selection of threshold values by the user is somewhat arbitrary, and it is challenging to visually track ‘by eye’ the impact of selecting a threshold greyscale value of, say, 178 versus 182, for example. Cel-shading reduces the potential number of threshold values which may be implemented by the user, simplifying this selection. The ‘base value’ (coarseness of the binning) is controlled by the **Cel Base Value** slider. You can view the implementation of Cel-Shading on the current layer by checking the **View Cel Image** checkbox. For the test sample, we use a base value of 40. Adjust the base value using the **Cel Base Value** slider. Then apply this to the whole stack using the **Apply Cel-Shade** button.

![A Cel-Shaded Image](/images/Cel-Image.png)  

##### Stage 1.2: Thresholding

Thresholding is a standard way to remove extraneous objects and background noise from CT scans. Here we work on the principle that the scanned object is a different density than the  surrounding mount. For our purposes, samples are typically mineralized biological tissues, surrounded by a mount comprising foam or low-density plastic. We provide necessary thresholding capabilities with this program, following the same working order as the Cel-shade function. **Threshold Value** adjusts the value used to a threshold; **View Threshold Image** illustrates the implementation of said threshold on the current layer and **Apply Threshold** applies this value throughout the stack. For the test set, we use a threshold value of 255 for the max and a value of 40 for the min.

At this stage, we also provide users with the option to apply ‘canny edge detection’ to remove internal data points from the objects, thus reducing each specimen to a ‘surface’. This is not required in many cases. 

![A Thresholded Image](/images/Threshold.png)  

##### Stage 1.3: Blobbing 

Blobbing allows us to identify connected voxels in 3-dimensions, and thus separate each discrete specimen as a unique object. However, this is a highly memory intensive task, and therefore downsampling and tray separation (see ‘Working with Large Stacks and Low Powered Machines’ below) is recommended. We provide the option to control the minimum size of islands detected as blobs via the **Min Blob Size** slide, which will remove blobs with less volume than the assigned value. Any extraneous noise or small islands of dirt/other unwanted material may be removed in this manner. To blob the stack, use the **Separate the Blobs** button. This may take some time. If the program closes, it means not enough memory was available. Users should instead follow the advice for ‘Working on Low Powered Machines’ (below) or consider further downsampling their dataset before importing into MiTiSegmenter. Once complete, you will notice that the individual blobs are each represented by masks of unique shades of grey.

![A Blobbed stack](/images/Blobbed.png) 

#### Stage 2: Labelling 

This stage allows the user to input CSV files, in order for the exported data to be appropriately labelled with unique specimen identifier codes, without the requirement for users to manually assigning specimen names/numbers. If the objects do not require labelling, you can skip to Stage 3. 

##### Stage 2.1 Traying 

To correctly label the blobs, we first need to identify the number of layers comprising our bulk CT scan and to locate the vertical ‘centre’ of each tray in the images stack. This is done by using the **Apply Traying** button. The gaps between trays is determine when the blobs in a layer is less than the min blob size. The middle of the tray is the center point between the first layer higher than the min blob size and the last. Once this process is complete, the far-right viewer will display horizontal blue lines representing the ‘middle’ of each layer. Also, the left ‘list box’ will display a list of the detected layers. Note: if a layer is incorrect, you can click the layer within the list box and use **Delete Tray** to remove. Similarly, you can add trays manually by scrolling to the layer in the leftmost viewer and using the **Add tray** button. 

![Stacks Layered](/images/TrayLines.png)

##### Stage 2.2 Loading CSVs 

We use a block-based approach for labelling the blobs, so .csv is the preferred file format. Microsoft Excel or similar can be used to export the .csv files (one file per layer), and an example is provided for download with the test dataset. Names may comprise letters and numbers, but without special characters. Duplicate file names should be avoided.

To load the .csv files, use the **Load CSV** button on the far right. A file browser will appear. Choose each .csv file in order from the ‘highest’ to the ‘lowest’ in the z-stack, by selecting the .csv and **Select File**. A new browser window will appear for each .csv. 

If this stage is successful, when scrolling through the leftmost viewer, green gridlines will appear superimposed over the image stack. Grid dimensions will correspond to the row and column dimensions of the associated .csv file. For each grid, file identifiers for the four corner specimens will be displayed, for the user to validate the correct orientation of the grid.

##### Stage 2.3 Aligning the naming grids 

Naming grids will initially all share the centre X, Y and rotation as we assume the trays are stacked  in the same orientation . To move the centre of the naming grid, use the **Grid centre X** and **Grid centre Y** buttons. The orientation of the grid can be adjusted manually using the **Rotate Tray** slider. The X and Y dimensions of the grids may then be individually scaled using the **Scale Tray Horizontal** and **Scale Tray Vertical** to ensure the samples are centred in each grid square. 

For the sample data provided, we orientate the tray to 90 using the **Rotate Tray** slider. We set the centre position as (X) 120 (Y) 180, and a scale of 145 horizontal and 85 vertical for the top plate, and 95 vertical for the bottom.    

![After Alignment](/images/labels.png)

Should the CT dataset be mirrored relative to the actual layout of the plates (as defined in the .csv file), the functions **Flip Trays Horizontal** and **Flip Trays Vertical** located in the **Edit** menu can be used to flip the labelling grid to enable the correct assignment of labels to specimens. CT stacks are often reflected in this manner.

![Edit Menu](/images/FlipEdit.png)

#### Stage 3: Exporting

The final stage is to export the data as individually cropped image stacks and 3D models into their respective folders. To do this, select **File** and **Generate Tiff Stacks**

![Generate Menu](/images/GenerateMenu.png) 

A window will appear, prompting the user to select the format in which data will be exported: 

![Generate Window](/images/GenerateWindow.png)

MiTiSegmenter offers four export options:
* Raw Data - the unprocessed raw data. For each specimen, a subset of the original CT data will be cropped and saved as an 8-bit image stack. Any mounting medium present will remain visible.
* Processed Data - the processed data. As above, except for pixels falling outside the segmentation mask having values of 0 assigned. Pixels within the segmentation mask will remain as 8-bit greyscale. Background noise and the mounting medium should be removed.
* Segmentation Mask - the processed data (above) in binary format. The background is assigned to 0, and thresholded samples as 1. This is for future work to improve the software, and these can be used with the raw data to train segmentation networks, so human interaction will not be required.
* 3D Model - a 3D surface mesh of each specimen, stored in .ply format. Note models are exported after image exportation. If no images are exported, a model cannot be generated. 

![OutputDifferences](/images/OutputDifferences.png)

This process may take some time to fully complete, as it operates on the original full-size images. The stacks will be saved within the same folder as the .info file, within a sub-directory called **Blobstacks**. 

![Output](/images/Output.png)

### Working with Large Stacks and Low Powered Machines

MicroCT datasets are commonly high-resolution and memory intensive. Within MiTiSegmenter, we have therefore implemented the functionality to subset large scans comprising multiple stacked plates of specimens into individual full-resolution image stacks per plate. The protocol outlined above may subsequently be implemented on a plate-by-plate basis.

The original dataset is downsampled upon loading, as described above. Using the slider underneath the left-most viewing window (scrolling in the z-direction), the user identifies the slice representing the top of the uppermost plate (in the example dataset, this is ~slice 58) and then presses the **Add Tray** button. This slice number will then appear within the list box on the far right on the panel. The user continues downwards through the z-stack, identifying gaps between sequential plates/trays (in our example, the gap between the two trays is ~slice 470) and pressing **Add Tray***. Finally, the user identifies the bottom slice of the lowermost plate (in our example, ~slice 996), and presses **Add Tray**. In all instances, care must be taken to avoid selecting slices containing samples of interest. Only background/mount should be present on selected slices.

![Separate Trays 1](/images/SeparateTrays1.png) 

The user should then go to **File** and **Export Trays**. 

![Export trays](/images/ExportTrayMenu.png) 

MiTiSegmenter will create separate full-resolution image stacks of each plate into subfolders, including a .info file to load individual plates into the program. This may take some time. 

![Exported trays](/images/ExportedTrays.png)


## Future Additions 
We have several plans to improve the software in future versions. We welcome any further comments or suggestions:  
* Integration of threading to improve programs response and multi-threading for increase load and output times. 
* Switch to VTK background to allow more diverse file outputs. 
* Add option for user control over downsampling factor 
* Add an option to auto tray separation. 
* Improved segmentation tools to reduce user intervention. 
* Add multi-colour to the blobs.
-->
