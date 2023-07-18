@echo off 
REM put_here_your_inst_folder
SET root_path=E:\dev\FAIRMODE\

REM put_here_your_bin_from_conda (or activate properly the right conda env)
SET py_exec=C:\Dev\conda\fm_3_10\bin\python3.10
REM put_here_your_main_py
SET py_code=E:\dev\FAIRMODE\dev\py\compute_emissions.py

REM shared info
SET workers=8

REM test setting, change only after the first working run, if you need it
SET data_sub_path=data\
SET model_sub_path=asc\
SET grid_type=ASC
SET grid_sub_path=bottom_up_emissions\
SET grid_sel=%root_path%%data_sub_path%
SET grid_sel=%grid_sel%%grid_sub_path%
SET grid_sel=%grid_sel%%model_sub_path%
REM if input measure unit --> Tg yr-1, otherwise change accordingly to your input measure unit
REM requested final measure unit is kTons, put here the conversion factor (multiply by...)
SET to_kton=1000

SET fname=CHMI_RIMM_CZ_NO2_ALL_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc
SET fgrid=%grid_sel%%fname%
REM %conda% activate

echo %py_exec% %py_code% %root_path% %fgrid% %grid_type% %to_kton% %workers%
%py_exec% %py_code% %root_path% %fgrid% %grid_type% %to_kton% %workers%

REM %conda% deactivate
