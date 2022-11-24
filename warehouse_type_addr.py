import datetime

import pandas
import matplotlib.pyplot as plt
import seaborn as sns
import util
# from ceshi import draw
from warehouse_type import merge


def mergeType1(df, df_qty):
    df_all = pandas.DataFrame(columns=df.columns)
    dfg = df.groupby('address')
    for addr, wdf in dfg:
        if wdf.shape[0] == 1:
            df_all = pandas.concat([df_all, wdf],
                                   ignore_index=False, sort=False)
            continue
        types = wdf['type'].unique()
        for typee in types:
            type_df = wdf[wdf['type'] == typee]
            first_row_df = type_df.iloc[0]
            sid = first_row_df['store_id_c']
            dcnc = first_row_df['delv_center_num_c']
            stn = first_row_df['store_name_c']
            merged_ids = type_df.index[1:]
            for merged_id in merged_ids:
                origin_store_id = wdf.at[merged_id, 'store_id_c']
                origin_delv_id = wdf.at[merged_id, 'delv_center_num_c']

                # 修改单量表
                df_qty_change = df_qty[
                    (df_qty['store_id_c'] == origin_store_id) & (df_qty['delv_center_num_c'] == origin_delv_id)]
                changed_ids = df_qty_change.index
                for changed_id in changed_ids:
                    df_qty.at[changed_id, 'store_id_c'] = sid
                    df_qty.at[changed_id, 'delv_center_num_c'] = dcnc
                    df_qty.at[changed_id, 'store_name_c'] = stn

                wdf.at[merged_id, 'store_id_c'] = sid
                wdf.at[merged_id, 'delv_center_num_c'] = dcnc
                wdf.at[merged_id, 'store_name_c'] = stn
            # 直接合并所有条
        df_all = pandas.concat([df_all, wdf],
                               ignore_index=False, sort=False)
    return df_all


def mergeType(df, df_qty):
    df_all = pandas.DataFrame(columns=df.columns)
    dfg = df.groupby(['type', 'delv_center_num_c'])
    for tp, wdf in dfg:
        if wdf.shape[0] == 1:
            df_all = pandas.concat([df_all, wdf],
                                   ignore_index=False, sort=False)
            continue
        else:
            first_row_df = wdf.iloc[0]
            sid = first_row_df['store_id_c']
            stn = first_row_df['store_name_c']
            merged_ids = wdf.index[1:]
            # 对每个合并掉的仓库（修改store id） 更新订单表
            for merged_id in merged_ids:
                origin_store_id = wdf.at[merged_id, 'store_id_c']
                # 修改单量表 找到仓库
                df_qty_change = df_qty[
                    (df_qty['store_id_c'] == origin_store_id) & (
                            df_qty['delv_center_num_c'] == first_row_df['delv_center_num_c'])]
                changed_ids = df_qty_change.index
                for changed_id in changed_ids:
                    df_qty.at[changed_id, 'store_id_c'] = sid
                    df_qty.at[changed_id, 'store_name_c'] = stn

                wdf.at[merged_id, 'store_id_c'] = sid
                wdf.at[merged_id, 'store_name_c'] = stn
                wdf.at[merged_id, 'dis'] = first_row_df['dis']
                wdf.at[merged_id, 'address'] = first_row_df['address']
            # 直接合并所有条
        df_all = pandas.concat([df_all, wdf],
                               ignore_index=False, sort=False)
    return df_all, df_qty


def getGPS():
    warehouse_df = pandas.read_csv(
        'F:\myStuff\数据\疫情场景数据\仓地址_771.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df['addr'] = warehouse_df.apply(
        lambda x: x['store_name_c'] if len(x['addr']) <= 1 else x['addr'], axis=1)

    warehouse_df[['lng', 'lat']] = warehouse_df.apply(
        lambda x: util.geocodeBDetailed(x['addr']), axis=1,
        result_type='expand')

    count = warehouse_df[warehouse_df['lat'] == 0].shape[0]

    while count > 5:
        if count <= 13:
            warehouse_df['addr'] = warehouse_df.apply(
                lambda x: x['addr'][:15] if x['lat'] == 0 else x['addr'], axis=1,
                result_type='expand')
        warehouse_df[['lng', 'lat']] = warehouse_df.apply(
            lambda x: (x['lng'], x['lat']) if x['lat'] != 0 else util.geocodeBDetailed(x['addr']), axis=1,
            result_type='expand')
        count = warehouse_df[warehouse_df['lat'] == 0].shape[0]

    warehouse_df.to_csv('F:\myStuff\数据\疫情场景数据\仓地址_771.csv', index=False)
    exit(0)


