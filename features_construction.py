import datetime

import folium
import geopandas
import numpy
import pandas
from shapely import geometry

from shapely.geometry import MultiPolygon

import util
from site_covid_visual import random_color, visualizze

map = folium.Map(location=[31.3004, 121.294], zoom_start=10)


def warehouse_features():
    warehouse_df_all = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/available_warehouses_v2.csv',
        engine='python',
        skip_blank_lines=True)
    # warehouse_df.drop('store_name_c_x', inplace=True, axis=1)
    # warehouse_df.drop('store_name_c', inplace=True, axis=1)
    city_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/城市到上海距离.csv',
        engine='python',
        skip_blank_lines=True)

    warehouse_df = pandas.merge(warehouse_df, warehouse_df_all, on=['store_id_c', 'delv_center_num_c'],
                                how='left')
    warehouse_df.drop_duplicates(subset=['store_id_c', 'delv_center_num_c'], inplace=True)
    warehouse_df = pandas.merge(warehouse_df, city_df, on='city',
                                how='left')
    df = warehouse_df[['store_id_c', 'delv_center_num_c', 'store_name_c', 'city', 'storetype', 'city_dis']]
    print(df.shape[0])  # 169个
    df.to_csv('/Users/lyam/同步空间/数据/仓/warehouse_features_v2.csv', index=False)


def filter_sites():
    # 合并所有站点
    # ware_to_site_df = pandas.read_csv(
    #     '/Users/lyam/Documents/mystuff/idea/数据/仓数据/20220906/仓_上海_1月_8月仓至站数据_20220908191143.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    # sites_df1 = ware_to_site_df[['site_id_c', 'site_name_c']]
    # sites_df1.to_csv('temp_site.csv', index=False)
    sites_df1 = pandas.read_csv(
        'temp_site.csv',
        engine='python',
        skip_blank_lines=True)
    site_df = pandas.read_csv(
        '/Users/lyam/Documents/mystuff/idea/数据/仓数据/20220906/上海_1_8月_仓_出站量_20220906200232.csv',
        engine='python', encoding='gb2312',
        skip_blank_lines=True)
    sites_df2 = site_df[['site_id_c']]
    sites_df2.drop_duplicates(inplace=True)
    site_df = pandas.merge(sites_df2, sites_df1, on='site_id_c', how='left')
    print(sites_df1.shape[0])
    print(sites_df2.shape[0])
    site_df.drop_duplicates(inplace=True)
    print(site_df.shape[0])
    site_df.to_csv('/Users/lyam/同步空间/数据/营业站/available_sites.csv', index=False)
    site_df.to_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/available_sites.csv', index=False)
    exit(0)


def toGeoFence(site_df, fence_attr):
    site_df[fence_attr] = geopandas.GeoSeries.from_wkt(site_df[fence_attr])
    site_df = geopandas.GeoDataFrame(site_df, geometry=fence_attr)
    site_df.set_crs(epsg="4326", inplace=True)
    return site_df


