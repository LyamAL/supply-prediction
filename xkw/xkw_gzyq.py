import datetime

import folium
import geopandas
import pandas
from matplotlib.ticker import MultipleLocator

import util
from delay_check import toHours
from features_construction import toGeoFence
from site_covid_visual import random_color
from site_covid_with_more_dates import formatAddress


def yq1():
    site_early_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_04160517.csv',
        engine='python',
        skip_blank_lines=True)
    site_late_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_05250809.csv',
        engine='python',
        skip_blank_lines=True)
    # site_all_df = pandas.read_csv(
    #     '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
    #     engine='python',
    #     skip_blank_lines=True)

    # df2 = pandas.read_excel(
    # '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/fomulated_files.xlsx')
    # ls = list(df2.columns)
    # site_early_df = site_early_df[~site_early_df['node_name'].isin(ls)]
    # site_late_df = site_late_df[~site_late_df['node_name'].isin(ls)]
    site_covid_df = pandas.concat([site_early_df, site_late_df])
    site_covid_df.to_csv('covid_sites_unfiltered.csv', index=False, encoding='gbk')
    print(site_covid_df.drop_duplicates(subset=['site_code', 'dt']).shape[0])
    pass


def yq2():
    map = folium.Map(location=[31.3004, 121.294], zoom_start=10)
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)
    df2 = pandas.read_excel(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/fomulated_files.xlsx')
    ls = list(df2.columns)
    site_df = site_df[site_df['node_name'].isin(ls)]

    poly_color = [random_color() for _ in range(site_df.shape[0])]
    site_df['color'] = poly_color
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
                'fillOpacity': 0.5},
        )
        polyg_.add_to(map)

    map.fit_bounds(map.get_bounds(), padding=(10, 10))

    map.save('xkw/fomulated_files.html')


def yq3():
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    site_df = toGeoFence(site_df, 'fence')
    site_df['area'] = site_df.apply(lambda x: x['fence'].area, axis=1)
    site_df = site_df[['area', 'site_code']]
    covid_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/site_features_covid.csv',
        engine='python',
        skip_blank_lines=True)
    covid_df = pandas.merge(site_df, covid_df, on='site_code', how='right')
    covid_df.to_csv('site_info.csv', index=False)
    pass


def srtp():
    dt_ls = ['real_delv_tm', 'route_start_node_real_send_tm', 'start_opt_tm']
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/全阶段/所有订单数据.csv',
        parse_dates=dt_ls,
        engine='python', skip_blank_lines=True)
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.dropna(subset=['route_start_node_real_send_tm'], inplace=True)
    df = df[df['real_delv_tm'] < datetime.datetime(2022, 8, 15)]
    df = df[df['real_delv_tm'] >= datetime.datetime(2022, 1, 1)]
    df = df[df['route_start_node_real_send_tm'] < datetime.datetime(2022, 8, 15)]
    df = df[df['route_start_node_real_send_tm'] >= datetime.datetime(2022, 1, 1)]
    # yq4(df)
    yq5(df)


