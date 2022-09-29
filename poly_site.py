import webbrowser

import folium
import geopandas
import numpy as np

import pandas
# 生成随机颜色
import random


def style(feature):
    return {
        'fillColor': feature['properties']['color'],
        'fillOpacity': 0.7, 'color': '#ffffff', 'weight': 0.7, 'opacity': 0.7
    }


def colored(id):
    if len(id) > 6:
        return '#' + id[0:6]
    if len(id) == 6:
        return '#' + id
    return '#' + id + '5' * (6 - len(id))


if __name__ == '__main__':
    # df_latlng = pandas.read_csv('F:\myStuff\数据\AQIDEA\上海营业站位置信息_20220904222813.csv', engine='python',
    #                             skip_blank_lines=True)
    # df_latlng.drop_duplicates(subset=['ql_id'])
    # df_latlng.dropna(subset=['lng'], inplace=True)
    # df_latlng = df_latlng[['ql_id', 'node_name', 'address', 'lng', 'lat']]
    # geometry = geopandas.points_from_xy(df_latlng.lng, df_latlng.lat)
    # geo_df = geopandas.GeoDataFrame(df_latlng[['ql_id', 'node_name', 'address', 'lat', 'lng']], geometry=geometry)

    df = geopandas.read_file('F:\myStuff\数据\AQIDEA\上海营业站围栏数据_20220905005442.csv', encoding='utf-8')
    df.dropna(subset=['aoi_polygon'], inplace=True)
    df['aoi_polygon'] = geopandas.GeoSeries.from_wkt(df['aoi_polygon'])
    my_geo_df = geopandas.GeoDataFrame(df, geometry='aoi_polygon')
    my_geo_df['color'] = ''
    my_geo_df.set_crs(epsg="4326", inplace=True)
    m = folium.Map(location=[31.2303904, 121.4737021],
                   width='100%', height='100%',
                   zoom_start=11)
    # geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]
    # for coordinates in geo_df_list:
    #     m.add_child(folium.Marker(location=coordinates, icon=folium.Icon(color="green")))
    my_geo_df['color'] = my_geo_df.apply(lambda x: colored(x['site_id']), axis=1)
    # dfg = my_geo_df.groupby('site_id')

    # for k, v in dfg:
    #     color = colored()
    #     for x in v.index:
    #         v.at[x, 'color'] = color
    #     # for _, r in v.iterrows():
    #     #     sim_geo = geopandas.GeoSeries(r['aoi_polygon']).simplify(tolerance=0.001)
    #     #     geo_j = sim_geo.to_json()
    #     #     geo_j = folium.GeoJson(data=geo_j,
    #     #                            style_function=lambda x: {'fillColor': color, 'fillOpacity': 0.7,
    #     #                                                      'color': '#ffffff', 'weight': 0.7,
    #     #                                                      'opacity': 0.7})
    #     #     folium.Popup(r['site_name']).add_to(geo_j)
    #     #     geo_j.add_to(m)

    folium.GeoJson(data=my_geo_df, style_function=style).add_to(m)
    m.save('map1.html')
    webbrowser.open_new_tab('map.html')
