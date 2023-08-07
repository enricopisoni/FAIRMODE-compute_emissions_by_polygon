import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import dask
import geopandas as gpd
import numpy as np
import os
import pandas as pd
import sys
import warnings
import xarray as xr
import xrspatial
from dask import delayed
from dask.distributed import Client, LocalCluster
from geocube.api.core import make_geocube
from pyproj import CRS
from shapely.geometry import box
from time import time

import fairmode_parameters
from fairmode_parameters import build_out as build_out


#from multiprocessing import Pool

# TODO: if the grid is huge there would be the necessity to limit the extent
# TODO: Consider this https://stackoverflow.com/questions/14697442/faster-way-of-polygon-intersection-with-shapely
# Done: remove extra columns (as described in readme file)
# Done: force specific pollutant name and GNFR (look at the readme)
# Done: display a warning if some combination of polluttant/sector is missing, after this check do the following
# Done: ... as final option: merge global csv in a single file
#res_path.append('2020_CTS')
#res_path.append('2021_CTS')


def run_manually(app_root, grid, out, grid_type, to_tons_factor):

    workers_no = 2
    cluster = LocalCluster(n_workers=workers_no)
    client = Client(cluster)

    print(client.dashboard_link)
    admin_file = fairmode_parameters.get_admin_file()
    admin_col =  fairmode_parameters.get_admin_col()
    admin_val = fairmode_parameters.get_admin_val()
    admin_id = fairmode_parameters.get_admin_id()
    filter_condition = fairmode_parameters.get_filter_condition()
    admin_class = fairmode_parameters.get_admin_id_class()

    for i, admin in enumerate(admin_file):

        #build zone full file
        print(admin)

        zones = build_zones(app_root, admin)
        print('build_zones(admin)', zones)
        print('build_out(res_path[i])', out)
        print('admin_col[i]', admin_col[i])
        print('admin_val[i]', admin_val[i])
        print('admin_type_col[i]', admin_id[i])
        print('filter_condition[i]', filter_condition[i])
        print('admin_class[i]', admin_class[i])

        main(zones, grid, client, out, grid_type=grid_type,
             admin_type_col=admin_col[i], admin_type_val=admin_val[i], admin_id=admin_id[i],
             filter_condition=filter_condition[i], admin_class=admin_class[i], to_tons_factor=to_tons_factor)

    #sys.exit(0)
    print('...main finished')
    print("DASK client shutdown")
    client.shutdown()

def build_zones(app_root,admin_file):
    zones = os.path.join(app_root, 'data')
    zones = os.path.join(zones, 'polygons')
    zones = os.path.join(zones, admin_file)
    zones = os.path.join(zones, admin_file+'.shp')
    return zones


def __bbox_creator(coords):
    '''
    :param coords:
    :return:
    '''
    return box(*coords)


def __pixel2poly_power(lat: np.array, lon: np.array, hlf_res: float) -> list:
    """Convert tuples of coordinates to a list of polygons

    Convert a list of coordinates, usually from a raster where pixels is a point,
    into a series of polygons organized in a geopandas GeoDataFrame


    :param lat:  Array of values from a raster where pixel is a point
    :param lon: Array of values from a raster where pixel is a point
    :param hlf_res: half-pixel resolution
    :return list: A list of shapely polygons
    """

    import dask.bag as db

    lon_min = (lon.round(3) - hlf_res).round(2)
    lat_min = (lat.round(3) - hlf_res).round(2)
    lat_max = (lat.round(3) + hlf_res).round(2)
    lon_max = (lon.round(3) + hlf_res).round(2)
    start = time()
    bbox = [[lon_min[i], lat_min[j], lon_max[i], lat_max[j]] for j, yj in enumerate(lat) for i, xi in enumerate(lon)]

    b = db.from_sequence(bbox, npartitions=8)
    b1 = b.map(__bbox_creator)
    #print('start compute bag')
    polygons = b1.compute()
    #print('end compute bag')
    #print(f'Duration of parallel processing (Dask): {time() - start:.2f} secs')
    return polygons


def __pixel2poly(lat: np.array, lon: np.array, hlf_res: float) -> list:
    """Convert tuples of coordinates to a list of polygons

    Convert a list of coordinates, usually from a raster where pixels is a point,
    into a series of polygons organized in a geopandas GeoDataFrame


    :param lat:  Array of values from a raster where pixel is a point
    :param lon: Array of values from a raster where pixel is a point
    :param hlf_res: half-pixel resolution
    :return list: A list of shapely polygons
    """

    lon_min = (lon.round(3) - hlf_res).round(2)
    lat_min = (lat.round(3) - hlf_res).round(2)
    lat_max = (lat.round(3) + hlf_res).round(2)
    lon_max = (lon.round(3) + hlf_res).round(2)

    polygons = []

    #print(lat.shape[0], lon.shape[0], lon.shape[0]*lat.shape[0])
    start = time()
    for j, yj in enumerate(lat):
        for i, xi in enumerate(lon):
            polygons.append(box(lon_min[i], lat_min[j], lon_max[i], lat_max[j]))
    #print(f'Duration of sequential processing: {time() - start:.2f} secs')

    return polygons


def do_CAMS(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor):

    # convert polygons to raster
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    # adapt to be compatible with the original grid
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )

    # apply the weights
    masked = xds * amm_mask_grid.perc * to_tons_factor
    stats = pd.DataFrame()

    # compute statistic for each sector
    for t in range(masked.time.shape[0]):
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        tds = masked.isel(time=t)
        yr = int(tds.time.dt.year.values)
        for sector in list(tds.keys()):
            if sector == "Latitude-Longitude":
                continue
            # ToDo 20230712: fix bug when a multipolygon create more than one
            # ToDo 20230712: value for a single admin (sum together and keep only one row in the dataframe)
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(sector), stats_funcs=["sum"]
                )["sum"].values,
                11,
            )
            # original version (sector as column)
            # spec_gdf[sector] = np.round(val, 4)
            # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            # sector as key version
            spec_gdf[['POLLUTANT', 'YEAR', 'GNF_SECTOR', 'EMIS(kTons)']] = pollutant, int(yr), sector, np.round(val, 11)
            stats = pd.concat([stats, spec_gdf], axis=0)
        # move this inside the cycle
        # stats = pd.concat([stats, spec_gdf], axis=0)

    return stats


