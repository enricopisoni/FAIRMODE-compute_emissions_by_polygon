# Project Title

Cookiepoly is a python code to "cut" a well (geo) defined grid onto a selected administrative shape file.

## Description

It tries to read the most common format:
GRID
	(1) netcdf (with specific a couple of specific internal organization). Useful for TOP-DOWN (but with some adaptation also fot BU)
	(2) asc (BU)
	(3) geotiff (BU)
POLYGONS
	(1) shp folder organization, with some specification about which code is the key


## Getting Started

### Dependencies

* python 3.10
* conda
* fm_3_10.yml packages needed

### Installing

* github clone
* app_root is your unzip folder
(1)Copy in an user-executable destination folder the file fm.zip (or the clone from github)
(2)Extract all the contents in a user-executable folder (app_root)
(3)-->Follow PYTHON/CONDA ENV instructions<--
(4)Create (or check the existence and the full permission) app_root/output
(5)Change/adapt the scripts
	(a)for windows they are in $app_root + /dev/bat/*.bat
	(b)for unix they are in $app_root + /dev/sh/*.sh
		_Change properly app_root
		_Change properly output

PYTHON/CONDA ENV
It is strongly reccomended to create a brand new compatible env, to do this, go to conda prompt:
Requisite:

_python 3.10
_conda installation: conda https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda

It is strongly reccomended to create a brand new compatible env, to do this, go to conda prompt:
(1)Change folder to: $app_root/dev/
(2)Type: conda env create -f fm_3_10.yml -name fm_3_10

## Executing program

### SCRIPT DESCRIPTION

* EXAMPLE -1- (default mode, single ASC file)

[/dev/sh/do_ASC_single.sh]
[/dev/bat/do_ASC_single.bat]

* EXAMPLE -2- (default mode, multiple ASC files in a dir)

[/dev/sh/do_ASC_folder.sh]
[/dev/sh/do_ASC_folder.bat]

* EXAMPLE -3- (default mode, single TIF file)

[/dev/sh/do_GTIFF_single.sh]
[/dev/bat/do_GTIFF_single.bat]

* EXAMPLE -4- (default mode, multiple TIF files in a dir)

[/dev/sh/do_GTIFF_folder.sh]
[/dev/sh/do_GTIFF_folder.bat]

* EXAMPLE -5- (default mode, to run directly the python code)

run directly in a python environent the 'main*.py' code, after having modified rows 12, 17 and 21
These 3 rows allows to select the type of data format (asc vs gtiff) and the gridded data filenames.

## Input description

(0)Test grids folder are $app_root/data/bottom_up_emissions/
(1)Each file must contain one and only one data grid/matrix (Single year / Single pollutant / Single sector)
(2) ASC / GEOTIFF accepted
(3)Each file must follow  a name convention like this:
InventoryName_IstitutionName_CountryCode_Pollutant_GNFR_ID_epsgXXXXX_year_desc.extension
#Valid file example
#THESE ARE ONLY TEST FILES, don't look at the name.
--> CHMI_RIMM_CZ_NO2_ALL_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc <--
Splitting we have:
--> CHMI RIMM CZ NO2 ALL EPSG28403 2017 MAP-FILE2019-09-16b6fc2e-816.asc <--
(4) Valid Pollutant = [NO2, SO2, PM2.5, PM_coarse, PM10, VOC, NH3]
(5) Valid GNFR = [GA, GB, GC, GD, GE, GF, GI, GJ, GK, GM]

**ENV DATA**

In the admin data you have following subfolders:
$app_root/polygons
_NUTS_RG_01M_2021_4326
_URAU_RG_100K_2020_4326_FUA
_URAU_RG_100K_2021_4326_FUA
-->Don't remove or change them<--


## Help


Any advise for common problems or issues.
```
   
```

## Authors

Contributors names and contact info

(c) JRC 2023

## Version History

* (beta) 2023.04.17 beta test release
    * Single grid approach
    * Dask approach
    * Polygons id/decoding as parameter
* ()
    * ()

## License

See the LICENSE.txt file for details

## Acknowledgments

For name of the files and other data specifications, you can also refer to the documents at https://aqm.jrc.ec.europa.eu/ecmaps/.
