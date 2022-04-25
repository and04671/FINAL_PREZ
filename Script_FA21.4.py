#!/usr/bin/env python
# coding: utf-8

# 
# # Finding the Lowest Energy Pathway for User-Selected Locations and Mobility Parameters
# 
#     Independent Research 8990
#     Cole Anderson
#     12/22/2021

# ## Import needed modules (run EVERY time first)
# Module setup and variable definition

# In[ ]:


import requests #used in ETL
import zipfile #used to unzip ETL files
import arcpy # used for central functions
import geopy #used for Nomatim locator attempt
import json # used in ETL
from geopy.geocoders import Nominatim
import utm #used in locator portion
import arcpy.nax #used in router
import arcpy.na #""
from arcpy import env

#script folder location
baseURL = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code'

#GDB location
createGDB = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb'

#Network Feature Dataset Location
createNW = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\Network'

#Network layer location
buildNW = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\Network\AllFinal'

#road lines shapefile
RCLshp = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\RoadCenterline.shp'

#road lines layer 
RCL = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\Network\RoadCenterline'

#road buffer layer
Buffer = r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\Network\Road_Buffer'


# ## Retrieve data from MN Geospatial Commons and FTP Server
# This gathers the roads file and the DEM file and unzips them

# In[ ]:


# a function to search MN_Geospatial Commons for specific datasets
def downloader (search_query, result_num, resource_num):
    ##############################
    # the URL is the MN Geospatial Commons API location + search terms you want
    big_url = 'https://gisdata.mn.gov/api/3/action/package_search?q=' + search_query
    
    # Sends a request to the API for the set big_url
    # API returns response object
    response = requests.get(big_url, verify = False)
    
    # API response object need to be loaded as a JSON
    json_response = json.loads(response.content)
    
    # this enters the first layer of the JSON to a list of results
    result_options = json_response['result']['results']
    
    #select the result from the JSON 
    chosen_result = result_options[result_num]
    
    # enter second layer to resources and select resource number
    resources_under_result= chosen_result['resources'][resource_num]
    
    # find the URL for that selected resource for retreival
    chosen_resource = resources_under_result['url']
    print(chosen_resource)

    # send a request to the resource URL and get response object
    URL_request = requests.get(chosen_resource)
    
    #save this response object to a zipfile (because response is a ZIP)
    with open('filename.zip', 'wb') as f:
        f.write(URL_request.content)  
        f.close()
        
    # extract the zipfile contents to central folder (Code)    
    with zipfile.ZipFile("filename.zip","r") as zip_ref:
        zip_ref.extractall(baseURL)
    
    # confirms completion
    print('Download and extraction complete. Check notebook folder')
##############################################

#execute function for DEM and RoadCenterline datasets
downloader('us-mn-state-metrogis-trans-road-centerlines-gac',8,2)
downloader('dataset/elev-dtm-30m-condpr-a',1,1)


# ## LAZ Data
# This downloads each need LAZ (zipped LAS) files, but they must be unzipped using LASTools in the command line.

# In[ ]:


#to collect LAZ files for DEM integration
#same general process as first download ETL, except the links are directly recovered and content saved
#ie, no "retreive,get,use new address, get" like CKAN
import requests
def retrieve (link, save):
    response = requests.get(link)
    with open(save, 'wb') as f:
     f.write(response.content)
     f.close()
        
# numbers indicate tile and date. letters are subtiles denoting location.       
for each in ["4342-01-25_c_a","4342-01-25_c_b",
            "4342-01-25_c_c","4342-01-25_c_d",
            "4342-01-25_d_a","4342-01-25_d_b",
            "4342-01-25_d_c","4342-01-25_d_d",
            "4342-02-25_a_a","4342-02-25_a_b",
            "4342-02-25_b_a","4342-02-25_b_b"]:
        link = "https://resources.gisdata.mn.gov/pub/data/elevation/lidar/county/hennepin/laz//"+ each + ".laz"
        print(link)
        save = 'LAZ_data2//'+ each +'.laz'
        retrieve (link, save)

# Must unzip using command line laszip.exe - found as part of LASTools download


# ## Create a new GDB and feature dataset to work in
# Creates a blank geodatabase and places a feature dataset with UTM15 spatial reference inside of it.

# In[ ]:


# Find the spatial reference from RoadCenterline dataset (UTM 15T)
spatial_ref = arcpy.Describe(RCLshp).spatialReference