def site_relations():
    # 合并fence
    # site_df = pandas.read_csv(
    #     '/Users/lyam/Documents/mystuff/idea/数据/营业站/available_sites.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    # site_df_all = pandas.read_csv(
    #     '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    # site_df_all = site_df_all[['site_code', 'fence', 'node_name']]
    # site_df_all.drop_duplicates(inplace=True)
    # site_df = pandas.merge(site_df_all, site_df, left_on='site_code', right_on='site_id_c', how='right')
    # # site_df = site_df[['site_id_c', 'site_name_c', 'fence']]
    # df_nan = site_df[site_df[['fence']].isnull().T.any()]
    # df_nan.to_csv('/Users/lyam/同步空间/数据/营业站/sites_in_qty_but_no_fence.csv', index=False)
    # site_df.dropna(inplace=True)
    # site_df.drop_duplicates(inplace=True)
    # print(site_df.shape[0])
    # site_df = toGeoFence(site_df, 'fence')
    # site_miyun_df = site_df[site_df['site_name_c'] == '上海密云营业部']
    # polygons = list()
    # indxs = list()
    # for idx, row in site_miyun_df.iterrows():
    #     indxs.append(idx)
    #     polygons.append(row['fence'])
    # site_df.at[indxs[0], 'fence'] = MultiPolygon(polygons)
    # site_df.drop(index=indxs[1:], inplace=True)
    #
    # site_df.sort_values(by=['site_id_c'], ascending=True, inplace=True)
    # length = site_df.shape[0]
    # site_df.index = range(length)
    # site_df.to_csv('/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv', index=False)
    # exit(0)
    # site_df.to_csv('/Users/lyam/同步空间/数据/营业站/available_sites_with_fences.csv', index=False)  # 285个
    # exit(0)

    # 构建表
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
    site_df.sort_values(by=['site_id_c'], ascending=True, inplace=True)
    length = site_df.shape[0]
    site_df.index = range(length)
    site_df_b = site_df
    site_relations_df = pandas.DataFrame(columns=range(length), index=range(length))
    site_distance_df_ = pandas.DataFrame(columns=range(length), index=range(length))

    for idx, row in site_df.iterrows():
        for i, r in site_df_b.iterrows():
            if i == idx:
                isNeighbor = 1
                distance = 0
            else:
                isNeighbor = int(r['fence'].touches(row['fence']) or r['fence'].overlaps(row['fence']))
                distance = util.distance(r['lng'], r['lat'], row['lng'], row['lat'])
            site_relations_df.at[idx, i] = isNeighbor
            site_distance_df_.at[idx, i] = round(distance, 5)
    site_relations_df.to_csv('/Users/lyam/同步空间/数据/营业站/site_relations_01_matrix.csv', index=False)
    site_distance_df_.to_csv('/Users/lyam/同步空间/数据/营业站/site_distances.csv', index=False)
    pass


def warehouse_relations():
    warehouse_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/warehouse_features_v2.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df.sort_values(by=['store_id_c', 'delv_center_num_c'], ascending=True, inplace=True)
    length = warehouse_df.shape[0]
    warehouse_df.index = range(length)
    warehouse_df_b = warehouse_df
    warehouse_relation_df = pandas.DataFrame(columns=range(length), index=range(length))
    for idx, row in warehouse_df.iterrows():
        for i, r in warehouse_df_b.iterrows():
            # 是否品类关联
            if row['storetype'] == r['storetype']:
                warehouse_relation_df.at[idx, i] = r['storetype']
            else:
                warehouse_relation_df.at[idx, i] = 0
    print(warehouse_relation_df)
    warehouse_relation_df.to_csv('/Users/lyam/同步空间/数据/仓/warehouse_relations_v2.csv', index=False)
    pass


def site_gps_revised():
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    site_df = site_df[['site_code', 'node_name', 'lng', 'lat', 'fence', 'county_name']]
    site_df = toGeoFence(site_df, 'fence')

    site_miyun_df = site_df[site_df['node_name'] == '上海密云营业部']
    polygons = list()
    indxs = list()
    for idx, row in site_miyun_df.iterrows():
        indxs.append(idx)
        polygons.append(row['fence'])
    site_df.at[indxs[0], 'fence'] = MultiPolygon(polygons)
    site_df.drop(index=indxs[1:], inplace=True)

    site_df.sort_values(by=['site_code'], ascending=True, inplace=True)
    length = site_df.shape[0]
    site_df.index = range(length)

    site_df[['lng', 'lat']] = site_df.apply(
        lambda x: util.centroidShapely(x['fence']), axis=1,
        result_type='expand')
    site_df['in_poly'] = site_df.apply(lambda x: util.pnpolyShaple(x['fence'], geometry.Point(x['lng'], x['lat'])),
                                       axis=1)  # 4
    # visualizze(site_df[site_df['in_poly_2'] == False])
    site_df.drop('in_poly', axis=1, inplace=True)
    site_df.to_csv('/Users/lyam/同步空间/数据/营业站/site_revised_gps_v2.csv', index=False)
    pass


