import os
from datetime import datetime

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def df_attributed(df):
    df_tt = df.groupby(['md', 'type'])['sale_ord_count']
    df_t = df_tt.sum().unstack()  # 收集每天每个站点产生的对应单量
    df_t = df_t.fillna(0)
    df_t["平均水平"] = df_t.apply(lambda x: x.mean(), axis=1)  # 求所有站点总和
    # df_t.reset_index(inplace=True)
    return df_t


if __name__ == '__main__':
    df_out = pd.read_csv('F:/myStuff/数据/20220906/上海_1_8月_仓_出仓量_20220906200242.csv', engine='python',
                         skip_blank_lines=True, parse_dates=['first_sorting_tm_c'])
    df_in = pd.read_csv('F:/myStuff/数据/20220906/上海_1_8月_仓_订单量_20220906200512.csv', engine='python',
                        skip_blank_lines=True, parse_dates=['sale_ord_dt_c'])
    # df_site_in = pd.read_csv('F:/myStuff/数据/20220906/上海_1_8月_仓_入站量_20220906200142.csv', engine='python',
    #                      skip_blank_lines=True, parse_dates=['end_node_insp_tm_c'])
    # df_site_out = pd.read_csv('F:/myStuff/数据/20220906/上海_1_8月_仓_出站量_20220906200232.csv', engine='python',
    #                      skip_blank_lines=True, parse_dates=['real_delv_tm_c'])
    df_type = pd.read_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\warehouse_type_v3.csv', engine='python',
                          skip_blank_lines=True)

    df_out = pd.merge(df_out, df_type, on='store_name_c', how='left')
    df_out = df_out[['first_sorting_tm_c', 'store_name_c', 'sale_ord_count', 'type', 'sub_type']]

    df_in = pd.merge(df_in, df_type, on='store_name_c', how='left')
    df_in = df_in[['sale_ord_dt_c', 'store_name_c', 'sale_ord_count', 'type', 'sub_type']]

    df_in = df_in[df_in['type'] != '其他']
    df_out = df_out[df_out['type'] != '其他']
    df_out = df_out.dropna(subset=['store_name_c'])
    df_in = df_in.dropna(subset=['store_name_c'])
    df_out = df_out.dropna(subset=['first_sorting_tm_c'])
    df_in = df_in.dropna(subset=['sale_ord_dt_c'])

    df_in['md'] = df_in['sale_ord_dt_c'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
    df_out['md'] = df_out['first_sorting_tm_c'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))

    df_out['sale_ord_count'] = df_out['sale_ord_count'].astype(int)
    df_in['sale_ord_count'] = df_in['sale_ord_count'].astype(int)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(20, 15))
    fig, ax = plt.subplots()
    # ax.xaxis.set_major_locator(MultipleLocator(7))

    # df.set_index(["md"], inplace=True)
    df_o = df_attributed(df_out)
    df_i = df_attributed(df_in)

    top10 = ['食品酒类', '个护清洁', '家居日用', '平均水平', '3C', '母婴玩具', '医药保健', '宠物', '家用电器', '服饰']
    df_o = df_o[top10]
    df_i = df_i[top10]

    my_x_ticks_ = np.arange(1640966400, 1661698800, 604800)
    ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks_]
    ls = df_i.columns.values.tolist()

    s1 = 40 / plt.gcf().dpi * len(ax_xlabels) + 2 * 0.2
    margin = 0.2 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    # plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    s2 = 130 / plt.gcf().dpi * 6 + 2 * 0.2
    margin = 0.2 / plt.gcf().get_size_inches()[1]
    plt.gcf().subplots_adjust(bottom=margin, top=1. - margin)
    plt.gcf().set_size_inches(s1, s2)
    # plt.ylim(0, 400000)

    # 个护清洁，公共平台，休闲食品，饮料冲调，水果生鲜，米面粮油，家居日用，数码通讯，综合，服装，母婴玩具
    # df_o['res'].plot(kind='line', legend=True, label='出仓量')
    # df_i['res'].plot(kind='line', legend=True, label='当日总下单量')
    plt.xticks(ticks=my_x_ticks_, labels=ax_xlabels)
    sns.lineplot(data=df_i)
    plt.ylabel('数量')
    plt.xlabel('日期')
    plt.title('上海仓库类型与每日订单量分析')
    plt.savefig('./上海仓库类型每日订单量分析')
    plt.show()
    exit(0)

    # sns.lineplot(x="md", y="package_qty", markers="o", data=df, estimator=np.median)
    # sns.lineplot(x="md", y="rec_qty", markers="o", data=df, estimator=np.median)
    # sns.lineplot(x="md", y="unfin_qty", markers="o", data=df, estimator=np.median)
    # sns.lineplot(x="md", y="order_qty", markers="o", data=df, estimator=np.median)
    # sns.lineplot(x="md", y="valid_order_qty", markers="o", data=df, estimator=np.median)
    plt.legend(labels=['总单量', '接收单量', '未生产单量', '当日总下单量', '有效单量'], loc='upper right')
    plt.savefig('./上海仓库每日总单量分析2(0426-0512)')
    plt.show()
    exit(0)
