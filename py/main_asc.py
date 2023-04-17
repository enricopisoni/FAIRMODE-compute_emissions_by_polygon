import compute_emissions
import os


if __name__ == "__main__":
    """ " Brief description"""
    
    workers=2
    app_root='D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
    data_sub_path='data'    
    grid_sub_path='bottom_up_emissions'
    model_sub_path='asc'

    grid_sel=os.path.join(app_root, data_sub_path)
    grid_sel=os.path.join(grid_sel, grid_sub_path)   
    grid_sel=os.path.join(grid_sel, model_sub_path)
    grid_sel=os.path.join(grid_sel, 'CHMI_RIMM_CZ_NO2_ALL_EPSG28403_2017_MAP-FILE2019-09-16b6fc2e-816.asc')
    
    out=os.path.join(app_root, 'output/')
    to_kton=1000
    grid_type='ASC'
    
    compute_emissions.run_manually(app_root, grid_sel, out, grid_type, to_kton)