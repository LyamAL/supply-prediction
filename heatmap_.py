import datetime
import re
import random
import warnings

import folium.plugins as plugins

import pandas as pd
import folium
import pandas
import geopandas
from folium.plugins import HeatMap

from pandas.core.common import SettingWithCopyWarning

control_type_color = ['red', 'yellow', 'green']

map = folium.Map(location=[31.3004, 121.294], zoom_start=10)


def random_color():
    return "#{}{}{}{}{}{}".format(*(random.choice("0123456789abcdef") for _ in range(6)))


def plotDotforDataframe(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[point.lat, point.lng],
                        radius=1, fillOpacity=0.5,
                        weight=4).add_to(map)


def plotDot(lat, lng, color):
    folium.CircleMarker(location=[lat, lng],
                        radius=1, fill_color=color, fill_opacity=0.5, color=color,
                        weight=4).add_to(map)


def getCovidColor(type):
    if type == '封控区':
        return control_type_color[0]
    if type == '管控区':
        return control_type_color[1]
    return control_type_color[2]


def countLockDown(s):
    if pandas.isna(s):
        return 0
    return len(re.findall('封', s))


if __name__ == '__main__':
    warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
    site_df = pandas.read_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_with_covid_info_v2.csv',
                              engine='python',
                              skip_blank_lines=True)
    # 4.15 - 5.17 疫情和营业部/仓对上
    # point in polygon
    # site_df = site_df.head(100)
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date

    poly_color = [random_color() for _ in range(site_df.shape[0])]
    site_df['color'] = poly_color
    data_all = list()
    for index, row in site_df.iterrows():
        fillColor = row['color']
        color = 'white'
        polyg_ = folium.GeoJson(
            row['fence'],
            style_function=lambda x, fillColor=fillColor, color=color: {
                "fillColor": fillColor,
                "color": color,
                'weight': 1.5,
                'fillOpacity': 0.1},
        )
        polyg_.add_to(map)
    while cur_date <= end_date:  # 获得疫情数据
        # map = folium.Map(location=[31.3004, 121.294], zoom_start=10)
        md = cur_date.strftime("%m-%d")
        site_df_daily = site_df[
            ['site_code', 'color', 'node_name', 'county_name', 'town_name', 'address', 'lng', 'lat', 'fence',
             md]]
        print(site_df_daily.shape[0])
        site_df_daily['lockdown_count'] = site_df_daily.apply(lambda x: countLockDown(x[md]), axis=1)
        site_df_daily['weight'] = site_df_daily['lockdown_count'] / site_df_daily['lockdown_count'].max()
        site_df_daily_notnan = site_df_daily[site_df_daily['weight'] != 0]
        data = site_df_daily_notnan[['lat', 'lng', 'weight']].values.tolist()
        data_all.append(data)
        # HeatMap(data=data, gradient=gradient, radius=25, max_zoom=10, blur=10).add_to(map)

        # map.fit_bounds(map.get_bounds(), padding=(10, 10))
        # md = cur_date.strftime("%m%d")
        # filename = str('covid_in_site_heatmap_' + md + '.html')
        # map.save(filename)
        cur_date += datetime.timedelta(days=1)

    site_df.apply(lambda x: plotDotforDataframe(x), axis=1)
    gradient = {.2: "blue", .4: "cyan", .6: "lime", .8: "yellow", 1: "red"}
    hm = plugins.HeatMapWithTime(data_all, radius=25, position='topleft', gradient=gradient, display_index=True,
                                 index=list(site_df['route_dt'].unique()))
    hm.add_to(map)

    filename = str('covid_in_site_heatmap_revised_gps.html')
    map.save(filename)