def site_features():
    site_early_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_04160517.csv',
        engine='python',
        skip_blank_lines=True)
    site_late_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_05250809.csv',
        engine='python',
        skip_blank_lines=True)
    site_all_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    sites = list(site_all_df['site_code'])
    site_early_df = site_early_df[site_early_df['site_code'].isin(sites)]
    site_late_df = site_late_df[site_late_df['site_code'].isin(sites)]
    site_covid_df = pandas.concat([site_early_df, site_late_df])
    site_covid_df.to_csv('/Users/lyam/同步空间/数据/营业站/site_features_covid.csv', index=False)
    exit(0)


def warehouse_site_relations():
    # multiIndex way
    # Set 3 axis labels/dims
    start_date = datetime.datetime(2022, 1, 1, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 15, hour=0, minute=0, second=0)
    cur_date = start_date
    dates = list()
    while cur_date <= end_date:
        dates.append(cur_date.strftime("%y-%m-%d"))
        cur_date += datetime.timedelta(days=1)

    available_warehouses_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/available_warehouses_v2.csv',
        engine='python',
        skip_blank_lines=True)
    available_sites_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_size = available_warehouses_df.shape[0]
    site_size = available_sites_df.shape[0]
    warehouses = numpy.arange(0, warehouse_size)  # 仓
    sites = numpy.arange(0, site_size)  # 仓
    Array_3D = numpy.zeros((len(dates), warehouses.size, len(sites)))
    # Reshape data to 2 dimensions
    maj_dim = 1
    for dim in Array_3D.shape[:-1]:
        maj_dim = maj_dim * dim
    new_dims = (maj_dim, Array_3D.shape[-1])
    Array_3D = Array_3D.reshape(new_dims)
    # Create the MultiIndex
    midx = pandas.MultiIndex.from_product([dates, warehouses])
    # Create sample data for each patient, and add the MultiIndex.
    ware_site_relations_df = pandas.DataFrame(data=Array_3D,
                                              index=midx,
                                              columns=sites)
    ware_to_site_df = pandas.read_csv(
        'csvs/mergeCity后的仓至站.csv', parse_dates=['sale_ord_dt_c'],
        engine='python',
        skip_blank_lines=True)
    print(ware_to_site_df.shape[0])
    ware_to_site_df.drop_duplicates(subset=['site_id_c', 'sale_ord_dt_c', 'store_id_c', 'delv_center_num_c'],
                                    inplace=True)
    print(ware_to_site_df.shape[0])

    # 是否有单量
    cur_date = start_date
    while cur_date <= end_date:
        tomorrow = cur_date + datetime.timedelta(days=1)
        ymd = cur_date.strftime("%y-%m-%d")
        # sale_ord_dt_c,store_id_c,store_name_c,delv_center_num_c,delv_center_name_c,site_id_c,site_name_c,sale_ord_count
        ware_to_site_daily_df = ware_to_site_df[
            (ware_to_site_df['sale_ord_dt_c'] >= cur_date) & (ware_to_site_df['sale_ord_dt_c'] < tomorrow)]
        for idx, row in available_warehouses_df.iterrows():
            exact_warehouse_df = ware_to_site_daily_df[
                (ware_to_site_daily_df['store_id_c'] == row['store_id_c']) & (
                        ware_to_site_daily_df['delv_center_num_c'] == row['delv_center_num_c'])]
            for i, r in available_sites_df.iterrows():
                exact_warehouse_site_df = exact_warehouse_df[
                    exact_warehouse_df['site_id_c'] == r['site_id_c']]
                haveOrders = int(exact_warehouse_site_df.shape[0] > 0)
                # if exact_warehouse_site_df.shape[0] == 0:
                #     haveOrders = 0
                #     print('no orders. warehouse:{idx}, site: {i}'.format(idx=idx, i=i))
                # else:
                #     # TODO 可以改成单量
                #     # haveOrders = int(exact_warehouse_site_df['sale_ord_count'].sum() > 0)
                ware_site_relations_df.at[(ymd, idx), i] = haveOrders
        cur_date = tomorrow
    ware_site_relations_df.to_csv('/Users/lyam/同步空间/数据/仓/ware_site_relations.csv', index=True)
    pass