def label_point(x, y, val, ax):
    a = pandas.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'] + .02, point['y'], str(point['val']), weight='ultralight', va='top',
                horizontalalignment='center')


def drawAll(df, dt):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.xlabel('距离（KM）')
    plt.ylabel('单量')
    # df = df.loc[df['sale_ord_count'] != df['sale_ord_count'].max()]
    # df = df[df['dis'] < 400]
    # df = df[df['sale_ord_count'] < 1e6]
    plt.xlim(0, max(df['city']))
    plt.ylim(0, max(df['sale_ord_count']))
    for t in ls2:
        plt.xlim(0, max(df['city_dis']))
        plt.ylim(0, max(df['sale_ord_count']))
        df_t = df[df['storetype'] == t]
        print(df_t.shape[0])
        df_t = df_t[
            ['store_id_c', 'delv_center_num_c', 'sale_ord_count', 'store_name_c', 'province', 'city', 'city_dis',
             'storetype']]
        sns.scatterplot(x="city_dis", y="sale_ord_count", data=df_t)
        # 拉长x轴
        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])

        label_point(df_t.city_dis, df_t.sale_ord_count, df_t.city, plt.gca())
        # df_t.to_csv('F:\myStuff\数据\分析\仓\距离和单量\订单量城市距离{dt}_{t}.csv'.format(t=t, dt=dt), index=False)
        plt.xlabel('距离（KM）')
        plt.ylabel('单量')
        plt.title('同品类（{t}）仓的距离和单量关系'.format(t=t))
        plt.savefig('F:\myStuff\数据\分析\仓\距离和单量\dis_in_ord_{t}_{dt}.png'.format(t=t, dt=dt))
        plt.show()
    # sns.lmplot(x="dis", y="sale_ord_count", data=df, hue='type', col='type', col_wrap=3)
    # sns.scatterplot(data=df, hue='storetype', x="city_dis", y="sale_ord_count")

    # plt.title('{dt}同品类仓的距离和单量关系'.format(dt=dt))
    # plt.xlabel('距离（KM）')
    # plt.ylabel('单量')
    # plt.savefig('F:\myStuff\数据\分析\仓\距离和单量\dis_sale_ord_v4_{dt}.png'.format(dt=dt), dt=dt)
    # plt.show()


ls = ['FDC', '新通路', '综合']
ls2 = ['商超', '小电', '药品', '百货', '3C', '健康', '服装', '图书', '生鲜', '冷链', '零售']


def mergeByCity(warehouse_df, df_qty, qty_has_center_id):
    warehouse_df = warehouse_df[
        ['store_id_c', 'store_name_c', 'delv_center_num_c', 'delv_center_name_c', 'storetype', 'province', 'city']]

    # 同品类 -> 同delv center -> 合并
    dfg = warehouse_df.groupby(['storetype', 'delv_center_num_c'])
    df_all = pandas.DataFrame(columns=warehouse_df.columns)
    for k, df_grouped in dfg:
        if df_grouped.shape[0] == 1:
            df_all = pandas.concat([df_all, df_grouped],
                                   ignore_index=False, sort=False)
            continue
        dfgg = df_grouped.groupby('city')
        for kk, df_groupeded in dfgg:
            if df_groupeded.shape[0] == 1:
                df_all = pandas.concat([df_all, df_groupeded],
                                       ignore_index=False, sort=False)
                continue
            # 要合并的
            first_row_df = df_groupeded.iloc[0]
            indexs = df_groupeded.index[1:]
            for idx in indexs:
                origin_store_id = df_groupeded.at[idx, 'store_id_c']
                origin_store_name = df_groupeded.at[idx, 'store_name_c']
                if qty_has_center_id:
                    df_qty_change = df_qty[
                        (df_qty['store_id_c'] == origin_store_id) & (
                                df_qty['delv_center_num_c'] == first_row_df['delv_center_num_c'])]
                else:
                    df_qty_change = df_qty[df_qty['store_name_c'] == origin_store_name]

                changed_ids = df_qty_change.index
                for changed_id in changed_ids:
                    df_qty.at[changed_id, 'store_id_c'] = first_row_df['store_id_c']
                    df_qty.at[changed_id, 'store_name_c'] = first_row_df['store_name_c']

                df_grouped.at[idx, 'store_id_c'] = first_row_df['store_id_c']
                df_grouped.at[idx, 'store_name_c'] = first_row_df['store_name_c']
            df_all = pandas.concat([df_all, df_grouped],
                                   ignore_index=False, sort=False)

    df_all.drop_duplicates(inplace=True)
    return df_all, df_qty