def do_GTIFF(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id):

    # convert polygons to raster
    print('Start GTIFF (single admin/poly)')
    #print('set spatial dims...')
    xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    #print('... set spatial dims done ')

    #print('make_geocube')
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    #print('... make_geocube done')
    # adapt to be compatible with the original grid
    #print('rename')
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )
    #print('... rename done')

    # apply the weights
    #print('masked')
    masked = xds * amm_mask_grid.perc * to_tons_factor
    stats = pd.DataFrame()
    #print('... masked done')

    # compute statistic for each sector
    #print('year')
    #print(year)
    spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
    tds = masked
    #print('tds-->', tds)
    #yr = int(tds.time.dt.year.values)
    for dataset in list(tds.keys()):
        #print('sector')
        #print(sector)
        #print('amm_mask_grid.IUID.shape, tds.get(sector).shape')
        #print(amm_mask_grid.IUID.shape, tds.get(sector).shape)
        if dataset == "Latitude-Longitude":
            continue
        try:
            # 20230721: fix bug when a multipolygon create more than one
            # MM 20230721: value for a single admin (sum together and keep only one row in the dataframe)
            # ToDo: put this aggregation in a atomic function and call it when necessary (parameters = stats_func?))
            #print('dataset-->', dataset)
            #print('vals-->')
            vals = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(dataset).squeeze(), stats_funcs=["sum"]
                )["sum"].values,
                11,
            )
            agg_val = -1.

            for test_val in vals:
                agg_val=agg_val+test_val
                print('val...done')
                #val_test = pd.DataFrame(val).fillna(0).values.astype(np.int32)
                #val_test = np.asarray(val, dtype=object)
                # original version (sector as column)
                # spec_gdf[sector] = np.round(val, 4)
                # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
                # sector as key version
                #val_test = print(pd.DataFrame(val).values.astype(np.double))
                print('***intersection***')
                print('pollutant, int(year), sect_id, test_val')
                print(pollutant, int(year), sect_id, test_val)
                print('*-->intersection<--*')

            if agg_val > 0.:
                spec_gdf[['POLLUTANT', 'YEAR', 'GNF_SECTOR', 'EMIS(kTons)']] = pollutant, int(year), sect_id, agg_val
                stats = pd.concat([stats, spec_gdf], axis=0)
                # print('... sector done')
                print(dataset, '... single admin/poly done-->', stats)
        except Exception as e:
            print('Exception in do_GTIFF')
            print(e, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print('--->Exception in do_GTIFF<---')
            #continue
        '''
        except ValueError:
            print('admin outside, discard')
        '''

    # move this inside the cycle
    # stats = pd.concat([stats, spec_gdf], axis=0)
    # print('******')

    return stats


def do_ASC(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id):

    # convert polygons to raster
    print('Start ASC')
    #print('set spatial dims...')
    xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    #print('... set spatial dims done ')

    #print('make_geocube')
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    #print('... make_geocube done')
    # adapt to be compatible with the original grid
    #print('rename')
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )
    #print('... rename done')

    # apply the weights
    #print('masked')
    masked = xds * amm_mask_grid.perc * to_tons_factor
    stats = pd.DataFrame()
    #print('... masked done')

    # compute statistic for each sector
    #print('year')
    #print(year)
    spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
    tds = masked
    #yr = int(tds.time.dt.year.values)
    for dataset in list(tds.keys()):
        #print('sector')
        #print(sector)
        #print('amm_mask_grid.IUID.shape, tds.get(sector).shape')
        #print(amm_mask_grid.IUID.shape, tds.get(sector).shape)
        if dataset == "Latitude-Longitude":
            continue
        try:
            # ToDo 20230712: fix bug when a multipolygon create more than one
            # ToDo 20230712: value for a single admin (sum together and keep only one row in the dataframe)
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(dataset).squeeze(), stats_funcs=["sum"]
                )["sum"].values,
                11,
            )
            # original version (sector as column)
            # spec_gdf[sector] = np.round(val, 4)
            # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            # sector as key version
            spec_gdf[['POLLUTANT', 'YEAR', 'GNF_SECTOR', 'EMIS(kTons)']] = pollutant, int(year), sect_id, np.round(val, 11)
            stats = pd.concat([stats, spec_gdf], axis=0)
            # print('... sector done')
            print(dataset, '... single admin done-->', stats)
        except ValueError:
            print('admin outside, discard')

    # move this inside the cycle
    # stats = pd.concat([stats, spec_gdf], axis=0)
    # print('******')

    return stats


def do_EMEP(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor):

    print('Start EMEP')
    xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    # convert polygons to raster
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    # adapt to be compatible with the original grid
    #amm_mask_grid.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)

    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.y, "lon": xds.y}
    )

    # apply the weights
    masked = xds * amm_mask_grid.perc * to_tons_factor
    stats = pd.DataFrame()

    # compute statistic for each sector
    for t in range(masked.time.shape[0]):
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        tds = masked.isel(time=t)
        yr = int(tds.time.dt.year.values)
        for sector in list(tds.keys()):
            if sector == "Latitude-Longitude":
                continue
            # ToDo 20230712: fix bug when a multipolygon create more than one
            # ToDo 20230712: value for a single admin (sum together and keep only one row in the dataframe)
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(sector), stats_funcs=["sum"]
                )["sum"].values,
                4,
            )
            # original version (sector as column)
            # spec_gdf[sector] = np.round(val, 4)
            # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            # sector as key version
            spec_gdf[['POLLUTANT', 'YEAR', 'GNF_SECTOR', 'EMIS(kTons)']] = pollutant, int(yr), sector, np.round(val, 4)
            stats = pd.concat([stats, spec_gdf], axis=0)
        # move this inside the cycle
        # stats = pd.concat([stats, spec_gdf], axis=0)

    return stats


