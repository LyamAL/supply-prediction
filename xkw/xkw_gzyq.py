import datetime

import folium
import geopandas
import pandas
from matplotlib.ticker import MultipleLocator

from delay_check import toHours
from features_construction import toGeoFence
from site_covid_visual import random_color


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
        # '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/sites.xlsx')
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
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/sites.xlsx')
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

    map.save('xkw/sites.html')


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
    # df = pandas.read_csv(
    #     '../csvs/route_df.csv',
    #     engine='python', skip_blank_lines=True)
    # rts = ['Route1', 'Route2', 'Route3', 'Route4', 'Route5', 'Route6']
    # df_ = pandas.DataFrame()
    # for i, r in df.iterrows():
    #     path = {}
    #     flag = True
    #     lastCol = None
    #     for col in rts:
    #         if pandas.notna(r[col]):
    #             path['dt'] = r['dt']
    #             if flag:
    #                 path['route_a'] = r['warehouse']
    #                 path['route_b'] = r[col]
    #                 lastCol = col
    #                 flag = False
    #                 df_ = df_.append([path], ignore_index=True)
    #             else:
    #                 path['route_a'] = r[lastCol]
    #                 path['route_b'] = r[col]
    #                 lastCol = col
    #                 df_ = df_.append([path], ignore_index=True)
    #         else:
    #             break
    #     pass
    # df_.drop_duplicates(inplace=True)
    # df_.to_csv('../csvs/routes_a_b.csv', index=False)
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


if __name__ == '__main__':
    srtp()
