from datetime import datetime

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

from thirdparty_ import draw

if __name__ == '__main__':
    # print(int(datetime(2022, 1, 1, hour=0, minute=0, second=0).timestamp()))
    # print(int(datetime(2022, 8, 31, hour=0, minute=0, second=0).timestamp()))
    df1 = pd.read_csv('F:\myStuff\数据\参考文献2\仓_上海_1月_8月出仓数据_20220905182552.csv', engine='python', skip_blank_lines=True,
                     parse_dates=['out_wh_dt'])
    df2 = pd.read_csv('F:\myStuff\数据\参考文献2\仓_上海_1月_8月订单数据_20220905181532.csv', engine='python', skip_blank_lines=True,
                     parse_dates=['sale_ord_dt'])
    df3 = pd.read_csv('F:\myStuff\数据\参考文献2\营业站_上海_1月_8月妥投数据_20220905182112.csv', engine='python', skip_blank_lines=True,
                     parse_dates=['delv_dt'])
    df1 = df1[df1['store_name'].str.contains('上海')]
    df2 = df2[df2['store_name'].str.contains('上海')]

    df1.dropna(subset=['out_wh_dt'], inplace=True)
    df2.dropna(subset=['sale_ord_dt'], inplace=True)
    df3.dropna(subset=['delv_dt'], inplace=True)

    # low = datetime(2022, 3, 10)
    # high = datetime(2022, 7, 31)
    # df1 = df1[df1['out_wh_dt'] >= low]
    # df1 = df1[df1['out_wh_dt'] <= high]

    # df2 = df2[df2['sale_ord_dt'] >= low]
    # df2 = df2[df2['sale_ord_dt'] <= high]

    # df3 = df3[df3['delv_dt'] >= low]
    # df3 = df3[df3['delv_dt'] <= high]
    #
    df1['out_wh_dt'] = df1['out_wh_dt'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
    df2['sale_ord_dt'] = df2['sale_ord_dt'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
    df3['delv_dt'] = df3['delv_dt'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 10))
    # 设置坐标轴范围
    # plt.ylim((0, 2250000))
    # my_y_ticks = np.arange(0, 2250000, 250000)
    # plt.yticks(my_y_ticks)
    my_x_ticks_ = np.arange(1646841600, 1659225601, 604800)
    ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks_]

    # my_x_ticks = np.arange(1640966400, 1661875200, 1296000)
    # ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks]
    # plt.xticks(ticks=my_x_ticks, labels=ax_xlabels, rotation=30)

    # df_zy_tt = pd.read_csv('F:/myStuff/数据/妥投数据.csv', engine='python', skip_blank_lines=True
    #                            , parse_dates=['realtime_finish_dt'])
    # df_zy_tt.dropna(subset=['countwaybill'], inplace=True)
    # df_zy_tt.dropna(subset=['realtime_finish_dt'], inplace=True)
    # df_zy_tt = df_zy_tt[df_zy_tt['realtime_finish_dt'] >= low]
    # df_zy_tt = df_zy_tt[df_zy_tt['realtime_finish_dt'] <= high]
    # df_zy_tt['md'] = df_zy_tt['realtime_finish_dt'].apply(lambda x: int(x.timestamp()))
    #
    #
    #
    # df_zy_repo = pd.read_csv('F:/myStuff/数据/仓处理数据-对应到营业站.csv', engine='python', skip_blank_lines=True
    #                              , parse_dates=['dt'])
    # df_zy_repo.dropna(subset=['countwaybill'], inplace=True)
    # df_zy_repo.dropna(subset=['dt'], inplace=True)
    #
    # df_zy_repo['md'] = df_zy_repo['dt'].apply(lambda x: int(x.timestamp()))

    # fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(20, 10))
    # xaxis = np.arange(1646841600, 1659225601, 86400)
    # axes1 = axes[0]
    # df_t1 = draw(df_zy_tt, 'node_code', 'countwaybill')
    # df_t2 = draw(df_zy_repo, 'node_code', 'countwaybill')
    #
    # axes1.plot(xaxis, df_t1['res'], color='#008244', label='原日妥投总量')
    # axes1.plot(xaxis, df_t2['res'], color='#907033', label='原仓库当日处理量')
    #
    # axes1.set_xticks(my_x_ticks_)  # 设置x轴
    # axes1.set_xticklabels(ax_xlabels, rotation=30)
    #
    # axes1.set_title('原-2022年站点妥投量和仓库处理量对比')
    # axes1.set_ylabel('日总量')  # 设置子图的小标题
    # axes1.grid(True)  # 显示网格
    # axes1.legend()

    # plt.ylabel('单量')
    # plt.xlabel('日期')
    # plt.title('仓库下单量/出库量/妥投量')
    # plt.savefig('./仓库单量分析01-09')
    # plt.show()
    # exit(0)

    axes2 = axes[1]
    axes2.set_xticks(my_x_ticks_)  # 设置x轴
    axes2.set_xticklabels(ax_xlabels, rotation=30)

    df_temp = df2.groupby(['sale_ord_dt', 'store_id'])['sale_ord_count'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)

    axes2.plot(xaxis, df_temp['sum'], color='#552241',  label='0905发下单量')

    # 出仓量 = out_wh_tm
    df_temp = df1.groupby(['out_wh_dt', 'store_id'])['sale_ord_count'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)
    axes2.plot(xaxis, df_temp['sum'], color='#907033', label='0905发出仓量')

    # 妥投量 = succ_delv_tm
    df_temp = df3.groupby(['delv_dt', 'site_id'])['sale_ord_count'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)
    # df_temp['sum'].plot(marker='v', ms=3, legend=True, label='妥投量')
    axes2.plot(xaxis, df_temp['sum'], color='#008244',  label='0905发妥投量')
    axes2.set_title('2022年0905数据-仓库下单量/出库量/妥投量')
    axes2.set_ylabel('日总量')  # 设置子图的小标题
    axes2.grid(True)  # 显示网格
    axes2.legend()

    plt.savefig('./对比.png')
    plt.show()