def do_EMEP_split(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor):

    print('Start EMEP (split)')

    xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    sectors_names=['A_PublicPower', 'B_Industry','C_OtherStationaryComb','D_Fugitives','E_Solvents','F_RoadTransport',
    'G_Shipping','H_Aviation','I_OffRoad','J_Waste','K_AgriLivestock','L_AgriOther','M_Other','SumAllSectors']
    sectors_codes=['publicpower', 'industry', 'otherstationarycomb', 'fugitive', 'solvents', 'roadtransport',
                   'shipping', 'aviation', 'offroad', 'waste', 'agrilivestock', 'agriother', 'other', 'sumallsectors']

    poll_codes=['SOx', 'PM10','PM2_5','NOx','NMVOC','NH3']
    poll_names=['sox', 'pm10','pm2_5','nox','nmvoc','nh3']

    source_lon=xds.lon.values
    source_lat=xds.lat.values

    years=xds['time']
    #print('********')
    #print(years)
    #print('********')
    yy=range(len(list(years)))
    stats = pd.DataFrame()

    for year in yy:
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        #print('---->', year, '<---')
        for sect_idx in enumerate(sectors_codes):
            sect=sectors_codes[sect_idx[0]]
            sect_name=sectors_names[sect_idx[0]]
            '''
            if os.path.exists(full_name):
                print('Still there, skip')
                continue
            '''
            # Use the resample method to interpolate the data to the new grid
            '''
            xds_selected = xds[sect].isel(time=year)
            #temp.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
            #print(temp, 'temp')
            # try to workaround error
            try:
                #temp.data=temp.data/(geozoom*geozoom)
                xds_resampled = temp.interp(lat=source_lat, lon=source_lon, method='nearest')
            except:
                temp.load()
                #temp.data=temp.data/(geozoom*geozoom)
                xds_resampled = temp.interp(lat=source_lat, lon=source_lon, method='nearest')
            temp = None
            #print('xds_resampled', xds_resampled)
            '''
            xds_selected = xds[sect].isel(time=year)
            #print('---->', sect, '<---')
            xds_selected.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
            #print('try geocube...')
            amm_mask_grid = make_geocube(
                vector_data=AOI_wgs,
                measurements=["perc", "IUID"],
                like=xds_selected,
            )
            #print('... done')
            # adapt to be compatible with the original grid
            amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
                {"lat": xds.lat, "lon": xds.lon}
            )
            single_grid = xds_selected * amm_mask_grid.perc * to_tons_factor
            # ToDo 20230712: fix bug when a multipolygon create more than one
            # ToDo 20230712: value for a single admin (sum together and keep only one row in the dataframe)
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, single_grid, stats_funcs=["sum"]
                )["sum"].values,
                11,
            )
            # original version (sector as column)
            # spec_gdf[sector] = np.round(val, 4)
            # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            # sector as key version
            spec_gdf[['POLLUTANT', 'YEAR', 'GNF_SECTOR', 'EMIS(kTons)']] = pollutant, int(year), sect_name, np.round(val, 11)
            #if val > 0.00001:
            #    print(year, sect, val)
            stats = pd.concat([stats, spec_gdf], axis=0)
            #print('...year/sector processed')

    '''
    # convert polygons to raster
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    # adapt to be compatible with the original grid
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )

    # apply the weights
    masked = xds * amm_mask_grid.perc
    stats = pd.DataFrame()

    # compute statistic for each sector
    for t in range(masked.time.shape[0]):
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        tds = masked.isel(time=t)
        yr = int(tds.time.dt.year.values)
        for sector in list(tds.keys()):
            if sector == "Latitude-Longitude":
                continue
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(sector), stats_funcs=["sum"]
                )["sum"].values,
                4,
            )
            # original version (sector as column)
            # spec_gdf[sector] = np.round(val, 4)
            # spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            # sector as key version
            spec_gdf[['pollutant', 'year', 'sector', 'emis']] = pollutant, int(yr), sector, np.round(val, 4)
            stats = pd.concat([stats, spec_gdf], axis=0)
        # move this inside the cycle
        # stats = pd.concat([stats, spec_gdf], axis=0)
    '''
    #print('...admin processed')
    return stats



def __setreproj(dataset: xr.Dataset, crs: int = 4326):
    """Assigne a specific CRS to a Xarray dataset

    :param dataset: Dataset to be reprojected
    :param crs: Destination CRS, (default value: 4326)
    :return: Xarray Dataset with CRS reference
    """
    return dataset.rio.write_crs(CRS.from_user_input(crs).to_string(), inplace=True)


def __half_res(start_coord: float, end_coord: float) -> float:
    """Return half of the pixel resolution computed through the coordinates

    :param start_coord: Coordinate with the smaller value
    :param end_coord: Coordinate with the bigger value
    :return: return half of pixel resoltion
    """
    return np.around((end_coord - start_coord) / 2, 4).data


@delayed
def __statistics(
    local_region: gpd.geodataframe,
    cells: gpd.geodataframe,
    xds: ...,
    spec_admin_aoi: ...,
    geo_crs: int,
    pollutant: str,
    grid_type: str,
    to_tons_factor: float,
    year = None,
    sect_id = None,
) -> gpd.GeoDataFrame:

    """Compute statistics

    Compute statistics on a specific region of interest within a larger geospatial area.

    :param local_region:  A GeoDataFrame containing the specific region of interest.
    :param cells: A GeoDataFrame containing the original cells that intersect the region of interest.
    :param xds: A dataset containing the data to be analyzed.
    :param spec_admin_aoi: A dataset containing administrative information about the region of interest.
    :param geo_crs: The reference system used in the GeoDataFrame.
    :param pollutant: The pollutant being analyzed.
    :param grid_type: The type of input grid.
    :param to_tons_factor: conversion factor to kton.
    :param year: single year being analyzed (bottom up).
    :param sect_id: single sector being analyzed (bottom up).
    :return: A GeoDataFrame containing statistics for each sector within the region of interest.
    """

    # Extract the unique identifier for the local area
    IUID = local_region["IUID"].unique()[0]

    # Explode central polygon and clean it up for silvers
    central_poly = local_region.loc[local_region["OID"].isnull()].explode(
        index_parts=True
    )
    central_poly["area"] = central_poly.geometry.area
    valid_central = (
        central_poly.loc[central_poly["area"] > 1]
        .reset_index(level=1)
        .drop(["level_1"], axis=1)
    )

    # Extract original cells that intersect the local area of interest (cookie cutted)
    merged = cells.merge(local_region, on="OID")
    merged = merged.rename({"geometry_x": "geometry"}, axis=1)
    concat = pd.concat([merged, valid_central], ignore_index=True).drop(
        ["geometry_y"], axis=1
    )
    concat = concat.drop("OID", axis=1)
    AOI_pixels = gpd.GeoDataFrame(concat, crs=local_region.crs)

    # convert local polygons to the original reference system
    AOI_wgs = AOI_pixels.to_crs(geo_crs)
    if grid_type == 'CAMS':
        return do_CAMS(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor)
    elif grid_type == 'EMEP':
        return do_EMEP_split(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor)
    elif grid_type == 'ASC':
        return do_ASC(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id)
    elif grid_type == 'GTIFF':
        return do_GTIFF(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id)
    '''
    # convert polygons to raster
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    # adapt to be compatible with the original grid
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )

    # apply the weights
    masked = xds * amm_mask_grid.perc
    stats = pd.DataFrame()

    # compute statistic for each sector
    for t in range(masked.time.shape[0]):
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        tds = masked.isel(time=t)
        yr = int(tds.time.dt.year.values)
        for sector in list(tds.keys()):
            if sector == "Latitude-Longitude":
                continue
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(sector), stats_funcs=["sum"]
                )["sum"].values,
                4,
            )
            #original version (sector as column)
            #spec_gdf[sector] = np.round(val, 4)
            #spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            #sector as key version
            spec_gdf[['pollutant', 'year', 'sector', 'emis']] = pollutant, int(yr), sector, np.round(val, 4)
            stats = pd.concat([stats, spec_gdf], axis=0)
        # move this inside the cycle
        # stats = pd.concat([stats, spec_gdf], axis=0)

    return stats
    '''


