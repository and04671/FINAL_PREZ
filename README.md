# EnergyMobile Accessible Router

Project Repository Summary:
EnergyMobile is a routing application designed to create 
customized least energy cost paths for pedestrians with
mobility limitations. It takes a user selected set of 
addresses and a preferred balance of weighting distance 
and grade. 

Update Information:
The first prototype was developed in spring 2021 as a skeletal
python script. This current version is in the process of making 
updates and accuracy improvements. These include: improving slope accuracy, 
adding restictions to travel modes, updating weighting and energy equations, 
creating a user selected mode and address, automating most of the code into 
a more user friendly repetitive structure, and general cleaning.

Abstract:
The goal for this study is to define and find the least energy route between a start and end address for different levels of mobility as selected by the user. This is accomplished via Python script and ArcGIS routing tools. The base data utilized for the project are a feature dataset of metro area roads, 30-meter DEM of Minnesota, and 12 LIDAR LAS blocks from MN DNR. While the prototype program effectively “solved” the problem in the initial study, it calculated energy incorrectly for a single travel mode, displaying results to a clunky UI. This version works via the same design with a number of fundamental improvements. Primarily, it relies on more reasonable energy calculations, creates a more accurate network dataset, allows user input, and utilizes reasonable restrictions. It is also designed to output a cost surface from a start location using the same information. The results will again be verified for feasibility; pedestrians must be able to traverse the path, the route should be found to be the lowest possible energy for the travel mode, and all cases must properly follow set restrictions. The results indicate a significant improvement in both form and function over the first prototype. The results produce different routes for different weighting in a way that makes sense if traced out. Though it may make more sense to add an accessibility module to an existing map platform, this project effectively builds on and displays GIS skills acquired in the graduate program.

Citations:
ESRI. (2021). What is the network analyst module (arcpy.nax). ArcGIS Pro Help. Retrieved May 10, 2021, from https://pro.arcgis.com/en/pro-app/latest/arcpy/network-analyst/what-is-the-network-analyst-module.htm 

ESRI. (2021). Create a network dataset. ArcGIS Pro Help. Retrieved May 10, 2021, from https://pro.arcgis.com/en/proapp/latest/help/analysis/networks/how-to-create-a-usable-network-dataset.htm 

ESRI. (2021). Route. ArcGIS Pro Help. Retrieved May 10, 2021, from https://pro.arcgis.com/en/pro-app/latest/arcpy/networkanalyst/route.htm 

De Neef, M. (2013, May 29). Gradients and cycling: How much harder are STEEPER CLIMBS? The Climbing Cyclist. Retrieved May 10, 2021, from http://theclimbingcyclist.com/gradients-and-cycling-how-much-harder-are-steeper-climbs

Isenburg, M. (2019). Free and lossless lidar compression. LASzip. Retrieved December 19, 2021, from https://laszip.org/ 

N. Bolten, S. Mukherjee, V. Sipeeva, A. Tanweer and A. Caspi, "A pedestrian-centered data approach for equitable access to urban infrastructure environments," in IBM Journal of Research and Development, vol. 61, no. 6, pp. 10:1-10:12, 1 Nov.-Dec. 2017, doi: 10.1147/JRD.2017.2736279.

Python Software Foundation. (2021, July). Developer Interface. Requests: HTTP for humans™¶. Retrieved December 19, 2021, from https://docs.python-requests.org/en/latest/ 

Metropolitan Council. (2020, March 3). Road centerlines (Geospatial Advisory Council Schema). Retrieved May 10, 2021, from https://gisdata.mn.gov/dataset/us-mn-state-metrogis-trans-road-centerlines-gac

U.S. Geological Survey. (2004, January 5). Minnesota digital elevation model - 30 meter resolution. Retrieved May 10, 2021, from https://gisdata.mn.gov/dataset/elev-30m-digital-elevation-model

TASKAR Research Center, (2016). Accessmap. University of Washington. Retrieved December 19, 2021, from https://www.accessmap.io/ 

The Land Management Information Center, MN Planning (2012). (Hennepin County LAZ tile data) [FTP Server]). Minnesota: MN DNR. Retrieved October 20, 2021 from https://resources.gisdata.mn.gov/pub/data/elevation/lidar/county/hennepin/laz/  


  