def yq4(df):
    df = df[['real_delv_tm', 'route_start_node_real_send_tm', 'waybill_code', 'start_node_name']]
    df['route_start_node_real_send_dt'] = df['route_start_node_real_send_tm'].apply(
        lambda x: x.replace(hour=0, minute=0, second=0))
    df = df[
        (df['route_start_node_real_send_dt'] == datetime.datetime(2022, 6, 27)) | (
                df['route_start_node_real_send_dt'] == datetime.datetime(2022, 4, 15))]

    df['delay_seconds'] = df.apply(
        lambda x: (x['real_delv_tm'] - x['route_start_node_real_send_tm']).total_seconds(), axis=1)
    df['delay_days'] = df.apply(
        lambda x: toHours(x['delay_seconds']), axis=1)

    address_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    address_df = address_df[['store_name_c', 'city']]
    df = pandas.merge(df, address_df, right_on='store_name_c', left_on='start_node_name', how='left')
    df.dropna(subset=['city'], inplace=True)
    df = df[df['city'].isin(['上海市', '武汉市', '广州市', '北京市'])]
    df_common = df[df['route_start_node_real_send_dt'] == datetime.datetime(2022, 6, 27)]
    df_common['avg_delay_days'] = (
        df_common['delay_days'].groupby(df_common['city']).transform('mean'))
    df_covid = df[df['route_start_node_real_send_dt'] == datetime.datetime(2022, 4, 15)]
    df_covid['avg_delay_days'] = (
        df_covid['delay_days'].groupby(df_covid['city']).transform('mean'))
    df_covid['covid'] = '疫情场景'
    df_common['covid'] = '常规场景'
    df = pandas.concat([df_covid, df_common])
    df['dt'] = df['route_start_node_real_send_tm'].dt.strftime('%m-%d')

    df = df[['dt', 'avg_delay_days', 'city', 'covid']]
    df.drop_duplicates(inplace=True)
    df.sort_values(by='dt', inplace=True)

    from matplotlib import pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # plt.figure(figsize=(12, 10))
    import seaborn as sns
    ax = sns.barplot(data=df, x='city', y="avg_delay_days", hue='covid', palette=['#D98880', '#7DCEA0'])
    plt.legend(title='')
    ax.grid(True)
    ax.set_xlabel('日期')
    ax.set_ylabel('耗时(天)')
    ax.set_title(f'2022年不同城市出仓发往上海运单的时效性分析')
    plt.savefig('../pngs/夏凯文/时效分析.png')
    plt.show()


df_res = pandas.DataFrame()

m = folium.Map(location=[39.35531, 117.22924], zoom_start=10)


def yq5_splitroute(x):
    global df_res
    routes = x.recommended_routing.split('->')
    data = {'dt': x['dt']}
    k = 1
    for idx, route in enumerate(routes):
        if '接货仓' in route:
            k = 1
            continue
        pairs = route.split('_')
        if idx == 0:
            k = 1
            data['warehouse'] = pairs[2]
        else:
            col = 'Route' + str(k)
            data[col] = pairs[2]
            k += 1
    df_res = df_res.append([data], ignore_index=False)


def yq5_plotLine(x):
    loc = [(x.lat_w, x.lng_w), (x.lat_c, x.lng_c)]
    if x['dt'] == '04-02':
        color = 'red'
    else:
        color = 'green'
    folium.PolyLine(loc,
                    color=color,
                    weight=3,
                    opacity=0.7).add_to(m)
    pass


def yq5_plotDot(point):
    folium.CircleMarker(location=[point.city_lat, point.city_lng],
                        radius=1, fillOpacity=0.7, color='red',
                        weight=10).add_to(m)
    pass


def yq5_draw():
    df_ = pandas.read_csv(
        '../csvs/route_df.csv', engine='python',
        skip_blank_lines=True)

    address_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/城市到上海距离.csv', engine='python',
        skip_blank_lines=True)
    ls = ['上海市', '苏州市', '沈阳市', '东莞市', '合肥市', '武汉市',
          '佛山市', '天津市', '宁波市', '成都市', '西安市', '无锡市']
    address_df = address_df[address_df['city'].isin(ls)]

    address_df.apply(lambda x: yq5_plotDot(x), axis=1)

    # node_addr_df = node_addr_df[['lng', 'lat', 'node_code']]
    # node_addr_df = node_addr_df.rename(columns={'lng': 'lng_c', 'lat': 'lat_c'})
    # node_addr_df.drop_duplicates(inplace=True)
    # address_df = address_df[['store_name_c', 'lat', 'lng']]
    # address_df = address_df.rename(columns={'lng': 'lng_w', 'lat': 'lat_w', 'store_name_c': 'route_a'})
    # address_df.drop_duplicates(inplace=True)
    # df_ = pandas.merge(address_df, df_, on='route_a', how='right')
    # df_nan = df_[df_[['lat_w']].isnull().T.any()]
    # df_nan_ = pandas.merge(node_addr_df, df_nan, left_on='node_code', right_on='route_a', how='right')
    # df_nan_['lat_w'] = df_nan_['lat_c']
    # df_nan_['lng_w'] = df_nan_['lng_c']
    # df_nan_.drop(['lat_c', 'lng_c', 'node_code'], axis=1, inplace=True)
    # df_ = pandas.concat([df_nan_, df_])
    # df_.dropna(subset=['lat_w'], inplace=True)
    # df_ = pandas.merge(node_addr_df, df_, left_on='node_code', right_on='route_b', how='right')
    # df_.dropna(subset=['lng_c'], inplace=True)
    # df_.drop_duplicates(inplace=True)
    # df_.apply(lambda x: yq5_plotDot(x), axis=1)
    m.save('../htmls/paths_routes_distribution.html')
    exit(0)


