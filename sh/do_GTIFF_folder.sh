
#put_here_your_inst_folder
app_root="/storage/fairmode/"

#put_here_your_bin_from_conda (or activate properly the right conda env)
py_exec=/storage/mariomi/conda/fm_3_10/bin/python3.10
py_code=$app_root/compute_emissions.py

#shared info
workers=8

#test setting, change only after the first working run, if you need it
data_sub_path="data/"
model_sub_path="gtiff/"
grid_type=GTIFF
grid_sub_path="bottom_up_emissions/"
grid_root=$app_root$data_sub_path
grid_root=$grid_root$grid_sub_path
grid_root=$grid_root$model_sub_path
filter="*.tif"
#input measure unit --> Tg yr-1
to_kton=1000

find $grid_root -name $filter|while read fgrid; do
  echo "$fgrid"
  echo $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
  $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
done
