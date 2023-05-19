@echo off 
REM put_here_your_inst_folder
SET root_path=E:\dev\FAIRMODE\

REM put_here_your_bin_from_conda (or activate properly the right conda env)
SET py_exec=C:\Dev\conda\fm_3_10\bin\python3.10
REM put_here_your_main_py
SET py_code=E:\dev\FAIRMODE\dev\py\compute_emissions.py

REM shared info

REM test setting, change only after the first working run, if you need it
SET data_sub_path=data\
SET out_sub_path=output\
SET out_sub_path=%root_path%%data_sub_path%out_sub_path

REM Remove sectors and pollutant from file name
SET fname=AMS-MINNI_ENEA_IT_GB_EPSG32632_MAP-FILE-20210205-e45c21-913.csv
SET out_merge_csv=%out_sub_path%%fname%

REM %conda% activate

echo %py_exec% %py_code% %out_sub_path% %out_merge_csv%
%py_exec% %py_code% %out_sub_path% %out_merge_csv%

REM %conda% deactivate