def yq5(df):
    df['start_opt_dt'] = df['start_opt_tm'].apply(
        lambda x: x.replace(hour=0, minute=0, second=0))
    # df = df[
    #     (df['start_opt_dt'] == datetime.datetime(2022, 6, 27, 0, 0, 0)) | (
    #             df['start_opt_dt'] == datetime.datetime(2022, 4, 3))]
    df['dt'] = df['start_opt_tm'].dt.strftime('%m-%d')
    df.sort_values(by='dt', inplace=True)
    df = df[['waybill_code', 'recommended_routing', 'dt']]
    df.apply(lambda x: yq5_splitroute(x), axis=1)
    df_res.to_csv('../csvs/route_df.csv', index=False)
    print(len(df_res['warehouse'].unique()))
    centers = pandas.unique(df[['Route1', 'Route2', 'Route3', 'Route4', 'Route5', 'Route6']].values.ravel('K'))
    print(len(centers))
    exit(0)
    pass


def yq6():
    site_dddf = pandas.read_csv(
        'covid_sites_left.csv', encoding='gbk',
        engine='python',
        skip_blank_lines=True)
    ls = list(site_dddf['site_code'].unique())

    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    site_revised_gps_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/site_revised_gps_v2.csv',
        engine='python',
        skip_blank_lines=True)
    site_df.drop_duplicates(subset=['fence'], inplace=True)
    site_df.drop('fence', inplace=True, axis=1)
    site_revised_gps_df = toGeoFence(site_revised_gps_df, 'fence')
    site_df = pandas.merge(site_df, site_revised_gps_df, left_on='site_id_c', right_on='site_code', how='left')
    site_df = site_df[['site_id_c', 'site_name_c', 'lng', 'lat', 'fence']]

    site_df = site_df[site_df['site_id_c'].isin(ls)]
    site_df.sort_values(by=['site_id_c'], ascending=True, inplace=True)
    site_df.index = site_df['site_id_c']
    site_df_b = site_df
    site_distance_df_ = pandas.DataFrame(columns=site_df['site_id_c'], index=site_df['site_id_c'])

    for idx, row in site_df.iterrows():
        for i, r in site_df_b.iterrows():
            if i == idx:
                distance = 0
            else:
                distance = util.distance(r['lng'], r['lat'], row['lng'], row['lat'])
            site_distance_df_.at[idx, i] = round(distance, 5)
    site_distance_df_.to_csv('173_site_distances_matrix.csv', index=False)
    pass


def yq7(site_id, site_poly_all, list_content):
    from shapely.geometry import Polygon, Point
    site_poly = site_poly_all[site_poly_all['site_code'] == site_id]
    site_poly = toGeoFence(site_poly, 'fence')

    site_polygon = site_poly['fence'].iloc[0]
    site_points = [[i[0], i[1]] for i in list(site_polygon.exterior.coords)]
    from mini_bounding_rect.MinimumBoundingBox import MinimumBoundingBox
    res = MinimumBoundingBox(15, 15, site_points)
    grids_poly = []
    for grid in res.grids:
        grid_polygon = Polygon([[p[1], p[0]] for p in grid])
        grids_poly.append(grid_polygon)
    pass
    grids_df = pandas.DataFrame({'grids_poly': grids_poly})
    grids_df['value'] = 0

    # 填value
    for k, v in list_content.items():
        for coords in v:
            for idx, row in grids_df.iterrows():
                p = Point(float(coords[0]), float(coords[1]))
                if row['grids_poly'].contains(p):
                    grids_df.at[idx, 'value'] = grids_df.at[idx, 'value'] + coords[2]
                    break
    grids_df.to_csv('grid_.csv', index=False)


