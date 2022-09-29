import datetime
import re
import random
import folium.plugins as plugins

import pandas as pd
import folium
import pandas
import geopandas
from folium.plugins import HeatMap

from util import pnpoly, centroidShapely, random_points_in_polygon, countLockDown

control_type_color = ['red', 'yellow', 'green']

map = folium.Map(location=[31.3004, 121.294], zoom_start=10)


def random_color():
    return "#{}{}{}{}{}{}".format(*(random.choice("0123456789abcdef") for _ in range(6)))


def plotDot(point):
    folium.CircleMarker(location=[point.lat, point.lng],
                        radius=2, fillOpacity=1, color='green',
                        weight=4).add_to(map)


def plotPopUpDot(point):
    folium.Marker(location=[point.lat, point.lng],
                  popup=folium.Popup('<i>The center of map</i>'),
                  tooltip='Center',
                  icon=folium.DivIcon(html=point.lockdown_count,
                                      class_name="mapText"),
                  ).add_to(map)


def plotSmallDot(lat, lng, color):
    folium.CircleMarker(location=[lat, lng],
                        radius=1, fill_color=color, fill_opacity=0.5, color=color,
                        weight=4).add_to(map)


def plotBigDot(lat, lng, color):
    folium.CircleMarker(location=[lat, lng],
                        radius=2, fill_color=color, fill_opacity=0.7, color=color,
                        weight=4).add_to(map)


def getCovidColor(type):
    if type == '封控区':
        return control_type_color[0]
    if type == '管控区':
        return control_type_color[1]
    return control_type_color[2]


if __name__ == '__main__':
    site_df = pandas.read_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_covid_jd_gps_宽型md_04160517.csv',
                              engine='python',
                              skip_blank_lines=True)
    covid_df = pandas.read_csv('/Users/lyam/Documents/mystuff/idea/数据/疫情/covid_with_jd_gps.csv', engine='python',
                               skip_blank_lines=True)

    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date

    covid_df['dt'] = pandas.to_datetime(covid_df['dt'], format='%Y/%m/%d')
    covid_df = covid_df[
        ['id', 'city', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(
        ascending=True, inplace=True, by=['dt'])
    poly_color = [random_color() for _ in range(site_df.shape[0])]
    site_df['color'] = poly_color

    # 揪出错误的gps，采用中心点法或随即取点法重新定位gps
    site_df['in_poly'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)
    site_df[['lng', 'lat']] = site_df.apply(
        lambda x: (x['lng'], x['lat']) if x['in_poly'] else centroidShapely(x['fence']), axis=1, result_type='expand')
    site_df['in_poly_again'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)  # 109
    site_df[['lng', 'lat']] = site_df.apply(
        lambda x: (x['lng'], x['lat']) if x['in_poly_again'] else random_points_in_polygon(x['fence'], 1), axis=1,
        result_type='expand')
    count = site_df['in_poly_again'].value_counts().size
    times = 0

    while count > 1 and times < 20:
        times += 1
        site_df[['lng', 'lat']] = site_df.apply(
            lambda x: (x['lng'], x['lat']) if x['in_poly_again'] else random_points_in_polygon(x['fence'], 1), axis=1,
            result_type='expand')
        site_df['in_poly_again'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)
        count = site_df['in_poly_again'].value_counts().size

    site_df.drop('in_poly', axis=1, inplace=True)
    site_df.drop('in_poly_again', axis=1, inplace=True)
    # site_df.to_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_revised_gps_covid_宽型md_04160517.csv',
    #                index=False)

    # 画polygon
    while cur_date <= end_date:  # 获得疫情数据
        map = folium.Map(location=[31.3004, 121.294], zoom_start=10)
        # 画polygon
        for index, row in site_df.iterrows():
            fillColor = row['color']
            color = 'white'
            polyg_ = folium.GeoJson(
                row['fence'],
                style_function=lambda x, fillColor=fillColor, color=color: {
                    "fillColor": fillColor,
                    "color": color,
                    'weight': 1,
                    'fillOpacity': 0.3},
            )
            polyg_.add_to(map)
        # end 画polygon

        # 画 站点point
        site_df.apply(plotDot, axis=1)
        md = cur_date.strftime("%m-%d")
        site_df_daily = site_df[
            ['site_code', 'color', 'node_name', 'county_id', 'county_name', 'lng',
             'lat', 'fence',
             md]]
        site_df_daily[['lockdown_count', 'restraint_count', 'safe_count']] = site_df_daily.apply(
            lambda x: countLockDown(x[md]), axis=1,
            result_type='expand')

        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_daily = covid_df[(covid_df['dt'] >= cur_date) & (covid_df['dt'] < tomorrow)]
        covid_df_daily.index = covid_df_daily['id']

        # site_df.apply(plotDot, axis=1)
        site_df_daily.apply(plotPopUpDot, axis=1)
        for index, row in site_df_daily.iterrows():
            # data = site_df_daily[['lat', 'lng', 'lockdown_count']].values.tolist()
            # gradient = {.4: "blue", .6: "cyan", .7: "lime", .8: "yellow", 1: "red"}
            # HeatMap(data=data, gradient=gradient, radius=5, max_zoom=10).add_to(map)
            if pandas.notna(row[md]):
                # 加点
                id_regex = r'(\d{1,6})'
                control_type_regex = r'([\u4e00-\u9fa5]{3})'
                # 这些是要打的点
                ids = re.findall(id_regex, row[md])
                controls = re.findall(control_type_regex, row[md])
                covids = zip(ids, controls)

                for point in covids:
                    if point[1] == '封控区':
                        covid_lat = covid_df_daily.at[int(point[0]), 'lat']
                        covid_lng = covid_df_daily.at[int(point[0]), 'lng']
                        plotSmallDot(covid_lat, covid_lng, 'red')
        map.fit_bounds(map.get_bounds(), padding=(10, 10))
        md = cur_date.strftime("%m%d")
        filename = str('covid_in_site_scatter_revised' + md + '.html')
        map.save(filename)
        cur_date += datetime.timedelta(days=1)
