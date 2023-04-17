import compute_emissions
import os


if __name__ == "__main__":
    """ " Brief description"""
    
    workers=2
    app_root='D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
    data_sub_path='data'    
    grid_sub_path='bottom_up_emissions'
    model_sub_path='gtiff'

    grid_sel=os.path.join(app_root, data_sub_path)
    grid_sel=os.path.join(grid_sel, grid_sub_path)   
    grid_sel=os.path.join(grid_sel, model_sub_path)
    grid_sel=os.path.join(grid_sel, 'AMS-MINNI_ENEA_IT_NOX_S2_EPSG32632_2015_MAP-FILE-20210205-e45c21-913.tif')
    
    out=os.path.join(app_root, 'output/')
    to_kton=1000
    grid_type='GTIFF'
    
    compute_emissions.run_manually(app_root, grid_sel, out, grid_type, to_kton)