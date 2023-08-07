# COOKIEPOLY: computing polygons' emissions starting from gridded emissions

Cookiepoly is a python code to "cut" a well (geo) defined grid onto a selected administrative shape file.
* Please read carefully instructions and Help // FAQ section specifically to set the "Conversion Unit Factor" 
* Version 1.1 solves coastal values missing during the conversion from cell to polygons (NUTS3 especially)      

## Description

It tries to read the most common format: <br>
GRID <br>
&nbsp;&nbsp;&nbsp;&nbsp;(1) netcdf. Useful for TOP-DOWN (but with some adaptation also for BU, waiting for file test) <br>
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
(5)Change/adapt the scripts <br>
&nbsp;&nbsp;&nbsp;&nbsp;(a)for windows they are in $app_root + \dev\bat\*.bat <br>
&nbsp;&nbsp;&nbsp;&nbsp;(b)for unix they are in $app_root + /dev/sh/*.sh <br>
&nbsp;&nbsp;&nbsp;&nbsp;(c)Change properly $app_root value (for the scripts related to your installation Win or Unix) <br>
&nbsp;&nbsp;&nbsp;&nbsp;(d)Change properly $py_exec value (put exactly the full path folder of your conda/bin python3_10 executable) <br>
(6)Create $app_root/output/zs folder <br>


* PYTHON/CONDA ENV

Requisite:

_python 3.10
_conda installation: conda https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda

It is strongly recommended to create a brand new compatible env. To do this, go to conda prompt. <br>
(1)Change folder to: $app_root/dev/ <br>
(2)Type: conda env create --name fm_3_10 --file=fm_3_10.yml <br>

## Executing program

* To run directly the python code: <br>

If you have some experience in a python IDE run directly there 'main_asc.py' or 'main_geotiff.py'<br>
After this test, we strongly suggest you to work on a copy of one of those "main".py and check/editing your copy. <br> 

Relevant lines to change/edit: <br>

_ from 21 to 30: input folder definition <br>
_ from 33 to 24: the gridded data filenames (input) <br>
_ from 37 to 40: output path <br>
_ 43: input type (GTIFF/ASC) <br>
_ 46: the conversion factor from your measure unit to destination <br>
  in our case we need to convert from source/input data measure unit to Ktons <br>


### SCRIPT DESCRIPTION

* EXAMPLE -1- (default mode, single ASC file)

[$app_root/dev/sh/do_ASC_single.sh] <br>
[$app_root\dev\bat\do_ASC_single.bat] <br>

* EXAMPLE -2- (default mode, multiple ASC files in a dir) <br>

[$app_root/dev/sh/do_ASC_folder.sh] <br>
[$app_root\dev\sh\do_ASC_folder.bat] <br>

* EXAMPLE -3- (default mode, single TIF file) <br>

[$app_root/dev/sh/do_GTIFF_single.sh] <br>
[$app_root\dev\bat\do_GTIFF_single.bat] <br>

* EXAMPLE -4- (default mode, multiple TIF files in a dir) <br>

[$app_root/dev/sh/do_GTIFF_folder.sh] <br>
[$app_root\dev\sh\do_GTIFF_folder.bat] <br>

## Input description

(1)Put grids folder in $app_root/data/bottom_up_emissions/  <br>
(2)Each file must contain one and only one data grid/matrix (Single year / Single pollutant / Single sector)  <br>
(3)Format: ASC / GEOTIFF accepted <br>
(4)FileName: Each file must follow  a name convention like this: <br>
InventoryName_IstitutionName_CountryCode_Pollutant_GNFR_ID_epsgXXXXX_year_desc.extension <br>
#Valid file example <br>

#THESE ARE ONLY TEST FILES, don't look at the name itself. <br>
--> CHMI_RIMM_CZ_NOX_GNFRF_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc <-- <br>
Splitting we have: <br>
--> CHMI RIMM CZ NOX GNFRF EPSG28403 2017 MAP-FILE2019-09-16b6fc2e-816.asc <-- <br>
(5) Valid Pollutant = [NOX, SO2, PM2.5, PM10, NMVOC, NH3] <br>


| Code Name | Description | Info |
|-----------|-----------|------------|
| NOX       | NOx      | ...        |
| NMVOC     | NMVOC   | ...       |
| NH3       | NH3   | ...      |
| SO2       | SO2   | ...       |
| PM2_5     | PM2.5   | ...       |
| PM10      | PM10   | ...       |

(6) Valid GNFR = [GNFRF, GGNFRC, GNFRKL, GNFRAB, GNFRG, GNFRE, GNFRD, GNFRHI, GNFRJ] <br>

Traffic (GNFR F), commercial and residential (GNFR C), agriculture (GNFR K + L), industry (GNFR A + B), shipping (GNFR G), Solvents (GNFR E), Fugitive (GNFR D), Off-road (GNFR I + H), Waste (GNFR J)

| Code Name | Description | Included Sectors |
|--------------|-----------|------------|
| GNFRF | Traffic      | GNFR F        |
| GNFRC      | Commercial and Residential   | GNFR C       |
| GNFRKL     | Agriculture   | GNFR K + L      |
| GNFRAB      | Industry   | GNFR A + B       |
| GNFRG     | Shipping   | GNFR G       |
| GNFRE     | Solvents   | GNFR E       |
| GNFRD    | Fugitive   | GNFR D       |
| GNFRHI    | Off-road   | GNFR I + H       |
| GNFRJ     | Waste   | GNFR J       |


## Output description

The output must have at least the following columns. Other fields are considered as optional information.

| NUTS_ID // FUA_ID    | CNTR_CODE   | NAME_LATN    | POLLUTANT   | YEAR  | SECTOR   | EMIS(kTons)  |

**ENV DATA**

Check the existence of the following subfolders: <br>
$app_root/polygons <br>
_URAU_RG_100K_2020_4326_FUA <br>
_NUTS_RG_01M_2016_4326 <br>
-->Don't remove or change them<--


## Help // FAQ


Any advise for common problems or issues will be added here.
<br>
```
2023.07.15 * Issue encountered with different version of numpy (partially fixed with release late July 2023)
```
```
2023.08.01 * Please fill / edit in a proper way the conversion factor as specified in "Executing program"
section and/or in the script file you're using (.sh or .bat)
```
```
2023.08.07 * Fix coastal cells "behaviour"
```

## Authors

Contributors names and contact info

(c) JRC 2023

## Version History

* (beta) 2023.04.17 beta test release <br>
&nbsp;&nbsp;&nbsp;&nbsp;* Single grid approach <br>
&nbsp;&nbsp;&nbsp;&nbsp;* Dask approach <br>
&nbsp;&nbsp;&nbsp;&nbsp;* Polygons id/decoding as parameter <br>
* (1.0) 2023.07.21 (1.0) <br>
&nbsp;&nbsp;&nbsp;&nbsp;* fixing numpy issue <br>
&nbsp;&nbsp;&nbsp;&nbsp;* fixing .bat files <br>
&nbsp;&nbsp;&nbsp;&nbsp;* improved readme.md <br>
* (1.1) 2023.08.07 (1.1) <br>
&nbsp;&nbsp;&nbsp;&nbsp;* fix coastal cells values to polygons <br>
&nbsp;&nbsp;&nbsp;&nbsp;* minors changes to readme.md <br>
* (1.2) 2023.08.09 (1.1) <br>
&nbsp;&nbsp;&nbsp;&nbsp;* env folders fixing (output moved under data, zs and merge created) <br>
&nbsp;&nbsp;&nbsp;&nbsp;* .py with wrong example sub_folders fixed <br>
&nbsp;&nbsp;&nbsp;&nbsp;* update conda and export a better detailed yml <br>
&nbsp;&nbsp;&nbsp;&nbsp;* minors changes to readme.md <br>
* () <br>
    * () <br>

## License

See the LICENSE.txt file for details

## Acknowledgments

For name of the files and other data specifications, you can also refer to the documents at https://aqm.jrc.ec.europa.eu/ecmaps/.
