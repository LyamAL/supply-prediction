import pandas


def warehouse_features():
    warehouse_df_all = pandas.read_csv(
        'F:\myStuff\数据\仓_gps_营业部_polygon_\仓库地址坐标品类距离_v3.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df = pandas.read_csv(
        'F:\myStuff\数据\仓\\available_warehouses.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df.drop('store_name_c_x', inplace=True, axis=1)
    warehouse_df.drop('store_name_c', inplace=True, axis=1)
    city_df = pandas.read_csv(
        'F:\myStuff\数据\仓_gps_营业部_polygon_\城市到上海距离.csv',
        engine='python',
        skip_blank_lines=True)

    warehouse_df = pandas.merge(warehouse_df, warehouse_df_all, on=['store_id_c', 'delv_center_num_c'],
                                how='left')
    warehouse_df = pandas.merge(warehouse_df, city_df, on='city',
                                how='left')
    df = warehouse_df[['store_id_c', 'delv_center_num_c', 'store_name_c', 'city', 'storetype', 'city_dis']]
    print(df.shape[0])  # 169个
    df.to_csv('F:\myStuff\数据\仓\warehouse_features.csv', index=False)


def filter_sites():
    # 合并所有站点
    ware_to_site_df = pandas.read_csv(
        'F:\myStuff\数据\\20220926_new\仓_上海_1月_8月仓至站数据_20220926175202.csv',
        engine='python',
        skip_blank_lines=True)
    sites_df1 = ware_to_site_df[['site_id_c', 'site_name_c']]
    sites_df1.drop_duplicates(inplace=True)
    site_df = pandas.read_csv(
        'F:\myStuff\数据\\20220926_new\上海_1_8月_仓_出站量_20220926175203.csv',
        engine='python',
        skip_blank_lines=True)
    sites_df2 = site_df[['site_id_c']]
    sites_df2.drop_duplicates(inplace=True)
    site_df = pandas.merge(sites_df2, sites_df1, on='site_id_c', how='inner')
    print(sites_df1.shape[0])
    print(sites_df2.shape[0])
    site_df.drop_duplicates(inplace=True)
    print(site_df.shape[0])
    site_df.to_csv('F:\myStuff\数据\营业站\\available_sites.csv', index=False)
    pass


def site_relations():
    site_df = pandas.read_csv(
        'F:\myStuff\数据\营业站\\available_sites.csv',
        engine='python',
        skip_blank_lines=True)
    site_df_all = pandas.read_csv(
        'F:\myStuff\数据\营业站\\上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    site_df_all = site_df_all[['site_code', 'node_name', 'lng_new', 'lat_new', '']]
    df = pandas.merge(site_df_all, site_df, left_on='node_name', right_on='site_name_c', how='right')
    print(df.shape[0])
    pass


def warehouse_relations():
    pass


if __name__ == '__main__':
    # warehouse_features()
    # filter_sites()

    # warehouse_relations()
    site_relations()

    site_gps_revised()