def reIndex(df):
    length = df.shape[0]
    df.index = range(length)
    return df


def sequence_data():
    # 仓
    available_warehouses_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/available_warehouses_v2.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_out_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/20220926_new/mergeCity后的_出仓量_仓库单量表.csv',
        engine='python', parse_dates=['first_sorting_tm_c'],
        skip_blank_lines=True)
    warehouse_out_df = pandas.merge(warehouse_out_df, available_warehouses_df, on=['store_id_c', 'delv_center_num_c'],
                                    how='right')
    warehouse_out_df.drop('delv_center_name_c', inplace=True, axis=1)
    warehouse_out_df.drop('store_name_c', inplace=True, axis=1)
    warehouse_out_df.columns = ['dt', 'store_id_c', 'delv_center_num_c', 'count']
    warehouse_seq_df = pandas.DataFrame(columns=['dt', 'store_id_c', 'delv_center_num_c', 'count'])
    dfg = warehouse_out_df.groupby(['dt', 'store_id_c', 'delv_center_num_c'])
    for k, v in dfg:
        if v.shape[0] <= 1:
            warehouse_seq_df = pandas.concat([warehouse_seq_df, v])
        else:
            data = v.iloc[0]
            data['count'] = v['count'].sum()
            data = data.to_dict()
            warehouse_seq_df = pandas.concat([warehouse_seq_df, pandas.DataFrame([data])])

    warehouse_seq_df.sort_values(by=['dt', 'store_id_c', 'delv_center_num_c'], inplace=True, ascending=True)
    warehouse_seq_df = reIndex(warehouse_seq_df)
    warehouse_seq_df.to_csv('/Users/lyam/同步空间/数据/仓/warehouse_out_sequence.csv', index=False)
    # 站
    available_sites_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    sites_out_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/20220926_new/上海_1_8月_仓_出站量_20220926175203.csv',
        engine='python', parse_dates=['real_delv_tm_c'],
        skip_blank_lines=True)
    available_sites_df = available_sites_df[['site_id_c']]
    sites_out_df = pandas.merge(sites_out_df, available_sites_df, how='right', on='site_id_c')
    sites_out_df.drop('site_name_c', inplace=True, axis=1)
    sites_out_df.columns = ['dt', 'site_id_c', 'count']

    sites_seq_df = pandas.DataFrame(columns=['dt', 'site_id_c', 'count'])
    dfg = sites_out_df.groupby(['dt', 'site_id_c'])
    for k, v in dfg:
        if v.shape[0] <= 1:
            sites_seq_df = pandas.concat([sites_seq_df, v])
        else:
            data = v.iloc[0]
            data['count'] = v['count'].sum()
            data = data.to_dict()
            sites_seq_df = pandas.concat([sites_seq_df, pandas.DataFrame([data])])
    sites_seq_df.sort_values(by=['dt', 'site_id_c'], inplace=True, ascending=True)
    sites_seq_df = reIndex(sites_seq_df)
    sites_seq_df.to_csv('/Users/lyam/同步空间/数据/仓/site_out_sequence.csv', index=False)
    pass


if __name__ == '__main__':
    # warehouse_features()
    # filter_sites()
    # site_gps_revised()
    # warehouse_relations()
    # site_relations()
    # site_features()
    # warehouse_site_relations()

    # available_warehouses_df = pandas.read_csv(
    #     '/Users/lyam/同步空间/数据/仓/ware_site_relations.csv',
    #     engine='python', index_col=[0, 1],
    #     skip_blank_lines=True)
    sequence_data()
