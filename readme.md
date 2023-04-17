# COOKIEPOLY: computing polygons' emissions starting from gridded emissions

Cookiepoly is a python code to "cut" a well (geo) defined grid onto a selected administrative shape file.

## Description

It tries to read the most common format: <br>
GRID <br>
&nbsp;&nbsp;&nbsp;&nbsp;(1) netcdf (with specific a couple of specific internal organization). Useful for TOP-DOWN (but with some adaptation also fot BU) <br>
&nbsp;&nbsp;&nbsp;&nbsp;(2) asc (BU) <br>
&nbsp;&nbsp;&nbsp;&nbsp;(3) geotiff (BU) <br>
POLYGONS <br>
&nbsp;&nbsp;&nbsp;&nbsp;(1) shp folder organization, with some specification about which code is the key <br>


## Getting Started

### Dependencies

* python 3.10
* conda
* fm_3_10.yml packages needed

### Installing

* github clone
* $app_root is your unzip folder root

(1)Copy in an user-executable destination folder the file fm.zip (or the full clone from github) <br>
(2)Extract all the contents in a user-executable folder ($app_root) <br>
(3)-->Follow PYTHON/CONDA ENV instructions<-- <br>
(4)Create (or check the existence and the full permission of) $app_root/output <br>
(5a)Change/adapt the scripts <br>
&nbsp;&nbsp;&nbsp;&nbsp;(a)for windows they are in $app_root + \dev\bat\*.bat <br>
&nbsp;&nbsp;&nbsp;&nbsp;(b)for unix they are in $app_root + /dev/sh/*.sh <br>
(5b)Change properly $app_root value (for the scripts related to your installation Win or Unix) <br>
(5c)Change properly $py_exec value (put exactly the full path folder of your conda/bin python3_10 executable) <br>
(5d)Create $app_root/output/zs folder <br>


* PYTHON/CONDA ENV

Requisite:

_python 3.10
_conda installation: conda https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda

It is strongly reccomended to create a brand new compatible env. To do this, go to conda prompt. <br>
(1)Change folder to: $app_root/dev/ <br>
(2)Type: conda env create --name fm_3_10 --file=fm_3_10.yml <br>

## Executing program

### SCRIPT DESCRIPTION

* EXAMPLE -1- (default mode, single ASC file)

[$app_root/dev/sh/do_ASC_single.sh]
[$app_root\dev\bat\do_ASC_single.bat]

* EXAMPLE -2- (default mode, multiple ASC files in a dir)

[$app_root/dev/sh/do_ASC_folder.sh]
[$app_root\dev\sh\do_ASC_folder.bat]

* EXAMPLE -3- (default mode, single TIF file)

[$app_root/dev/sh/do_GTIFF_single.sh]
[$app_root\dev\bat\do_GTIFF_single.bat]

* EXAMPLE -4- (default mode, multiple TIF files in a dir)

[$app_root/dev/sh/do_GTIFF_folder.sh]
[$app_root\dev\sh\do_GTIFF_folder.bat]

* EXAMPLE -5- (default mode, to run directly the python code)

run directly in a python environent the 'main*.py' code, after having modified rows 12, 17 and 21  <br>
These 3 rows allows to select the type of data format (asc vs gtiff) and the gridded data filenames.  <br>

## Input description

(0)Put grids folder in $app_root/data/bottom_up_emissions/  <br>
(1)Each file must contain one and only one data grid/matrix (Single year / Single pollutant / Single sector)  <br>
(2)Format: ASC / GEOTIFF accepted <br>
(3)FileName: Each file must follow  a name convention like this: <br>
InventoryName_IstitutionName_CountryCode_Pollutant_GNFR_ID_epsgXXXXX_year_desc.extension <br>
#Valid file example <br>

#THESE ARE ONLY TEST FILES, don't look at the name itself. <br>
--> CHMI_RIMM_CZ_NO2_ALL_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc <-- <br>
Splitting we have: <br>
--> CHMI RIMM CZ NO2 ALL EPSG28403 2017 MAP-FILE2019-09-16b6fc2e-816.asc <-- <br>
(4) Valid Pollutant = [NO2, SO2, PM2.5, PM_coarse, PM10, VOC, NH3] <br>
(5) Valid GNFR = [GA, GB, GC, GD, GE, GF, GI, GJ, GK, GM] <br>

**ENV DATA**

Check the existence of the following subfolders:
$app_root/polygons
_NUTS_RG_01M_2021_4326
_URAU_RG_100K_2020_4326_FUA
_URAU_RG_100K_2021_4326_FUA
-->Don't remove or change them<--


## Help


Any advise for common problems or issues will be added here.
```
   
```

## Authors

Contributors names and contact info

(c) JRC 2023

## Version History

* (beta) 2023.04.17 beta test release
&nbsp;&nbsp;&nbsp;&nbsp;* Single grid approach
&nbsp;&nbsp;&nbsp;&nbsp;* Dask approach
&nbsp;&nbsp;&nbsp;&nbsp;* Polygons id/decoding as parameter
* ()
    * ()

## License

See the LICENSE.txt file for details

## Acknowledgments

For name of the files and other data specifications, you can also refer to the documents at https://aqm.jrc.ec.europa.eu/ecmaps/.