def yq8():
    from shapely.geometry import Polygon

    site_poly = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    site_poly = toGeoFence(site_poly, 'fence')
    distance_df = pandas.DataFrame(index=range(site_poly.shape[0]))
    distance_df['site_code'] = site_poly['site_code']
    from mini_bounding_rect.MinimumBoundingBox import MinimumBoundingBox
    for i, r in site_poly.iterrows():
        site_points = [[i[0], i[1]] for i in list(r['fence'].exterior.coords)]
        res = MinimumBoundingBox(15, 15, site_points)
        grid_polygon_a = Polygon([[p[1], p[0]] for p in res.grids[0]])
        grid_polygon_b = Polygon([[p[1], p[0]] for p in res.grids[1]])
        distance_df.at[i, 'distance'] = util.distance(grid_polygon_a.centroid, grid_polygon_b.centroid)
    distance_df.to_csv('distance.csv', index=False)


def yq9(districts, covid_df):
    from shapely.geometry import Point
    grid_poly = pandas.read_csv(
        'grid_.csv',
        engine='python',
        skip_blank_lines=True)
    grid_poly['idx'] = list(range(grid_poly.shape[0]))
    # covid_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情数据/covid_with_jd_gps.csv', engine='python',
    #                            skip_blank_lines=True, encoding='utf-8',
    #                            parse_dates=['dt'])
    # covid_df = covid_df[['id', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    # covid_df.sort_values(ascending=True, inplace=True, by=['dt'])
    grid_poly = toGeoFence(grid_poly, 'grids_poly')
    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_i = covid_df[(covid_df['dt'] >= cur_date) & (covid_df['dt'] < tomorrow)]
        covid_df_i.sort_values(ascending=True, inplace=True, by=['county'])
        for county in districts:
            covid_df_i_county = covid_df_i[covid_df_i['county'] == county]
            print(cur_date, ' ', county, '有', covid_df_i_county.shape[0], '条疫情数据')
            for index, row in grid_poly.iterrows():
                isEmpty = True
                for i, r in covid_df_i_county.iterrows():
                    if util.pnpolyShaple(row['grids_poly'], Point(r['lng'], r['lat'])):
                        if isEmpty:
                            grid_poly.at[index, cur_date.strftime("%m-%d")] = str(r['id']) + '-' + r[
                                'control_type'] + ";"
                            isEmpty = False
                        else:
                            grid_poly.at[index, cur_date.strftime("%m-%d")] += str(r['id']) + '-' + r[
                                'control_type'] + ";"
        cur_date += datetime.timedelta(days=1)
    grid_poly.to_csv('covid_width_.csv', index=False)


def yq9_2():
    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date
    grid_poly = pandas.read_csv(
        'covid_width_.csv',
        engine='python',
        skip_blank_lines=True)

    grid_poly_df = pandas.DataFrame(
        columns=['idx', 'dt', 'lockdown_count', 'safe_count', 'restraint_count', 'value'])
    while cur_date <= end_date:
        md = cur_date.strftime("%m-%d")
        cur_date += datetime.timedelta(days=1)
        try:
            grid_poly_daily = grid_poly[['idx', md, 'value']]
        except Exception:
            continue
        grid_poly_daily[['lockdown_count', 'restraint_count', 'safe_count']] = grid_poly_daily.apply(
            lambda x: util.countLockDown(x[md]), axis=1,
            result_type='expand')

        for index, row in grid_poly_daily.iterrows():
            data = {'idx': row['idx'], 'value': row['value'], 'dt': cur_date,
                    'lockdown_count': row['lockdown_count'], 'restraint_count': row['restraint_count'],
                    'safe_count': row['safe_count'],
                    }
            grid_poly_df = pandas.concat([grid_poly_df, pandas.DataFrame.from_records([data])])

    grid_poly_df.to_csv('grid_covid_04160517.csv', index=False)