def __seq_statistics(
    local_region: gpd.geodataframe,
    cells: gpd.geodataframe,
    xds: ...,
    spec_admin_aoi: ...,
    geo_crs: int,
    pollutant: str,
    grid_type: str,
    to_tons_factor: float,
    year = None,
    sect_id = None,
) -> gpd.GeoDataFrame:

    """Compute statistics

    Compute statistics on a specific region of interest within a larger geospatial area.

    :param local_region:  A GeoDataFrame containing the specific region of interest.
    :param cells: A GeoDataFrame containing the original cells that intersect the region of interest.
    :param xds: A dataset containing the data to be analyzed.
    :param spec_admin_aoi: A dataset containing administrative information about the region of interest.
    :param geo_crs: The reference system used in the GeoDataFrame.
    :param pollutant: The pollutant being analyzed.
    :param grid_type: The type of input grid.
    :param to_tons_factor: conversion factor to kton.
    :param year: single year being analyzed (bottom up).
    :param sect_id: single sector being analyzed (bottom up).
    :return: A GeoDataFrame containing statistics for each sector within the region of interest.
    """

    # Extract the unique identifier for the local area
    IUID = local_region["IUID"].unique()[0]

    # Explode central polygon and clean it up for silvers
    central_poly = local_region.loc[local_region["OID"].isnull()].explode(
        index_parts=True
    )
    central_poly["area"] = central_poly.geometry.area
    valid_central = (
        central_poly.loc[central_poly["area"] > 1]
        .reset_index(level=1)
        .drop(["level_1"], axis=1)
    )

    # Extract original cells that intersect the local area of interest (cookie cutted)
    merged = cells.merge(local_region, on="OID")
    merged = merged.rename({"geometry_x": "geometry"}, axis=1)
    concat = pd.concat([merged, valid_central], ignore_index=True).drop(
        ["geometry_y"], axis=1
    )
    concat = concat.drop("OID", axis=1)
    AOI_pixels = gpd.GeoDataFrame(concat, crs=local_region.crs)

    # convert local polygons to the original reference system
    AOI_wgs = AOI_pixels.to_crs(geo_crs)
    if grid_type == 'CAMS':
        return do_CAMS(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor)
    elif grid_type == 'EMEP':
        return do_EMEP_split(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor)
    elif grid_type == 'ASC':
        return do_ASC(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id)
    elif grid_type == 'GTIFF':
        return do_GTIFF(AOI_wgs, xds, spec_admin_aoi, IUID, pollutant, to_tons_factor, year, sect_id)
    '''
    # convert polygons to raster
    amm_mask_grid = make_geocube(
        vector_data=AOI_wgs,
        measurements=["perc", "IUID"],
        like=xds,
    )
    # adapt to be compatible with the original grid
    amm_mask_grid = amm_mask_grid.rename({"y": "lat", "x": "lon"}).assign_coords(
        {"lat": xds.lat, "lon": xds.lon}
    )

    # apply the weights
    masked = xds * amm_mask_grid.perc
    stats = pd.DataFrame()

    # compute statistic for each sector
    for t in range(masked.time.shape[0]):
        spec_gdf = spec_admin_aoi.loc[spec_admin_aoi["IUID"] == IUID].copy()
        tds = masked.isel(time=t)
        yr = int(tds.time.dt.year.values)
        for sector in list(tds.keys()):
            if sector == "Latitude-Longitude":
                continue
            val = np.round(
                xrspatial.zonal.stats(
                    amm_mask_grid.IUID, tds.get(sector), stats_funcs=["sum"]
                )["sum"].values,
                4,
            )
            #original version (sector as column)
            #spec_gdf[sector] = np.round(val, 4)
            #spec_gdf[["pollutant", "year"]] = pollutant, int(yr)
            #sector as key version
            spec_gdf[['pollutant', 'year', 'sector', 'emis']] = pollutant, int(yr), sector, np.round(val, 4)
            stats = pd.concat([stats, spec_gdf], axis=0)
        # move this inside the cycle
        # stats = pd.concat([stats, spec_gdf], axis=0)

    return stats
    '''


