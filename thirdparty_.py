import numpy as np
import pandas
from matplotlib import pyplot as plt
from datetime import datetime


def draw(df, col1, col2):
    df_t = df.groupby(['md', col1])[col2].sum().unstack()
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.sum(), axis=1)
    return df_t


if __name__ == '__main__':
    df_repo = pandas.read_csv('F:/myStuff/供应预测/数据/Downloads/上海202203_202207三方配订单数据_20220819231133.csv', engine='python',
                              skip_blank_lines=True, parse_dates=['start_opt_day'])
    df_send = pandas.read_csv('F:/myStuff/供应预测/数据/Downloads/上海202203_202207三方配妥投数据_20220819231205.csv', engine='python',
                              skip_blank_lines=True, parse_dates=['signed_time_day'])
    df_repo.dropna(subset=['signed_sitename'], inplace=True)
    df_send.dropna(subset=['signed_sitename'], inplace=True)
    df_send['signed_time_day'] = pandas.to_datetime(df_send['signed_time_day'], format='%Y-%m-%d')

    df_send['md'] = df_send['signed_time_day'].apply(lambda x: int(x.timestamp()))
    df_repo['md'] = df_repo['start_opt_day'].apply(lambda x: int(x.timestamp()))

    high1 = datetime(2021, 7, 31)
    low1 = datetime(2021, 3, 10)
    df_send1 = df_send[df_send['signed_time_day'] >= low1]
    df_send1 = df_send1[df_send1['signed_time_day'] <= high1]

    df_repo1 = df_repo[df_repo['start_opt_day'] >= low1]
    df_repo1 = df_repo1[df_repo1['start_opt_day'] <= high1]

    high = datetime(2022, 7, 31)
    low = datetime(2022, 3, 10)
    df_send2 = df_send[df_send['signed_time_day'] >= low]
    df_repo2 = df_repo[df_repo['start_opt_day'] >= low]
    df_repo2 = df_repo2[df_repo2['start_opt_day'] <= high]
    df_send2 = df_send2[df_send2['signed_time_day'] <= high]

    df_zy_tt = pandas.read_csv('F:/myStuff/供应预测/数据/妥投数据.csv', engine='python', skip_blank_lines=True
                               , parse_dates=['realtime_finish_dt'])
    df_zy_tt.dropna(subset=['countwaybill'], inplace=True)
    df_zy_tt.dropna(subset=['realtime_finish_dt'], inplace=True)
    df_zy_tt['md'] = df_zy_tt['realtime_finish_dt'].apply(lambda x: int(x.timestamp()))

    df_zy_repo = pandas.read_csv('F:/myStuff/供应预测/数据/仓处理数据-对应到营业站.csv', engine='python', skip_blank_lines=True
                                 , parse_dates=['dt'])
    df_zy_repo.dropna(subset=['countwaybill'], inplace=True)
    df_zy_repo.dropna(subset=['dt'], inplace=True)

    df_zy_repo['md'] = df_zy_repo['dt'].apply(lambda x: int(x.timestamp()))

    # 2021
    df_zy_tt_1 = pandas.read_csv('F:/myStuff/供应预测/数据/常规数据/常规妥投.csv', engine='python', skip_blank_lines=True
                                 , parse_dates=['real_delv_day'])
    df_zy_tt_1 = df_zy_tt_1[df_zy_tt_1['real_delv_day'] >= low1]
    df_zy_tt_1 = df_zy_tt_1[df_zy_tt_1['real_delv_day'] <= high1]
    df_zy_tt_1['md'] = df_zy_tt_1['real_delv_day'].apply(lambda x: int(x.timestamp()))

    df_zy_repo1 = pandas.read_csv('F:/myStuff/供应预测/数据/常规数据/常规出仓.csv', engine='python', skip_blank_lines=True
                                  , parse_dates=['start_opt_day'])

    df_zy_repo1 = df_zy_repo1[df_zy_repo1['start_opt_day'] >= low1]
    df_zy_repo1 = df_zy_repo1[df_zy_repo1['start_opt_day'] <= high1]
    df_zy_repo1['md'] = df_zy_repo1['start_opt_day'].apply(lambda x: int(x.timestamp()))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # 设置坐标轴范围
    plt.ylim((0, 2250000))
    my_y_ticks = np.arange(0, 2250000, 250000)
    plt.yticks(my_y_ticks)
    my_x_ticks_ = np.arange(1646841600, 1659225601, 604800)

    fig, axes = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=(20, 10))
    fig.suptitle('自营和三方两指标对比')
    xaxis = np.arange(1646841600, 1659225601, 86400)
    # subplot1
    axes1 = axes[0, 0]

    df_t1 = draw(df_zy_tt, 'node_code', 'countwaybill')
    df_t2 = draw(df_zy_repo, 'node_code', 'countwaybill')

    axes1.plot(xaxis, df_t1['res'], color='#1f77b4', ls='--', label='自营-营业部当日妥投总量')
    axes1.plot(xaxis, df_t2['res'], color='#107033', ls='--', label='自营-仓库当日处理量')
    ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks_]

    axes1.set_xticks(my_x_ticks_)  # 设置x轴
    axes1.set_xticklabels(ax_xlabels, rotation=30)

    axes1.set_title('2022年自营的站点妥投量和仓库处理量对比')
    axes1.set_ylabel('日总量')  # 设置子图的小标题
    axes1.grid(True)  # 显示网格
    axes1.legend()

    df_t3 = draw(df_send, 'signed_sitecode', 'shipid_num')
    df_t4 = draw(df_repo, 'signed_sitecode', 'shipid_num')
    axes2 = axes[0, 1]
    axes2.plot(xaxis, df_t3['res'], color='#ff7f0e', ls='--', label='三方-营业部当日妥投总量')
    axes2.plot(xaxis, df_t4['res'], color='#007f0e', ls='--', label='三方-仓库当日处理量')
    axes2.set_xticks(my_x_ticks_)  # 设置x轴
    axes2.set_xticklabels(ax_xlabels, rotation=30)
    axes2.set_title('2022年三方(YUNDA)的站点妥投量和仓库处理量对比')
    axes2.set_ylabel('日总量')  # 设置子图的小标题
    axes2.grid(True)  # 显示网格
    axes2.legend()

    df_t5 = draw(df_zy_tt_1, 'end_node_id', 'waybill_count')
    df_t6 = draw(df_zy_repo1, 'end_node_id', 'waybill_count')
    axes3 = axes[1, 0]
    my_x_ticks_ = np.arange(int(low1.timestamp()), int(high1.timestamp()), 604800)
    xaxis = np.arange(int(low1.timestamp()), int(high1.timestamp()), 86400)
    axes3.plot(xaxis, df_t5['res'], color='#ff7f0e', ls='--', label='自营-营业部当日妥投总量')
    axes3.plot(xaxis, df_t6['res'], color='#007f0e', ls='--', label='自营-仓库当日处理量')
    axes3.set_title('2021年自营的站点妥投量和仓库处理量对比')
    axes3.set_ylabel('日总量')  # 设置子图的小标题
    axes3.set_xticks(my_x_ticks_)  # 设置x轴
    axes3.set_xticklabels(ax_xlabels, rotation=30)
    axes3.grid(True)  # 显示网格
    axes3.legend()

    df_t7 = draw(df_send1, 'signed_sitecode', 'shipid_num')
    df_t8 = draw(df_repo1, 'signed_sitecode', 'shipid_num')
    axes4 = axes[1, 1]
    axes4.plot(xaxis, df_t7['res'], color='#ff7f0e', ls='--', label='三方-营业部当日妥投总量')
    axes4.plot(xaxis, df_t8['res'], color='#007f0e', ls='--', label='三方-仓库当日处理量')
    axes4.set_title('2021年三方(YUNDA)的站点妥投量和仓库处理量对比')
    axes4.set_ylabel('日总量')  # 设置子图的小标题
    axes4.set_xticks(my_x_ticks_)  # 设置x轴
    axes4.set_xticklabels(ax_xlabels, rotation=30)
    axes4.grid(True)  # 显示网格
    axes4.legend()

    plt.savefig('./疫情-自营-YUNDA仓库每日处理量和妥投量均值分析(0310-0731)')
    plt.show()
