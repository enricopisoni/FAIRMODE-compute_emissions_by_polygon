
#put_here_your_inst_folder
code_root="/storage/mariomi/Shared_PyProj/FAIRMODE-compute_emissions_by_polygon/"
app_root="/eos/jeodpp/data/projects/FAIRMODE/"

#put_here_your_bin_from_conda (or activate properly the right conda env)
py_exec=/storage/mariomi/conda/fm_3_10/bin/python3.10
#put_here_main_py (leave as is)
py_code=$code_root/py/compute_emissions.py

#shared info
workers=8

#test setting, change only after the first working run, if you need it
data_root=$app_root
data_sub_path="data/"
grid_sub_path="bottom_up_source/"
model_format_sub_path="gtiff/"

grid_root=$data_root$data_sub_path$grid_sub_path
grid_root=$grid_root$model_format_sub_path

filter="*.tif"
grid_type=GTIFF

#if input measure unit --> Tg yr-1, otherwise change accordingly to your input measure unit
#requested final measure unit is kTons, put here the conversion factor (multiply by...)
to_kton=1000

find $grid_root -name $filter|while read fgrid; do
  echo "$fgrid"
  echo $py_exec $py_code $app_root $fgrid $grid_type $to_kton $workers
  $py_exec $py_code $app_root $fgrid $grid_type $to_kton $workers
done