arcpy.CreateFileGDB_management(baseURL, 'Prototype2')

# create a new feature dataset inside the project GDB using spatial reference from above
arcpy.CreateFeatureDataset_management(createGDB, 'Network', spatial_ref)


# ## Clip roads to study area and buffer bridge roads, import to dataset
# This clips the roads to the study geometry, then selected bridge areas out, which are buffered.

# In[ ]:


#roads clipped to UMN study area
arcpy.env.workspace = baseURL
arcpy.Clip_analysis('RoadCenterline.shp', createNW + '//Study_Geom_1', createNW +'//RoadClip')

#only bridges in UMN study area
arcpy.Clip_analysis('RoadCenterline.shp', createNW + '//Bridge_Geom_1', createNW +'//Bridges')

#buffered, only bridges in UMN study area
arcpy.Buffer_analysis(createNW + '//Bridges', createNW + '//BridgeBuffer', '50 meters', 'FULL', 'ROUND', "ALL")


# ## Convert LAS  to LAS Dataset, import to dataset (or gdb)
# This converts LAS files into a LAS dataset, and then to a raster, which is saved to the geodatabase.

# In[ ]:


arcpy.env.workspace = baseURL
arcpy.conversion.ConvertLas('LAZ_data2', 'LAZ_data2')#, 'SAME_AS_INPUT', '0', 'NO_COMPRESSION',"" , 'spatial_ref')#, {in_coordinate_system})

#LAS > Dataset
arcpy.management.CreateLasDataset('LAZ_data2', 'LASDataset')#, 'NO_RECURSION', '', spatial_ref)#, {compute_stats}, {relative_paths}, create_las_prj)

#turn into raster
arcpy.conversion.LasDatasetToRaster('LASDataset.lasd','LASRaster', 'ELEVATION')#, {interpolation_type}, {data_type}, {sampling_type}, {sampling_value}, {z_factor})
sr = arcpy.SpatialReference("NAD 1983 UTM Zone 15N")
arcpy.DefineProjection_management('LASRaster',sr)

arcpy.CopyRaster_management('LASRaster', createGDB + '\\AllLAS') 


# In[ ]:


