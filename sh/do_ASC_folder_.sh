py_exec=/storage/mariomi/conda/fm_3_10/bin/python3.10
#py_code=/home/mariomi/Documents/PyProjects/c5_emis/src/zonal_stat/main_mm_v2.py
#py_code=/home/mariomi/Documents/PyProjects/c5_emis/src/zonal_stat/main_mm_v4.py
py_code=/storage/mariomi/Shared_PyProj/c5_emis/src/zonal_stat/compute_emissions.py

#shared info
workers=8
root_path="/eos/jeodpp/data/projects/FAIRMODE/"
data_sub_path="data/"
model_sub_path="asc/"
grid_type=ASC
grid_sub_path="bottom_up_emissions/"
grid_root=$root_path$data_sub_path
grid_root=$grid_root$grid_sub_path
grid_root=$grid_root$model_sub_path
filter="*.asc"
#input measure unit --> Tg yr-1
to_kton=1000

find $grid_root -name $filter|while read fgrid; do
  echo "$fgrid"
  echo $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
  $py_exec $py_code $root_path $fgrid $grid_type $to_kton $workers
done
