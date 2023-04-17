
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
model_sub_path="asc/"
grid_type=ASC
grid_sub_path="bottom_up_emissions/"
grid_sel=$app_root$grid_sel
grid_sel=$grid_sel$grid_sub_path
grid_sel=$grid_sel$model_sub_path
#input measure unit --> Tg yr-1
to_kton=1000

fname=CHMI_RIMM_CZ_NO2_ALL_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc
fgrid=$grid_sel$fname

echo $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
$py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
