import os

import compute_emissions
import post_proc

if __name__ == "__main__":
    """Snippet to execute an user defined run

    list of files (string)
    set correct app_root location
    change (if necessary) 
        to_kton=1000
        grid_type='GTIFF' (ASC/GTIFF available uppercase)
    call 
    post_proc.finalize(split_path, merge_target_folder)
    only when you fill correctly all the combinations
    """
    
    workers=2
    #app_root='D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
    app_root='/eos/jeodpp/data/projects/FAIRMODE/'
    data_sub_path='data'    
    grid_sub_path='bottom_up_emissions'
    #grid_sub_path = 'bottom_up_source'
    model_sub_path='gtiff'

    # building input full path (data grid)
    grid_sel=os.path.join(app_root, data_sub_path)
    grid_sel=os.path.join(grid_sel, grid_sub_path)   
    grid_sel=os.path.join(grid_sel, model_sub_path)

    # put someway you input here (one by one or with a smart cycle...)
    grid_sel1=os.path.join(grid_sel, 'AMS-MINNI_ENEA_IT_NOX_GNFRHI_EPSG32632_2015_MAP-FILE-20210205-e45c21-913.tif')
    grid_sel2=os.path.join(grid_sel, 'AMS-MINNI_ENEA_IT_PM10_GNFRAB_EPSG32632_2015_MAP-FILE-20210205-e45c21-916.tif')

    # building intermediate full path (data grid --> csv)
    split_path=os.path.join(app_root, 'data')
    split_path = os.path.join(split_path, 'output')
    split_path = os.path.join(split_path, 'zs')
    # building final full path
    merge_target_folder = os.path.join(split_path, 'merge')

    # set few parameters
    grid_type='GTIFF'
    # put here the proper conversion factor to KTons
    # if you have 10^6 Tons as source measure unit (in your file)
    to_kton=1000
    # if you have Tons as source measure unit (in your file)
    #to_kton=0.001
    #or put the right value that fit your case
    #to_kton=??

    # two examples...
    compute_emissions.run_manually(app_root, grid_sel1, split_path, grid_type, to_kton)
    compute_emissions.run_manually(app_root, grid_sel2, split_path, grid_type, to_kton)
    # merge together
    post_proc.finalize(split_path, merge_target_folder)
