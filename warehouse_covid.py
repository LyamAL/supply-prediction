import geopandas
import pandas
import datetime

from folium import folium

import util
from matplotlib import pyplot as plt

if __name__ == '__main__':
    covid_df = pandas.read_csv('covid_with_gps.csv', engine='python', skip_blank_lines=True)
    site_df = pandas.read_csv('F:\myStuff\数据\疫情场景数据\site_df_with_covid_info_v2.csv', engine='python', skip_blank_lines=True)
    # 4.15 - 5.17 疫情和营业部/仓对上 point in polygon
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    # site_df.sort_values(ascending=True, inplace=True, by=['county_name'])
    # site_df.index = site_df['site_code']
    districts = list(site_df['county_name'].unique())

    # 创建一个新的地图底图，用于地理散点图
    map = folium.Map(location=[31.38383, 121.25309], zoom_start=13)

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        # 获得疫情数据
        site_df_daily = site_df[['site_code', 'node_name', 'county_name', 'town_name', 'address', 'lng', 'lat', 'fence',
                                 cur_date.strftime("%m-%d")]]
        # 画fence，画point
        for index, row in site_df_daily.iterrows():
            polygon = row['fence']
        cur_date += datetime.timedelta(days=1)
    site_df.to_csv('site_df_with_covid_info.csv', index=False)
    exit(0)
    # covid_df['dt'] = covid_df['dt'].apply(lambda x: x.strftime("%m-%d"))
    # print(covid_df['dt'].unique())