#Raster is clipped by Road_Buffer
from arcpy.sa import*
x = ExtractByMask(r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\LASRaster',r'Prototype2.gdb\\Network\\BridgeBuffer')
x.save('ClippedLASRaster.tif')
arcpy.CopyRaster_management('ClippedLASRaster.tif', createGDB + '\\ClippedLAS') 


# ## DEM import to dataset & clip to study area
# Simply pulls the DEM into the geodatabase and masks it to same geometry as clipped roads
# 

# In[ ]:


# set workspace 
arcpy.env.workspace = baseURL

#bring 30m DEM into the GDB and trim to study area (cannot bring inside feature dataset)
arcpy.CopyRaster_management('\\digital_terrain_model.gdb\DTM30CONDPR_A', createGDB + '\\DEM')
from arcpy.sa import*
x = ExtractByMask(r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\DEM', createNW +'\Study_Geom_1')
x.save(r'C:\\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype2.gdb\ClippedDEM')


# ## Use DEM/LIDAR to calculate elevations & slopes 
# Iterative surface information function give roads DEM elevation/slope, then overwrites LIDAR area with LIDAR elevation/slope
# 
# 

# In[ ]:


#reset workspace
arcpy.env.workspace = createNW + "//RoadClip"
roads = arcpy.env.workspace

arcpy.AddSurfaceInformation_3d(roads, createGDB + "//ClippedDEM", "AVG_SLOPE;Z_MAX;Z_MIN", "LINEAR", 0.1, .328)
#already in M
arcpy.AddSurfaceInformation_3d(roads, createGDB + "//ClippedLAS", "AVG_SLOPE;Z_MAX;Z_MIN", "LINEAR", 0.1 )


# ## Remap slope and distance fields
# The slope and distance fields need to be standardized so they are taken into account equally by the router.

# In[ ]:


arcpy.env.workspace = createNW 
#standardizes slope and distance to the same scale
#arcpy.management.AddField('RoadClip2',"Avg_Slope_MIN_MA")
arcpy.management.StandardizeField("RoadClip", "Avg_Slope", "MIN-MAX",1,100)
arcpy.management.StandardizeField("RoadClip", "Shape_Length", "MIN-MAX",1,100)


# ## Weight distance and slope
# Technically this block is unneeded- it is an option to weight the entire network dataset to start with rather than in the network properties. It is set up here to just cut all values in half, having no effect.

# In[ ]:


#select weighting for equation
s_weight = .5
d_weight = .5

# calculate custom variable fields for slope and distance based on weighting
arcpy.CalculateField_management("RoadClip", "Dist_Cust",
                                "!Shape_Length_MIN_MAX! * {}".format(s_weight),"Python3","","DOUBLE")

arcpy.CalculateField_management("RoadClip", "Slope_Cust",
                                "!Avg_Slope_MIN_MAX! * {}".format(d_weight),"Python3","","DOUBLE")


# ## Create a network dataset from clipped roads
# This block creates the network dataset required for routing from the clipped down road segments layer, then builds it to ensure it is created.

# In[ ]:


#reset workspace
arcpy.env.workspace = createGDB

# create a new nework dataset from the RoadCenterline layer (with a few calculated attributes)
arcpy.na.CreateNetworkDataset(createNW, "AllFinal", ["RoadClip"], "ELEVATION_FIELDS")

#build the network so that it exists
#arcpy.na.BuildNetwork(buildNW)


# ## Create base travel mode on network w/ restrictions
# Initial travel mode creation must be done manually in ArcGIS Pro

# #### Notes
#     Must use ARCGIS GUI 1x
#     Base Mode must be created manually
#     base form = (distance)(distance factor = 1)+(slope)(slope factor = 1)
#     must include restrictions by hand too.
# 
# 
# #### Data Type: File Geodatabase Network Dataset
#     Database: C:\Users\Cole\Documents\GitHub\EnergyMobile\Code\Prototype_2.gdb 
#     Feature Dataset: Network 
#     Network: All_ND
#     Dataset Version: 10.1
# 
# #### Build Status: Built
#       The network dataset has been built.
#       Build Time: Fri Oct 29 13:11:38 2021
# 
# #### Connectivity: 
#       Policies: 
#         RoadClip2 edges use End Point connectivity policy.
#         Elevation Model: Elevation Fields
# 
# #### Travel Mode: Mobility
#         Uses Costs: 
#         Impedance: Energy
#         Distance Cost: Length
# #### Costs: 
#     Cost: Length
#         Value: [Shape]
#     Cost: Energy
#         Value: 1*(!Dist_Cust!) + 1*(!Slope_Cust!)
#   
# #### Restrictions:
#       Value: [ST_PRE_TYP] = "Interstate"

# ## Gather addresses & preferences, solve, and return route
# This block creates a layer with the desired start and end route addresses using ArcGIS Geocoding Service outputs translated into UTM coordinates.
# 
# Second, this block runs the actual router, taking in the newly developed travel mode with its slope/distance parameters alongside the start/end points layer. Assuming success the router will complete and output a poly line path.

# In[ ]:


print("running router.")
# Travel Mode
mode = "Mobility"

# Route Name (always "R<route>_<D:S ratio>")
name = "R2_140"
#################################################

#reset workspace
arcpy.env.workspace = createGDB

# Find spatial ref from original RoadCenterline.shp (UTM 15T)
spatial_ref = arcpy.Describe(RCLshp).spatialReference

# Create a new point feature class using the spatial reference
arcpy.CreateFeatureclass_management(createGDB,"PtsLayer", "POINT", spatial_reference = spatial_ref)

arcpy.na.BuildNetwork(buildNW)
# This works so long as the UTM zone is 15T!

#################################################
#ARCGIS Router
print('Enter start address in format <address>, <city>, <st. abbreviation> <zip>')
startinput = input("Enter Start Address in format:'1670 W Peachtree St NE, Atlanta, GA 30309'")
endinput = input("Enter End Address in format:'1670 W Peachtree St NE, Atlanta, GA 30309'")

#this calls the Arc geocode server
locator_path = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/ArcGIS World Geocoding Service"
locator = arcpy.geocoding.Locator(locator_path)

#takes first geocode results, defines them as utm coordinates
geocoding_candidates = locator.geocode(startinput, True, maxResults = 1)
inside = geocoding_candidates[0]
location = (inside["Y"],((inside["X"])))
coord = utm.from_latlon(location[0], location[1])
print(coord)

#takes first geocode results, defines them as utm coordinates
geocoding_candidates2 = locator.geocode(endinput, True, maxResults = 1)
inside2 = geocoding_candidates2[0]
location2 = (inside2["Y"],((inside2["X"])))
coord2 = utm.from_latlon(location2[0], location2[1])
print(coord2)
####################################################

# Select the new point feature class
feature_class_source = "PtsLayer"

# Use a cursor to insert the two coordinates
cursor = arcpy.da.InsertCursor(feature_class_source,"SHAPE@XY")
cursor.insertRow([coord])
cursor.insertRow([coord2])
del cursor

###################################################

# This ND_layer is only temprorary to allow faster processing, not saved to ROM 
ND_layer = "TestRoute"

# Create a network dataset layer (ND_Layer) from the Network for faster processing
arcpy.nax.MakeNetworkDatasetLayer(buildNW, ND_layer)

# Instantiate a Route solver object
route = arcpy.nax.Route(ND_layer)

# Set the Travel Mode for this solver
nd_travel_modes = arcpy.nax.GetTravelModes(ND_layer)
#mode will refer to the selection made earlier
travel_mode = nd_travel_modes[mode]

#load the Route solver's Travel Mode
route.travelMode = travel_mode

#reset workspace
arcpy.env.workspace = createNW

# Load the points layer into the solver
route.load(arcpy.nax.RouteInputDataType.Stops, createGDB + '\\PtsLayer')

#reset workspace
arcpy.env.workspace = createGDB

# Set output path

output = '\\' + name 
output_path = createNW + output

# Excecute the route solve
result = route.solve()
print("Done")
    # Check for success
if result.solveSucceeded:
    result.export(arcpy.nax.RouteOutputDataType.Routes, output_path)
    print("Solving Complete")
    arcpy.management.Delete("TestRoute")    
    #arcpy.management.Delete(createGDB + '\\'+"PtsLayer")
    print("stop")
else:
    print("Solved failed")
    print(result.solverMessages(arcpy.nax.MessageSeverity.All))
    arcpy.management.Delete("TestRoute")    
    #arcpy.management.Delete(createGDB + '\\'+"PtsLayer")
    print("stop")


# ## Manual Deletes
# Override deletes if not using cost surface function

# In[ ]:


arcpy.management.Delete("TestRoute")
arcpy.management.Delete(createGDB + '\\'+"PtsLayer")


# ## Cost Surface
# This block takes the information from a specific route solve and creates a concentric service area for energy expenditure

# In[ ]:


import arcpy
arcpy.CheckOutExtension("network")
arcpy.env.workspace = createGDB
nds = buildNW
nd_layer_name = "All"

#variable naming
input_facilities = createGDB + "//PtsLayer"
output_polygons = createGDB + "//OutGonsR1_140"

############################################

# Create a network dataset layer and get the desired travel mode for analysis
arcpy.nax.MakeNetworkDatasetLayer(nds, nd_layer_name)
nd_travel_modes = arcpy.nax.GetTravelModes(nd_layer_name)
travel_mode = nd_travel_modes["Mobility"]

# Instantiate a ServiceArea solver object
service_area = arcpy.nax.ServiceArea(nd_layer_name)

# Set properties
service_area.timeUnits = arcpy.nax.TimeUnits.Minutes
service_area.defaultImpedanceCutoffs = [100, 200, 300, 500, 1000, 2000, 3000, 5000]
service_area.travelMode = travel_mode
service_area.outputType = arcpy.nax.ServiceAreaOutputType.Polygons
service_area.geometryAtOverlap = arcpy.nax.ServiceAreaOverlapGeometry.Dissolve
# Load inputs

service_area.load(arcpy.nax.ServiceAreaInputDataType.Facilities, input_facilities)
# Solve the analysis

result = service_area.solve()

# Export the results to a feature class
if result.solveSucceeded:
    result.export(arcpy.nax.ServiceAreaOutputDataType.Polygons, output_polygons)
else:
    print("Solve failed")
    print(result.solverMessages(arcpy.nax.MessageSeverity.All))
arcpy.management.Delete(nd_layer_name)


# again, manual deletes

# In[ ]:


#additional seperate deletes
arcpy.management.Delete(nd_layer_name)
arcpy.management.Delete("TestRoute")
arcpy.management.Delete(createGDB + '\\'+"PtsLayer")