def yq9_3(districts):
    from shapely.geometry import Point

    covid_df = pandas.read_csv('covid_0608.csv',
                               engine='python', parse_dates=['date'],
                               skip_blank_lines=True)
    grid_df = pandas.read_csv('grid_.csv',
                              engine='python',
                              skip_blank_lines=True)

    grid_df['idx'] = list(range(grid_df.shape[0]))
    grid_df = toGeoFence(grid_df, 'grids_poly')

    start_date = datetime.datetime(2022, 5, 25, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 9, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        md = cur_date.strftime("%m-%d")
        grid_df[md] = None
        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_i = covid_df[(covid_df['date'] >= cur_date) & (covid_df['date'] < tomorrow)]
        cur_date += datetime.timedelta(days=1)
        covid_df_i.sort_values(ascending=True, inplace=True, by=['area_name'])
        for county in districts:
            covid_df_i_county = covid_df_i[covid_df_i['area_name'] == county]
            if covid_df_i_county.shape[0] == 0:
                continue
            for index, row in grid_df.iterrows():
                isEmpty = True
                for i, r in covid_df_i_county.iterrows():
                    if util.pnpolyShaple(row['grids_poly'], Point(r['lng'], r['lat'])):
                        if isEmpty:
                            grid_df.at[index, md] = str(r['id']) + '-' + r['epidemic_level'] + ";"
                            isEmpty = False
                        else:
                            grid_df.at[index, md] += str(r['id']) + '-' + r['epidemic_level'] + ";"

    grid_df_ = pandas.DataFrame(
        columns=['dt', 'lockdown_count', 'safe_count', 'restraint_count', 'idx', 'value'])
    cur_date = start_date

    while cur_date <= end_date:
        md = cur_date.strftime("%m-%d")
        cur_date += datetime.timedelta(days=1)
        grid_df_daily = grid_df[
            ['idx', 'value', md]]
        grid_df_daily[['lockdown_count', 'restraint_count', 'safe_count']] = grid_df_daily.apply(
            lambda x: util.countLockDown(x[md]), axis=1,
            result_type='expand')
        for index, row in grid_df_daily.iterrows():
            data = {'idx': row['idx'], 'value': row['value'], 'dt': cur_date,
                    'lockdown_count': row['lockdown_count'], 'restraint_count': row['restraint_count'],
                    'safe_count': row['safe_count'],
                    }
            grid_df_ = pandas.concat([grid_df_, pandas.DataFrame.from_records([data])])

    grid_df_.to_csv('grid_covid_05250809.csv', index=False)


def yq9_4(site_id):
    site_early_df = pandas.read_csv(
        'grid_covid_05250809.csv',
        engine='python',
        skip_blank_lines=True)
    site_late_df = pandas.read_csv(
        'grid_covid_04160517.csv',
        engine='python',
        skip_blank_lines=True)

    site_covid_df = pandas.concat([site_early_df, site_late_df])
    site_covid_df['site_id'] = site_id
    return site_covid_df


def yq7_9():
    import pickle
    import os
    root = '/Users/lyam/PycharmProjects/lab-supply-prediction/xkw/pkls/1s/'
    filePaths = os.listdir(root)
    content_dict = dict()
    for filePath in filePaths:
        cur_content_dict = pickle.load(open(root + filePath, 'rb'))
        for i in cur_content_dict:
            content_dict[i] = cur_content_dict[i]
    site_poly_all = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    covid_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情数据/covid_with_jd_gps.csv', engine='python',
                               skip_blank_lines=True, encoding='utf-8',
                               parse_dates=['dt'])
    covid_df = covid_df[['id', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(ascending=True, inplace=True, by=['dt'])

    districts = site_poly_all['county_name'].unique().tolist()
    df_all = pandas.DataFrame()
    for site_id in content_dict:
        yq7(site_poly_all=site_poly_all, site_id=site_id, list_content=content_dict[site_id])
        yq9(districts=districts, covid_df=covid_df)
        yq9_2()
        yq9_3(districts=districts)
        df = yq9_4(site_id=site_id)
        df_all = pandas.concat([df_all, df])
    df_all.to_csv('all_sites_covid_grids.csv', index=False)
    exit(0)


if __name__ == '__main__':
    yq7_9()