def drawByCities(df, dt):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 8))
    # plt.xlim(0, max(df['city_dis']))
    plt.ylim(0, max(df['sale_ord_count']))
    df.sort_values(by=['city_dis'], ascending=True, inplace=True)
    df = levelize(df)
    ax_xlabels = list(df['city'].unique())  # 24
    my_x_ticks_ = list(df['city_dis'].unique())  # 24
    for t in ls2:
        df_t = df[df['storetype'] == t]
        df_t.sort_values(by=['city_dis'], ascending=True, inplace=True)
        plt.xticks(my_x_ticks_, ax_xlabels, rotation=30)
        plt.xlabel('距离（KM）')
        plt.ylabel('单量')
        sns.scatterplot(x="city_dis", y="sale_ord_count", data=df_t)
        plt.title('同品类（{t}）仓的距离和单量关系'.format(t=t))
        plt.savefig('F:\myStuff\数据\分析\仓\城市和单量\city_in_ord_{t}_{dt}.png'.format(t=t, dt=dt))
    plt.show()
    pass


def levelize(df):
    city_range = df['city_dis'].value_counts().sort_index().index.tolist()
    city_map = dict(zip(city_range, list(range(len(city_range)))))
    df['city_dis'] = df['city_dis'].map(city_map)
    return df


def filter_warehouse_qty_(qty_path, dt_attr, tp):
    warehouse_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df = warehouse_df[
        ['store_id_c', 'store_name_c', 'delv_center_num_c', 'delv_center_name_c', 'storetype', 'province', 'city']]
    warehouse_df.sort_values(by=['store_id_c', 'delv_center_num_c'], ascending=True, inplace=True)
    warehouse_df.reset_index(drop=True, inplace=True)

    warehouse_df['storetype'] = warehouse_df['storetype'].apply(lambda x: merge(x))
    # province_df = pandas.read_csv(
    #     'F:\myStuff\数据\仓_gps_营业部_polygon_\省份到上海距离.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    # city_df = pandas.read_csv(
    #     'F:\myStuff\数据\仓_gps_营业部_polygon_\城市到上海距离.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    in_df = pandas.read_csv(
        qty_path,
        engine='python', parse_dates=[dt_attr],
        skip_blank_lines=True)
    # in_df.drop('Unnamed: 0', inplace=True, axis=1)
    in_df.dropna(subset=['sale_ord_count'], inplace=True)
    in_df.sort_values(by=['store_id_c', 'delv_center_num_c'], ascending=True, inplace=True)
    in_df.reset_index(drop=True, inplace=True)

    # 按配送中心所在城市匹配
    warehouse_df, in_df = mergeByCity(warehouse_df, in_df, True)

    in_df.to_csv('csvs/mergeCity后的_{t}_仓库单量表.csv'.format(t=tp), index=False)
    exit(0)
    warehouse_df.drop_duplicates(inplace=True)

    warehouse_df = warehouse_df[warehouse_df['storetype'] != '其他']
    # warehouse_df = warehouse_df[warehouse_df['storetype'].isin(ls2)]

    # startdate = datetime.datetime(2022, 3, 1)
    # enddate = datetime.datetime(2022, 7, 1)
    # in_df1 = in_df[(in_df['sale_ord_dt_c'] <= startdate)]
    # in_df2 = in_df[(in_df['sale_ord_dt_c'] >= enddate)]
    # in_df = pandas.concat([in_df1, in_df2], ignore_index=False)

    # in_df['sale_ord_dt_c'] = in_df['sale_ord_dt_c'].apply(
    #     lambda x: (x.strftime("%m%d")))

    in_df = in_df[['store_id_c', 'delv_center_num_c']]
    in_df.drop_duplicates(inplace=True)
    # in_df = in_df[['sale_ord_dt_c', 'store_id_c', 'delv_center_num_c', 'sale_ord_count']]
    df = pandas.merge(warehouse_df, in_df, on=['store_id_c', 'delv_center_num_c'],
                      how='inner')
    print(df.shape[0])
    df.to_csv('csvs/{t}_warehouse_unique_.csv'.format(t=tp), index=False)

    # 画图用

    # df = df[['sale_ord_dt_c', 'store_id_c', 'delv_center_num_c', 'sale_ord_count']]
    # warehouse_info_df = warehouse_df[
    #     ['store_id_c', 'delv_center_num_c', 'province', 'city', 'store_name_c', 'storetype']]
    # warehouse_info_df.drop_duplicates(inplace=True)  # 601
    # df1 = df.groupby(['store_id_c', 'delv_center_num_c'])['sale_ord_count'].sum().reset_index(name='sale_ord_count')
    # df_res = pandas.merge(df1, warehouse_info_df, how='left', on=['store_id_c', 'delv_center_num_c'])

    # df_res = pandas.merge(df_res, province_df, on='province', how='left')
    # df_res = pandas.merge(df_res, city_df, on='city', how='left')

    # df_res.to_csv('temp_1_2_7_8_sale_city.csv', index=False)
    # draw()
    # drawAll(df_res)