def main(
    admin_pth: str,
    selected_grid: str,
    client,
    out_folder,
    geo_crs: int = 4326,
    prj_crs: int = 8857,
    grid_type = 'generic',
    admin_type_col = "LEVL_CODE",
    admin_type_val = "3",
    admin_id = "",
    filter_condition = "",
    admin_class = "",
    to_tons_factor=1.,
    workers_no=1,
):
    """
    zones, grid, client, out, grid_type=grid_type
    This function processes data on air pollutants and administrative boundaries to compute statistics and create shapefiles.

    :param admin_pth: A string containing the path to the administrative boundaries shapefile.
    :param selected_grid:  A string containing the path to the air pollutant dataset.
    :param client:  A dask distributed client used for parallel computation.
    :param geo_crs: An integer representing the geographic coordinate reference system (CRS) of the input data (default value is 4326).
    :param prj_crs:  An integer representing the projected CRS to which the input data will be converted (default value is 8857).
    :param lvl: An integer representing the administrative level to be used for the analysis (default value is 3).
    """
    #assert lvl != 0, "Level 0 not yet implemented due to oversea territories"

    # Split filename component
    print('-->', os.path.basename(selected_grid), '<--')
    if grid_type == 'generic':
        #read external file or passed parameters
        a=0
    elif grid_type == 'CAMS':
        try:
            model, area, resolution, origin, pollutant_nm, _, _, _ = os.path.basename(
                selected_grid
            ).split("_")
        except ValueError:
            print('Try different split')
            model, area, resolution, origin, pollutant_nm1, pollutant_nm2, _, _, _ = os.path.basename(
                selected_grid).split("_")
            pollutant_nm=pollutant_nm1+pollutant_nm2
    elif grid_type == 'EMEP':
        #SOx_2021_GRID_2000_to_2019
        try:
            pollutant_nm, year_ver, _, first_year, _, last_year = os.path.basename(
                selected_grid).split("_")
        except ValueError:
            print('Try different split')
            pollutant_nm1, pollutant_nm2, year_ver, _, first_year, _, last_year = os.path.basename(
                selected_grid).split("_")
            pollutant_nm=pollutant_nm1+pollutant_nm2
        model = grid_type
        area = 'UNKNOWN'
        resolution = 'UNKNOWN'
        origin = 'UNKNOWN'
        #sys.exit(1)
    elif grid_type == 'GTIFF':
        print('GTIFF')
        #CMAP_CHIM_ESP_PM10_EPSG4326_annual-mean-2012.asc
        #CEMAP_myInventory_BEL_PM10_S7_EPSG3447_2012_raster.asc
        #CEMAP_anyName_BEL_PM10_S10_EPSG3447_2012.tif
        try:
            model, institution, country, pollutant_nm, sect_id, epsg, year, desc = os.path.basename(
                selected_grid).split("_")
        except ValueError:
            print('Try different split')
            model, institution, country, pollutant_nm, sect_id, epsg, year, desc = os.path.basename(
                selected_grid).split("_")
        area = country
        print('model, institution, country, pollutant_nm, sect_id, epsg, year, desc')
        print(model, institution, country, pollutant_nm, sect_id, epsg, year, desc)
        grid_crs = int(epsg[4:len(epsg)])
        single_file = True
        #print(grid_crs)
    elif grid_type == 'ASC':
        #SOx_2021_GRID_2000_to_2019
        print('ASC')
        #CMAP_CHIM_ESP_PM10_EPSG4326_annual-mean-2012.asc
        #CEMAP_myInventory_BEL_PM10_S7_EPSG3447_2012_raster.asc
        #CEMAP_anyName_BEL_PM10_S10_EPSG3447_2012.tif
        try:
            model, institution, country, pollutant_nm, sect_id, epsg, year, desc = os.path.basename(
                selected_grid).split("_")
        except ValueError:
            print('Try different split')
            model, institution, country, pollutant_nm, sect_id, epsg, year, desc = os.path.basename(
                selected_grid).split("_")
        area = country
        print('model, institution, country, pollutant_nm, sect_id, epsg, year, desc')
        print(model, institution, country, pollutant_nm, sect_id, epsg, year, desc)
        grid_crs = int(epsg[4:len(epsg)])
        single_file = True
        #epsg_num=epsg[4:len(epsg)]
        #from osgeo import gdal

        #ds = gdal.Open(selected_grid)
        #ds = gdal.Translate(selected_grid + 'tif', ds, outputSRS='EPSG:' + epsg_num)
        #ds = None
        print(grid_crs)

    # Check existence
    # MM: add poly/admin type in the csv filename, maintain single output folder
    if single_file:
        out_file = os.path.join(out_folder, f"{model}_{institution}_{sect_id}_{pollutant_nm}_{admin_class}.csv")
    else:
        out_file = os.path.join(out_folder, f"{model}_{resolution}_{origin}_{pollutant_nm}_{admin_class}.csv")
    #out_file = f"{out_folder}{model}_{resolution}_{origin}_{pollutant_nm}_{admin_class}.csv"
    print('out_file-->', out_file)
    #sys.exit()
    if os.path.exists(out_file):
        print('Skip, file still there or not valid admin entity \n')
        print('(if you want to replace result, delete the file manually): ', out_file)
        #print("DASK client shutdown")
        #client.shutdown()
        return 0

    # Open Data
    admin_gdf = gpd.read_file(admin_pth)
    #print('admin_gdf-->', admin_gdf)
    pollutant_xds = xr.open_dataset(selected_grid)
    #print('pollutant_xds-->', pollutant_xds)

    # assign the correct projection
    #print(pollutant_xds.rio.crs, grid_crs)
    #print('__setreproj start...')
    pollutant_xds = __setreproj(pollutant_xds, grid_crs)
    #print('__setreproj done...')

    #out_name = f'/eos/jeodpp/data/projects/FAIRMODE/data/output/pm/{model}_{resolution}_{origin}_{pollutant_nm}.csv'
    # Extract Lat/Lon Values
    #print('working...')

    #print('*****')
    #print('pollutant_xds')
    #print(pollutant_xds)
    #print('*****')
    try:
        #print('check if xarray contains lat/lon...')
        lat = pollutant_xds.lat.values
        lon = pollutant_xds.lon.values
    except AttributeError:
        #print('... xarray doesnt contains lat/lon, try rename x and y')
        pollutant_xds = pollutant_xds.rename({'x': 'lon', 'y': 'lat'})
        #print('... renamed, try again ...')
        lat = pollutant_xds.lat.values
        lon = pollutant_xds.lon.values
        #print('... done')
        #lat = pollutant_xds.y.values
        #lon = pollutant_xds.x.values
    #print('lat-->', lat)
    #print('lon-->', lon)


    #lat = pollutant_xds.lat.values
    #lon = pollutant_xds.lon.values

    # Extract half pixel resolution
    hlf_res = __half_res(lat[1], lat[0])

    # Convert pixels into polygons
    #print('__pixel2poly start...', lat.shape[0]*lon.shape[0])
    '''
    #polygons = __pixel2poly_power(lat, lon, hlf_res)
    #polygons = __pixel2poly(lat, lon, hlf_res)
    if lat.shape[0]*lon.shape[0] > 1000000:
        print('switch to power')
        polygons = __pixel2poly_power(lat, lon, hlf_res)
    else:
        print('switch to easy')
        polygons = __pixel2poly(lat, lon, hlf_res)
    '''
    polygons = __pixel2poly(lat, lon, hlf_res)
    #print('__pixel2poly done...')
    print("\r\nPixels converted into cells")
    #why 4326? is the expected from grid or source from shape?
    #grid --> polygons --> set proper epsg (grid_crs)
    cells = gpd.GeoDataFrame(
        data={"OID": range(0, len(polygons))},
        geometry=polygons,
        crs=CRS.from_user_input(grid_crs),
    )
    #print('cells.total_bounds (before to_crs)')
    #print(cells.total_bounds)
    #print('****')
    '''
    cells = gpd.GeoDataFrame(
        data={"OID": range(0, len(polygons))},
        geometry=polygons,
        crs=CRS.from_user_input(4326),
    )
    '''

    # convert into a planar and orthogonal CRS and compute the area for each cell
    # 8857, fine you choose it for specific reason
    cells = cells.to_crs(prj_crs)
    #print('cells.total_bounds (after to_crs)')
    #print(cells.total_bounds)
    #print('****')
    cells["orig_area"] = cells.geometry.area

    # select and extract the selected level of administrative boundaries
    #admin_lvl = admin_gdf[admin_gdf["LEVL_CODE"] == lvl]
    admin_lvl = admin_gdf[admin_gdf[admin_type_col] == admin_type_val]
    #print('admin_lvl.shape', admin_lvl.shape)
    #force int if query result eq 0
    if admin_lvl.shape[0] == 0:
        admin_lvl = admin_gdf[admin_gdf[admin_type_col] == int(admin_type_val)]
        #print('admin_lvl.shape', admin_lvl.shape)

    # only two (exclusive) types of filter: select-only (== condition) or exclude (!= condition) a specific value
    print('admin_lvl-->', admin_lvl)
    if filter_condition != "":
        filter_col, filter_check, filter_value = filter_condition.split(" ")
        print('filter_col, filter_check, filter_value')
        print(filter_col, filter_check, filter_value)
        if filter_check == '==':
            admin_lvl = admin_lvl[admin_lvl[filter_col] == filter_value]
            print('== -->', admin_lvl)
        elif filter_check == '!=':
            admin_lvl = admin_lvl[admin_lvl[filter_col] != filter_value]
            print('!= -->', admin_lvl)
    else:
        print('no (valid) filter specified, do nothing and get all values...')
    #print(admin_type_col, admin_type_val, len(admin_lvl))

    # limit the administrative boundaries to the extent of the grid
    
    '''
    lon_min = (lon[0] - hlf_res).round(3)
    lat_min = (lat[0] - hlf_res).round(3)
    lon_max = (lon[-1] + hlf_res).round(3)
    lat_max = (lat[-1] + hlf_res).round(3)
    admin_aoi = admin_lvl.cx[lon_min:lon_max, lat_min:lat_max]
    '''
    admin_aoi = admin_lvl

    # convert into a planar and orthogonal CRS
    #print('admin_aoi.total_bounds (before to_crs)')
    #print(admin_aoi.total_bounds)
    #print('****')
    print('prj_crs', prj_crs)
    admin_aoi = admin_aoi.to_crs(prj_crs)
    #print('admin_aoi.total_bounds (after to_crs)')
    #print(admin_aoi.total_bounds)
    #print('****')
    #sys.exit(1)

    # Creat a unique identifier with integer values
    admin_aoi["IUID"] = admin_aoi.index

    # Extract from the administrative polygons lines
    borders = gpd.GeoDataFrame(geometry=admin_aoi.geometry.boundary)

    # Search all the polygons that intersect the administrative boundaries
    print("\r\nIntersection of cells, this can take some time")
    idx1, idx2 = cells.sindex.query_bulk(
        borders.geometry, predicate="intersects", sort=True
    )
    #print('idx1, idx2', idx1, idx2)
    touched_cells = cells.iloc[np.unique(idx2)]
    #print('touched_cells.shape', touched_cells.shape)

    # union cells and admin boundary
    try:
        admin_union = touched_cells.overlay(
            admin_aoi, how="union", keep_geom_type=True, make_valid=True
        )

        print("\r\nIntersection and union completed")

        # compute the percentage in respect to the entire cell area
        admin_union["perc"] = np.round(
            (admin_union.geometry.area / admin_union["orig_area"]), 3
        )
        admin_union.loc[admin_union["OID"].isnull(), "perc"] = 1
        # MM 20230801: check info into the dataframe
        #print('***no filter***')
        #print(admin_union[admin_union['OID'] == 13567])
        #print(admin_union[admin_union['perc'] < 0.95])
        check_lost_data = admin_union.groupby(['OID']).sum()
        #print(check_lost_data[check_lost_data['OID'] == 13567])
        #print(check_lost_data)
        #print('***now filter nan***')
        #print()
        admin_union_no_nan=admin_union.dropna(subset=[admin_id])
        #print(admin_union_no_nan[admin_union_no_nan['OID'] == 13567])
        #print(admin_union_no_nan[admin_union_no_nan['perc'] < 0.95])
        check_lost_data_drop_nan = admin_union_no_nan.groupby(['OID']).sum()
        #print(check_lost_data_drop_nan)
        #z['c'] = z.apply(lambda row: 0 if row['b'] in (0, 1) else row['a'] / math.log(row['b']), axis=1)
        #admin_union_no_nan['update_perc']=1
        #admin_union_no_nan['update_perc'] = admin_union_no_nan.apply(lambda row: 0 if row['sea']  else row['a'] / math.log(row['b']), axis=1)
        #check_lost_data_drop_nan.drop['AREA_SQM', 'IUID', 'orig_area']
        for index, row in check_lost_data_drop_nan.iterrows():
            #print('cycle')
            if row.perc < 0.999:
                #print('modify -->', row.name, row.IUID, row.perc)
                check_admin=admin_union.loc[admin_union['OID'] == row.name]
                #print('**')
                #print(check_admin)
                list_not_assigned=check_admin.loc[check_admin['IUID'].isnull()]
                list_assigned=check_admin.dropna(subset=[admin_id])
                tot_lost=list_not_assigned.groupby(['OID']).sum()
                #tot_lost=list_not_assigned.groupby(['OID'], as_index=False)['perc'].sum()
                #print('***')
                for index1, row1 in tot_lost.iterrows():
                    tot_lost = row1['perc']
                    tot_admin = 1. - tot_lost
                    for index2, row2 in list_assigned.iterrows():
                        #print('admin perc', row2['URAU_CODE'], row2['perc'])  # URAU_CODE / perc
                        #print('admin perc + sea/lost % component',
                        #print(tot_lost * (row2['perc'] / tot_admin))  # URAU_CODE / perc
                        #print('admin perc + sea/lost % component', row2['perc']+tot_lost*(row2['perc']/tot_admin)) # URAU_CODE / perc
                        #print('orig-->',admin_union.loc[(admin_union["OID"] == row.name) & (admin_union["URAU_CODE"] == row2['URAU_CODE']), "perc"])
                        #print('tot_admin-->',tot_admin)
                        replace_value=row2['perc']
                        if tot_admin != 0:
                            replace_value=row2['perc'] + tot_lost * (row2['perc'] / tot_admin)
                        admin_union.loc[
                            (admin_union["OID"] == row.name) & (admin_union[admin_id] == row2[admin_id]), "perc"] = \
                            replace_value


                        #print('new-->',admin_union.loc[(admin_union["OID"] == row.name) & (admin_union[admin_id] == row2[admin_id]), "perc"])
                        #print("Testing old version: No replacements")
            else:
                print('cell full covered -->', row.name, row.IUID)#, row.perc)
            #print('****')
            #print(row['OID'], row['perc'])
        '''
        for redistr in check_lost_data_drop_nan:
            lost_perc=1-redistr
            for fix_admin_perc in admin_union_no_nan[redistr['OID']]:
                admin_union[redistr]=aa
        '''
        #print(check_lost_data_drop_nan[check_lost_data_drop_nan['OID'] == 13567])
        #print(check_lost_data[check_lost_data['perc'] < 0.95])
        #print(check_lost_data)
        #print(check_lost_data[check_lost_data['perc'] < 0.95])
        # end
        #exit()
        #print('*****')
        delayed_regions = []

        # scatter data that would too big
        cells_s = client.scatter(cells)
        pollutant_xds_s = client.scatter(pollutant_xds)

        # Loops over the UTS
        print('Build dask stuff...')
        '''
        source_lon = lon
        source_lat = lat
        x_res = (source_lon[-1] - source_lon[0]) / source_lon.shape[0]
        y_res = (source_lat[-1] - source_lat[0]) / source_lat.shape[0]
    
        new_lon = np.arange(source_lon[0], source_lon[-1], x_res)  #
        new_lat = np.arange(source_lat[0], source_lat[-1], y_res)  #
    
        print(source_lon[0], source_lon[-1])
        print(new_lon[0], new_lon[-1])
    
        print(source_lat[0], source_lat[-1])
        print(new_lat[0], new_lat[-1])
    
        print(new_lon[1] - new_lon[0], new_lat[1] - new_lat[0])
        print(x_res, y_res)
    
        print(source_lon.shape, source_lon.shape)
        print(new_lon.shape, new_lat.shape)
        '''

        do_dask = True
        if do_dask:
            for i in admin_aoi[admin_id]:
                i_admin_aoi = admin_aoi.loc[admin_aoi[admin_id] == i].copy()
                i_admin_union = admin_union.loc[admin_union[admin_id] == i]

                # TODO over a distributed platform would be better to pass only the path
                delayed_regions.append(
                    __statistics(
                        i_admin_union,
                        cells_s,
                        pollutant_xds_s,
                        i_admin_aoi,
                        geo_crs,
                        pollutant_nm,
                        grid_type,
                        to_tons_factor,
                        year = year,
                        sect_id = sect_id,
                    )
                )
            print(
                f"\r\nData are ready to be analyzed.\n "
                f"Please follow the evolution here: {client.dashboard_link}"
            )
            regions_statistics = dask.compute(*delayed_regions)
            print("... dask done")

            # Re aggregate data
            print("aggregate & clean...")
            temp = list(regions_statistics)
            for i in range(len(temp) - 1, 0, -1):
                if temp[i].empty:
                    del temp[i]
            regions_statistics = tuple(temp)
            '''
            regions_gdf = gpd.GeoDataFrame(
                pd.concat(regions_statistics), crs=regions_statistics[0].crs
            )
            '''
            regions_gdf = gpd.GeoDataFrame(
                pd.concat(regions_statistics)
            )
            print("... aggregate & clean done")
            # put everything in a single file do not split between year...
            #regions_gdf.to_file(
            #        f"/eos/jeodpp/data/projects/FAIRMODE/data/output/pm/{model}_{resolution}_{origin}_{pollutant_nm}.shp"
            #    )
        else:
            #TODO: implement without dusk (check performance if sequential...)
            for i in admin_aoi[admin_id]:
                i_admin_aoi = admin_aoi.loc[admin_aoi[admin_id] == i].copy()
                i_admin_union = admin_union.loc[admin_union[admin_id] == i]
                region_statistics = __seq_statistics(
                    i_admin_union,
                    cells_s,
                    pollutant_xds_s,
                    i_admin_aoi,
                    geo_crs,
                    pollutant_nm,
                    grid_type,
                    to_tons_factor,
                    year=year,
                    sect_id=sect_id,
                )
                #print('-->', region_statistics)
                '''
                regions_gdf = gpd.GeoDataFrame(
                    pd.concat(region_statistics), crs=region_statistics[0].crs
                )
                '''


        lighter_ver = regions_gdf.drop(columns=['geometry'])
        drop_cols = ['CITY_CPTL', 'URAU_CATG', 'AREA_SQM', 'FID', 'IUID', 'NUTS3_2021', 'URAU_CATG',
                     'LEVL_CODE', 'MOUNT_TYPE', 'URBN_TYPE', 'COAST_TYPE', 'FUA_CODE', 'CITY_KERN']

        for drop_col in drop_cols:
            try:
                lighter_ver = lighter_ver.drop(columns = [drop_col])
                print('-->', drop_col, 'dropped <--')
            except:
                print('-->', drop_col, 'skipped <--')
                continue

        print('writing...', out_file)
        lighter_ver.to_csv(
                out_file
            )
        print('... writing done')
        '''
        lighter_ver.to_csv(
                f"/eos/jeodpp/data/projects/FAIRMODE/data/output/pm/{model}_{resolution}_{origin}_{pollutant_nm}.csv"
            )
        # loops over single years and save each of them on a single shape file
        for yr in regions_gdf["year"].unique():
            yearly_stat = regions_gdf.loc[regions_gdf["year"] == yr]
            #yearly_stat.to_file(
            #    f"./Data/{model}_{resolution}_{origin}_{pollutant_nm}_{yr}.shp"
            #)
            yearly_stat.to_file(
                f"/eos/jeodpp/data/projects/FAIRMODE/data/output/pm/{model}_{resolution}_{origin}_{pollutant_nm}_{yr}.shp"
            )
            lighter_ver = yearly_stat.drop(columns = ['geometry'])
            lighter_ver.to_csv(
                f"/eos/jeodpp/data/projects/FAIRMODE/data/output/pm/{model}_{resolution}_{origin}_{pollutant_nm}_{yr}.csv"
            )
         '''
    except Exception as e:
        print(e)
        print('no intersections, skip')

    print("**Task end**")


