import os


def build_merge(app_root):
    full_res_path = os.path.join(app_root, 'data')
    full_res_path = os.path.join(full_res_path, 'output')
    full_res_path = os.path.join(full_res_path, 'merge')
    #Add a separator
    #full_res_path = os.path.join(full_res_path, res_path+'_')
    return full_res_path

def build_out(app_root):
    full_res_path = os.path.join(app_root, 'data')
    full_res_path = os.path.join(full_res_path, 'output')
    full_res_path = os.path.join(full_res_path, 'zs')
    #Add a separator
    #full_res_path = os.path.join(full_res_path, res_path+'_')
    return full_res_path


def get_filter_condition():
    filter_condition = []
    #admin_file.append('NUTS_RG_01M_2021_4326')
    filter_condition.append('')
    #admin_file.append('URAU_RG_100K_2020_4326_FUA')
    filter_condition.append('')
    # admin_file.append('URAU_RG_100K_2020_4326_FUA')
    #filter_condition.append('CNTR_CODE == UK')
    #admin_file.append('URAU_RG_100K_2021_4326_FUA')
    #filter_condition.append('CNTR_CODE != UK')
    # admin_file.append('URAU_RG_100K_2020_4326_CITIES')
    # admin_file.append('URAU_RG_100K_2021_4326_CITIES')
    return filter_condition


def get_admin_id_class():
    admin_id_class = []
    admin_id_class.append('NUTS2016')
    admin_id_class.append('FUA2020')
    #admin_id_class.append('FUA-EU')
    #admin_id_class.append('FUA-UK')
    #admin_id_class.append('FUA-EU')
    return admin_id_class


def get_admin_file():

    admin_file = []
    admin_file.append('NUTS_RG_01M_2016_4326')
    admin_file.append('URAU_RG_100K_2020_4326_FUA')
    #admin_file.append('URAU_RG_100K_2021_4326_FUA')
    # admin_file.append('URAU_RG_100K_2020_4326_CITIES')
    # admin_file.append('URAU_RG_100K_2021_4326_CITIES')
    return admin_file


def get_admin_col():

    #admin_col=["LEVL_CODE","URAU_CATG","URAU_CATG", "URAU_CATG", "URAU_CATG"]
    #admin_col=["LEVL_CODE","URAU_CATG","URAU_CATG"]
    admin_col=["LEVL_CODE","URAU_CATG"]

    return admin_col


def get_res_path():

    res_path = []
    res_path.append('2016_NUTSLV3')
    res_path.append('2020_FUA')
    #res_path.append('2021_FUA')
    return res_path

def get_admin_id():

    # admin_id=["NUTS_ID","URAU_CODE","URAU_CODE","URAU_CODE","URAU_CODE"]
    #admin_id=["NUTS_ID","URAU_CODE","URAU_CODE"]
    admin_id = ["NUTS_ID", "URAU_CODE"]
    return admin_id


def get_admin_val():

    # admin_val=["3","F","F","C","C"]
    #admin_val=["3","F","F"]
    admin_val = ["3", "F"]
    return admin_val


def get_valid_poll():

    poll_codes = ['NOX', 'SO2', 'PM2.5', 'PM10', 'NMVOC', 'NH3']
    poll_names = ['sox', 'pm10', 'pm2_5', 'nox', 'nmvoc', 'nh3']
    return poll_codes


def get_valid_sectors():

    sector_codes =  ['GNFRF', 'GNFRC', 'GNFRKL', 'GNFRAB', 'GNFRG', 'GNFRE', 'GNFRD', 'GNFRHI', 'GNFRJ']
    sector_desc = ['Traffic', 'Commercial and residential' , 'Agriculture', 'Industry',
                   'Shipping', 'Solvents', 'Fugitive', 'Off-road', 'Waste']
    sector_mixed_codes = ['GNFR F', 'GNFR C', 'GNFR K + L', 'GNFR A + B', 'GNFR G', 'GNFR E', 'GNFR D', 'GNFR H + I', 'GNFR J']

    return sector_codes, sector_desc, sector_mixed_codes