def extractProvince_City():
    warehouse_df1 = pandas.read_csv(
        'F:\myStuff\数据\仓_gps_营业部_polygon_\仓库地址坐标品类_new.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df1['address'] = warehouse_df1['address'].str.replace('（', '(', regex=False)
    warehouse_df1['address'] = warehouse_df1['address'].str.replace('（', ')', regex=False)
    warehouse_df1['address'] = warehouse_df1['address'].str.replace('\u3000', '', regex=False)
    warehouse_df1['address'] = warehouse_df1['address'].str.replace(' ', '', regex=False)
    warehouse_df1[['province', 'city']] = warehouse_df1['address'].str.extract('(.{2,3}省)([^市]{2,4}市).*',
                                                                               expand=True)

    warehouse_df_not_nan = warehouse_df1[warehouse_df1['province'].notnull()]
    warehouse_df_nan = warehouse_df1[warehouse_df1[['province']].isnull().T.any()]
    warehouse_df_nan[['province', 'city']] = warehouse_df_nan.apply(
        lambda x: util.degeocodeBDetailed(x['lat'], x['lng']),
        result_type='expand', axis=1)
    warehouse_df1 = pandas.concat([warehouse_df_not_nan, warehouse_df_nan],
                                  ignore_index=True, sort=False)
    # 计算到上海的距离
    warehouse_df1.to_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\仓库地址坐标品类距离_v3.csv', index=False)
    exit(0)


def cal_distance():
    province_df = warehouse_df.drop_duplicates(subset=['province'])
    province_df = province_df[['province']]
    # city_df = warehouse_df.drop_duplicates(subset=['city'])
    # city_df = city_df[['city']]

    province_df['pro_lat'] = 0
    province_df['pro_lng'] = 0
    # city_df['city_lng'] = 0
    # city_df['city_lat'] = 0

    while len(province_df[province_df['pro_lat'] == 0]) > 0:
        province_df[['pro_lng', 'pro_lat']] = province_df.apply(
            lambda x: util.geocodeBDetailed(x['province']) if x['pro_lat'] == 0 else (x['pro_lng'], x['pro_lat']),
            axis=1,
            result_type='expand')
    # while len(city_df[city_df['city_lat'] == 0]) > 0:
    #     city_df[['city_lng', 'city_lat']] = city_df.apply(
    #         lambda x: util.geocodeBDetailed(x['city']) if x['city_lat'] == 0 else (x['city_lng'], x['city_lat']),
    #         axis=1,
    #         result_type='expand')

    # province_df['pro_dis'] = province_df.apply(
    #     lambda x: util.distance(x['pro_lng'], x['pro_lat'], 121.4737021, 31.2303904),
    #     axis=1)
    # city_df['city_dis'] = city_df.apply(lambda x: util.distance(x['city_lng'], x['city_lat'], 121.4737021, 31.2303904),
    #                                     axis=1)

    province_df.to_csv('/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/省份到上海距离_v2.csv', index=False)
    # city_df.to_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\城市到上海距离.csv', index=False)

    exit(0)
def filter_warehouse_site_():
    warehouse_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv',
        engine='python',
        skip_blank_lines=True)
    warehouse_df.drop_duplicates(subset=['store_id_c', 'delv_center_num_c'], inplace=True)
    warehouse_df = warehouse_df[warehouse_df['storetype'] != '其他']
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/20220926_new/仓_上海_1月_8月仓至站数据_20221004130333.csv',
        engine='python', encoding='gbk',
        skip_blank_lines=True)
    # site_df = pandas.read_csv(
    #     'site_df_t_0929.csv',
    #     engine='python',
    #     skip_blank_lines=True)
    # TODO 待数据更新修改！
    # sale_ord_dt_c,store_id_c,store_name_c,delv_center_num_c,delv_center_name_c,site_id_c,site_name_c,sale_ord_count
    site_df.dropna(subset=['sale_ord_count'], inplace=True)
    site_df.drop_duplicates(inplace=True)
    site_df.sort_values(by=['store_id_c', 'delv_center_num_c'], ascending=True, inplace=True)
    site_df.reset_index(drop=True, inplace=True)
    # site_df = site_df[['store_id_c', 'delv_center_num_c']]
    # site_df.to_csv('site_df_t_0929.csv', index=False)
    # exit(0)
    print('before merge', site_df.shape[0])
    warehouse_df, site_df_ = mergeByCity(warehouse_df, site_df, True)
    # site_df_.drop_duplicates(inplace=True)
    site_df.to_csv('csvs/mergeCity后的仓至站.csv', index=False)
    print('after merge', site_df_.shape[0])
    exit(0)
    # site_df = site_df['store_name_c']
    df = pandas.merge(warehouse_df, site_df, on=['store_id_c', 'delv_center_num_c'],
                      how='inner')
    print(df.shape[0])

    df.to_csv('csvs/ware-to-site_warehouse_unique_v2.csv', index=False)
    pass


