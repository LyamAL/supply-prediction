import datetime
import os
import random

import matplotlib.pyplot as plt
import numpy
import numpy as np
import pandas

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def plot(row):
    plt.scatter(row['width'], row['height'], marker="o", s=100, alpha=0.3, c=row['color'])
    pass


def plotSingle(w, h, c):
    plt.scatter(w, h, marker="o", s=100, alpha=0.3, c=c)
    pass


def plot_qty(row):
    plt.axline((row['w1'], row['h1']), (row['w2'], row['h2']))  # 画订单
    plt.text((row['w1'] + row['w2']) / 2, (row['h1'] + row['h2']) / 2, row['sale_ord_count'],
             verticalalignment='center')
    pass


def levelize(df, attr):
    city_range = df[attr].value_counts().sort_index().index.tolist()
    city_map = dict(zip(city_range, list(range(len(city_range)))))
    df[attr] = df[attr].map(city_map)
    return df


def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range


def randomlist(start, end, len):
    return random.sample(range(start, end), len)


# 画所有仓和站
def draw(warehouse_df, site_df):
    warehouse_df.dropna(subset=['city_dis'], inplace=True)
    plt.axis('off')
    len = 1200
    plt.xlim(0, len)
    plt.ylim(0, len)
    warehouse_df.sort_values(by='city_dis', ascending=True, inplace=True)
    warehouse_df = levelize(warehouse_df, 'city_dis')
    df_sh = warehouse_df[warehouse_df['city'] == '上海市']
    df_sh['c1'] = 'green'
    df_not_sh = warehouse_df[warehouse_df['city'] != '上海市']
    df_not_sh['c1'] = 'blue'
    df_not_sh['h1'] = random.sample(range(int(len * 0.34), int(len * 0.95)), df_not_sh.shape[0])
    # df_not_sh['h1'] = normalization(df_not_sh['city_dis']) * len * 0.65 + len * 0.3
    randms = random.sample(range(1, int(len * 0.3)), df_sh.shape[0])
    df_sh['h1'] = (df_sh['city_dis']) * len * 0.3 + randms
    warehouse_df = pandas.concat([df_sh, df_not_sh])

    warehouse_df['w1'] = random.sample(range(1, int(len * 0.46)), warehouse_df.shape[0])

    # 画营业站
    site_df['h2'] = random.sample(range(1, int(len * 0.98)), site_df.shape[0])
    site_df['c2'] = 'red'
    site_df['w2'] = random.sample(range(int(len * 0.55), int(len * 0.98)), site_df.shape[0])

    return warehouse_df, site_df


if __name__ == '__main__':
    df = pandas.read_csv('/Users/lyam/同步空间/数据/仓/ware-site_qty.csv', engine='python',
                         parse_dates=['sale_ord_dt_c'], skip_blank_lines=True)
    dfg = df.groupby(['sale_ord_dt_c', 'storetype'])
    dfs = df.drop_duplicates(subset=['site_id_c'])
    dfs.apply(lambda x: plotSingle(x['w2'], x['h2'], x['c2']), axis=1)
    for k, v in dfg:
        ymd = k[0].strftime("%m-%d")
        plt.title("{dt}-{tp}".format(dt=ymd, tp=k[1]))
        # 画所有仓
        v.apply(lambda x: plotSingle(x['w1'], x['h1'], x['c1']), axis=1)
        v.apply(plot_qty, axis=1)
        newpath = r'pngs/{dt}/{tp}'.format(dt=ymd, tp=k)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        plt.savefig("pngs/{dt}/{tp}/{dt}_{tp}.png".format(dt=ymd, tp=k))
        plt.show()
    exit(0)
    storetype_df = pandas.read_csv('/Users/lyam/同步空间/数据/仓/warehouse_features_v2.csv', engine='python',
                                   skip_blank_lines=True)
    site_df = pandas.read_csv('/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv', engine='python',
                              skip_blank_lines=True)
    storetype_df, site_df = draw(storetype_df, site_df)
    site_df = site_df[['site_id_c', 'w2', 'h2', 'c2']]
    storetype_df = storetype_df[['store_id_c', 'w1', 'h1', 'c1', 'delv_center_num_c', 'storetype']]
    ws_df = pandas.read_csv('csvs/mergeCity后的仓至站.csv', engine='python', parse_dates=['sale_ord_dt_c'],
                            skip_blank_lines=True)
    ws_df = ws_df[['sale_ord_dt_c', 'store_id_c', 'delv_center_num_c', 'site_id_c', 'sale_ord_count']]
    start_date = datetime.datetime(2022, 1, 1, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 15, hour=0, minute=0, second=0)
    cur_date = start_date

    df_res = pandas.DataFrame(
        columns=['store_id_c', 'delv_center_num_c', 'site_id_c', 'h1', 'w1', 'h2', 'w2', 'sale_ord_count',
                 'sale_ord_dt_c', 'c1', 'c2',
                 'storetype'])
    # 是否有单量
    while cur_date <= end_date:
        tomorrow = cur_date + datetime.timedelta(days=1)
        ymd = cur_date.strftime("%y-%m-%d")
        ware_to_site_daily_df = ws_df[
            (ws_df['sale_ord_dt_c'] >= cur_date) & (ws_df['sale_ord_dt_c'] < tomorrow)]
        ware_to_site_daily_df = pandas.merge(ware_to_site_daily_df, storetype_df,
                                             on=['store_id_c', 'delv_center_num_c'], how='left')
        ware_to_site_daily_df = pandas.merge(ware_to_site_daily_df, site_df,
                                             on=['site_id_c'], how='left')
        dfg = ware_to_site_daily_df.groupby('storetype')
        for k, v in dfg:
            dfgg = v.groupby(['store_id_c', 'delv_center_num_c', 'site_id_c'])
            for kk, vv in dfgg:
                # same type,same warehouse, same day,same site
                if vv.shape[0] <= 1:
                    df_res = pandas.concat([df_res, vv])
                else:
                    fr = vv.iloc[0]
                    fr['sale_ord_count'] = vv['sale_ord_count'].sum()
                    fr = fr.to_dict()
                    df_res = pandas.concat([df_res, pandas.DataFrame([fr])])
            # plt.title("{dt}-{tp}".format(dt=ymd, tp=k))
            # v.apply(plot, axis=1)  # 画仓

            # v.apply(plot_qty, axis=1)
            # TODO 新建文件夹
            # plt.savefig("pngs/{dt}/{dt}-{tp}.png".format(dt=ymd, tp=k))
            # plt.show()
            pass
        cur_date = tomorrow
    df_res.to_csv('/Users/lyam/同步空间/数据/仓/ware-site_qty.csv', index=False)
    pass
