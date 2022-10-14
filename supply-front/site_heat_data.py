import datetime

import geopandas
import pandas
import pandas as pd
from pandas_geojson import to_geojson, write_geojson


def sites_polygon():
    site_df = pd.read_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/上海营业站位置信息with合并围栏.csv',
                          engine='python',
                          skip_blank_lines=True)
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = site_df[['fence', 'site_code', 'node_name']]
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)
    site_df.to_file('sites_polygon.json', driver='GeoJSON')


def covid_heatmap():
    site_df = pd.read_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\上海营业站位置信息with合并围栏.csv', engine='python',
                          skip_blank_lines=True)
    covid_df = pd.read_csv('F:\myStuff\数据\疫情场景数据\site_control_type_04160517.csv', engine='python',
                           skip_blank_lines=True, parse_dates=['dt'])
    dt = datetime.datetime(2022, 4, 15)
    covid_df = covid_df[covid_df['dt'] == dt]
    covid_df.fillna(0, inplace=True)
    a = covid_df['lockdown_count'].sum()
    site_df['count'] = covid_df['lockdown_count'] / max(covid_df['lockdown_count'])
    site_df.fillna(0, inplace=True)
    b = site_df['count'].sum()
    geo_json = to_geojson(df=site_df, lat='lat_new', lon='lng_new',
                          properties=['site_code', 'node_name', 'count'])
    write_geojson(geo_json, filename='siteHeat.json', indent=4)


def site_info():
    site_df = pd.read_csv('/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv', engine='python',
                          skip_blank_lines=True)
    gps_df = pd.read_csv('/Users/lyam/同步空间/数据/营业站/site_revised_gps_v2.csv', engine='python',
                         skip_blank_lines=True)
    site_df = site_df[['site_code', 'node_name']]
    gps_df = gps_df[['site_code', 'lng', 'lat']]
    site_gps_df = pandas.merge(site_df, gps_df, on='site_code', how='left')

    site_gps_df.columns = ['id', 'name', 'lng', 'lat']
    geo_json = to_geojson(df=site_gps_df, lat='lat', lon='lng',
                          properties=['id', 'name'])
    write_geojson(geo_json, filename='sitesList_v2.json', indent=4)
    pass


def warehouses_info():
    warehouse_df = pd.read_csv('/Users/lyam/同步空间/数据/仓/available_warehouses_v2.csv', engine='python',
                               skip_blank_lines=True)
    warehouse_all = pd.read_csv('/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
                               skip_blank_lines=True)
    warehouse_df = pandas.merge(warehouse_df, warehouse_all, on=['delv_center_num_c', 'store_id_c'], how='left')
    warehouse_df['id'] = range(warehouse_df.shape[0])
    warehouse_df = warehouse_df[['id', 'store_name_c', 'lat', 'lng', 'storetype']]
    geo_json = to_geojson(df=warehouse_df, lat='lat', lon='lng',
                          properties=['id', 'store_name_c', 'storetype'])
    write_geojson(geo_json, filename='warehouses_info.json', indent=4)
    pass


if __name__ == '__main__':
    # sites_polygon()
    # site_info()
    warehouses_info()
