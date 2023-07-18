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
SET filter="*.asc"
REM if input measure unit --> Tg yr-1, otherwise change accordingly to your input measure unit
REM requested final measure unit is kTons, put here the conversion factor (multiply by...)
SET to_kton=1000

cd %grid_sel%
REM %conda% activate

for /f tokens^=* %%i in ('where .:*.asc')do (
	REM echo/ Path: %%~dpi ^| Name: %%~nxi
	SET fgrid=%%~dpi%%~nxi
	echo %py_exec%
	echo %py_code%
	REM notepad %%~dpi%%~nxi
	echo %root_path%
	echo %%~dpi%%~nxi
	echo %grid_type%
	echo %to_kton%
	echo %workers%
	%py_exec% %py_code% %root_path% %%~dpi%%~nxi %grid_type% %to_kton% %workers%
)

REM %conda% deactivate
