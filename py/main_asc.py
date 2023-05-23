import os

import compute_emissions
import post_proc

if __name__ == "__main__":
    """Snippet to execute an user defined run

    list of files (string)
    set correct app_root location
    change (if necessary) 
        to_kton=1000
        grid_type='ASC' (ASC/GTIFF available uppercase)
    call 
    post_proc.finalize(split_path, merge_target_folder)
    only when you fill correctly all the combinations
    """
    
    workers=2
    #app_root='D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
    app_root='/eos/jeodpp/data/projects/FAIRMODE/'
    data_sub_path='data'
    #grid_sub_path='bottom_up_emissions'
    grid_sub_path = 'bottom_up_source'
    model_sub_path='asc'

    # building input full path (data grid)
    grid_sel=os.path.join(app_root, data_sub_path)
    grid_sel=os.path.join(grid_sel, grid_sub_path)   
    grid_sel=os.path.join(grid_sel, model_sub_path)

    # put someway you input here (one by one or with a smart cycle...)
    grid_sel1=os.path.join(grid_sel, 'CHMI_RIMM_CZ_NOX_GNFRC_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc')
    grid_sel2=os.path.join(grid_sel, 'CHMI_RIMM_CZ_PM10_GNFRAB_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-817.asc')

    # building intermediate full path (data grid --> csv)
    split_path=os.path.join(app_root, 'data')
    split_path = os.path.join(split_path, 'output')
    merge_target_folder = os.path.join(split_path, 'merge')
    split_path = os.path.join(split_path, 'zs')

    # set few parameters
    to_kton=1000
    grid_type='ASC'

    # two examples...
    compute_emissions.run_manually(app_root, grid_sel1, split_path, grid_type, to_kton)
    compute_emissions.run_manually(app_root, grid_sel2, split_path, grid_type, to_kton)
    # merge together
    post_proc.finalize(split_path, merge_target_folder)