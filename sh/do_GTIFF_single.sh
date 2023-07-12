
#put_here_your_inst_folder
app_root="/storage/fairmode/"

#put_here_your_bin_from_conda (or activate properly the right conda env)
py_exec=/storage/mariomi/conda/fm_3_10/bin/python3.10
#put_here_your_main_py
py_code=$app_root/compute_emissions.py

#shared info
workers=8

#test setting, change only after the first working run, if you need it
data_sub_path="data/"
model_sub_path="gtiff/"
grid_type=GTIFF
grid_sub_path="bottom_up_emissions/"
grid_sel=$app_root$data_sub_path
grid_sel=$grid_sel$grid_sub_path
grid_sel=$grid_sel$model_sub_path
#if input measure unit --> Tg yr-1, otherwise change accordingly to your input measure unit
#requested final measure unit is kTons, put here the conversion factor (multiply by...)
to_kton=1000

fname=AMS-MINNI_ENEA_IT_NOX_GB_EPSG32632_2015_MAP-FILE-20210205-e45c21-913.tif
fgrid=$grid_sel$fname

echo $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
$py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