if __name__ == "__main__":
    """ " Brief description"""

    print("Welcome to the C&P")

    workers_no = 1
    print('arg #:', len(sys.argv))
    print('arg list', sys.argv)
    run_std_mode = False
    run_adv_mode = False
    merge_mode = False

    #sys.exit(0)
    print('**check mode**')
    if len(sys.argv) == 13:
        print('run_std_mode')
        zones = sys.argv[1]
        grid = sys.argv[2]
        grid_type = sys.argv[3]
        out = sys.argv[4]
        admin_type_col = sys.argv[5]
        admin_type_val = sys.argv[6]
        admin_id = sys.argv[7]
        admin_type_val = sys.argv[8]
        admin_id = sys.argv[9]
        to_tons_factor = float(sys.argv[10])
        workers_no = int(sys.argv[11])
        run_adv_mode = True
        print('zones, grid, grid_type, out, admin_type_col, admin_type_val,to_tons_factor')
        print(zones, grid, grid_type, out,
              admin_type_col, admin_type_val, to_tons_factor)
    elif len(sys.argv) == 6:
        print('run_adv_mode')
        app_root = sys.argv[1]
        grid = sys.argv[2]
        grid_type = sys.argv[3]
        to_tons_factor = float(sys.argv[4])
        #print('app_root, grid, grid_type, to_tons_factor')
        #print(app_root, grid, grid_type, to_tons_factor)
        workers_no = int(sys.argv[5])
        run_std_mode = True
        print('app_root, grid, grid_type, to_tons_factor, workers_no')
        print(app_root, grid, grid_type, to_tons_factor, workers_no)
        #sys.exit(0)
    elif sys.argv == 3:
        print('merge_mode')
        result_path = sys.argv[1]
        merge_target_path = sys.argv[2]
        merge_mode=True
    print('-->check mode<--')

    warnings.filterwarnings("ignore", category=UserWarning)

    # Dataset paths
    # zones = r".\Data\amministrativi\NUTS_RG_01M_2021_4326.shp"
    # pollutant = r".\Data\griglia\CAMS-REG-ANT_EUR_0.1x0.1_anthro_nh3_v6.1_Ref2_v2.1.nc"

	#sh.find(".", "-iname", "*.shp")
	#grid_list=sh.find(grid_root, "-iname", "*.nc", "-type", "f")
	#print(grid_root)
	
	#print(grid_list)
	# move pollutant in the cycle...
    #pollutant = grid_list[0]
    #r".\Data\griglia\CAMS-REG-ANT_EUR_0.1x0.1_anthro_nh3_v6.1_Ref2_v2.1.nc"

    cluster = LocalCluster(
        n_workers=workers_no,
    )
    client = Client(cluster)
    print(client.dashboard_link)

    try:
        if merge_mode:
            if fairmode_parameters.check_missing_poll_sect_combination(out):
                fairmode_parameters.merge_all(out, merge_target_path)
        else:

            if run_adv_mode:
                # put here explicitly a singl input combination
                print('**running adv mode**')
                print(zones)
                print(grid)
                print(out)
                main(zones, grid, client, out, grid_type=grid_type, admin_type_col=admin_type_col,
                     admin_type_val=admin_type_val, admin_id=admin_id,
                     filter_condition=filter_condition, admin_class=admin_class, to_tons_factor=to_tons_factor)
            if run_std_mode:
                # build "standard" admin list an iterate on them
                admin_file = fairmode_parameters.get_admin_file()
                admin_col = fairmode_parameters.get_admin_col()
                admin_val = fairmode_parameters.get_admin_val()
                admin_id = fairmode_parameters.get_admin_id()
                filter_condition = fairmode_parameters.get_filter_condition()
                admin_class = fairmode_parameters.get_admin_id_class()

                print(admin_file)

                for i, admin in enumerate(admin_file):
                    #build zone full file
                    print(admin)
                    zones = build_zones(app_root, admin)
                    out = build_out(app_root)
                    print('build_zones(admin)', zones)
                    print('out-->', out)
                    print('admin_col[i]', admin_col[i])
                    print('admin_val[i]', admin_val[i])
                    print('admin_id[i]', admin_id[i])
                    print('filter_condition[i]', filter_condition[i])
                    print('admin_class[i]', admin_class[i])
                    main(zones, grid, client, out, grid_type=grid_type,
                         admin_type_col=admin_col[i], admin_type_val=admin_val[i], admin_id=admin_id[i],
                         filter_condition=filter_condition[i], admin_class=admin_class[i],
                         to_tons_factor=to_tons_factor)
                #sys.exit(0)
            print('...main finished')
            print("DASK client shutdown")
            client.shutdown()
            #main(zones, pollutant, client)
    except KeyboardInterrupt:
        print("User has interrupted the process")
        print("DASK client shutdown")
        client.shutdown()
        sys.exit(0)
