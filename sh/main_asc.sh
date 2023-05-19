
#put_here_your_inst_folder
code_root="/storage/mariomi/Shared_PyProj/FAIRMODE-compute_emissions_by_polygon/"
app_root="/eos/jeodpp/data/projects/FAIRMODE/"

#put_here_your_bin_from_conda (or activate properly the right conda env)
py_exec=/storage/mariomi/conda/fm_3_10/bin/python3.10
#put_here_main_py (leave as is)
py_code=$code_root/py/main_asc.py

#test setting, change only after the first working run, if you need it
#data_root=$app_root

echo $py_exec $py_code
$py_exec $py_code $app_root