if __name__ == '__main__':
    # extractProvince_City()
    # filter_warehouse_qty_('/Users/lyam/同步空间/数据/20220926_new/上海_1_8月_仓_订单量_20220926212534.csv',
    #                       'sale_ord_dt_c', '订单量')
    # filter_warehouse_qty_('/Users/lyam/同步空间/数据/20220926_new/上海_1_8月_仓_出仓量_20220926212042.csv',
    #                       'first_sorting_tm_c', '出仓量')
    print('3')
    cal_distance()

    filter_warehouse_site_()
    df1 = pandas.read_csv(
        'csvs/ware-to-site_warehouse_unique_v2.csv',
        engine='python',
        skip_blank_lines=True)
    df1 = df1[['delv_center_num_c', 'store_id_c']]
    df1.drop_duplicates(inplace=True)

    df2 = pandas.read_csv(
        'csvs/out_warehouse_unique_.csv',
        engine='python',
        skip_blank_lines=True)
    df2 = df2[['delv_center_num_c', 'store_id_c']]
    df2.drop_duplicates(inplace=True)

    df3 = pandas.read_csv(
        'csvs/sale_warehouse_unique_.csv',
        engine='python',
        skip_blank_lines=True)
    df3 = df3[['delv_center_num_c', 'store_id_c']]
    df3.drop_duplicates(inplace=True)

    df = pandas.merge(df2, df3, on=['delv_center_num_c', 'store_id_c'], how='inner')
    df.drop_duplicates(inplace=True, subset=['delv_center_num_c', 'store_id_c'])
    df_res = pandas.merge(df, df1, on=['delv_center_num_c', 'store_id_c'], how='inner')
    df_res.to_csv('/Users/lyam/同步空间/数据/仓/available_warehouses_v2.csv', index=False)
