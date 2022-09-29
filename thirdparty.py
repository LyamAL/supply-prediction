from datetime import timedelta

import numpy as np
import pandas
from matplotlib import pyplot as plt


def fillna(df, year):
    df['dt'] = df.index
    df["dt"] = df.apply(lambda x: datetime.fromtimestamp(x['dt']), axis=1)
    df = df[['dt', 'res']]
    ls = to_Date(year)
    df_all = pandas.DataFrame({'dt': ls}, columns=['dt'])
    df_all["ts"] = df_all.apply(lambda x: x['dt'].timestamp(), axis=1)
    df = pandas.merge(df, df_all, on=['dt'], how='right')
    df['ts'] = df['ts'].astype(int)
    df.index = df['ts']
    df = df[['dt', 'res']]
    df.fillna(0, inplace=True)
    return df


def to_Date(year):
    low = datetime(year, 3, 10, hour=8)
    high = datetime(year, 7, 31, hour=8)
    cur = low
    lst = list()
    # lst.append(cur.strftime("%m-%d"))
    lst.append(cur)
    while cur < high:
        cur = (cur + timedelta(days=+1))
        lst.append(cur)
        # lst.append(cur.strftime("%m-%d"))
    return lst


def draw(df, col1, col2):
    # 所有三方配送下 每天营业部能收到多少单 / 所有三方的仓库 每个营业站每天能收到多少单
    df_t = df.groupby(['md', col1])[col2].sum().unstack()
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.sum(), axis=1)  # 每个营业部平均值
    return df_t
    # df_t['res'].plot(xticks=tricks, use_index=False, xlim=[low, high], legend=True, label=label)
    # y = df_t['res']
    # lst = to_Date()
    # new_y = Series()
    # for i, v in y.items():
    #     new_y = new_y.append(Series({datetime.fromtimestamp(i): 0}))
    # for i in lst:
    #     y = y.append(Series({i: 0}))
    # plt.plot(tricks, y, label=label)
    # print(df_t['res'].max())
    # print(df_t['res'].min())


def filter_shanghai(df):
    cities = ['河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川',
              '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '北京', '天津', '重庆', '广东']
    for i in cities:
        df = df.drop(df[df['signed_sitename'].str.contains(i)].index)
        print(df.shape[0])

    print('----------------------')


if __name__ == '__main__':
    df_repo = pandas.read_csv('F:/myStuff/供应预测/数据/Downloads/上海202203_202207三方配订单数据_20220819231133.csv', engine='python',
                              skip_blank_lines=True, parse_dates=['start_opt_day'])
    df_send = pandas.read_csv('F:/myStuff/供应预测/数据/Downloads/上海202203_202207三方配妥投数据_20220819231205.csv', engine='python',
                              skip_blank_lines=True, parse_dates=['signed_time_day'])
    df_repo.dropna(subset=['signed_sitename'], inplace=True)
    df_send.dropna(subset=['signed_sitename'], inplace=True)
    df_send.dropna(subset=['signed_time_day'], inplace=True)
    # 时间转换
    # a = df_send['company_name'].unique()
    # b = df_repo['company_name'].unique()
    # df_send = df_send[df_send['company_short'] == 'YUNDA']
    # df_repo = df_repo[df_repo['company_short'] == 'YUNDA']
    df_send['signed_time_day'] = pandas.to_datetime(df_send['signed_time_day'], format='%Y-%m-%d')

    df_send['md'] = df_send['signed_time_day'].apply(lambda x: int(x.timestamp()))
    df_repo['md'] = df_repo['start_opt_day'].apply(lambda x: int(x.timestamp()))
    filter_shanghai(df_repo)
    filter_shanghai(df_send)
    from datetime import datetime

    high1 = datetime(2021, 7, 31, hour=10)
    low1 = datetime(2021, 3, 10, hour=0)
    df_send1 = df_send[df_send['signed_time_day'] >= low1]
    df_send1 = df_send1[df_send1['signed_time_day'] <= high1]

    df_repo1 = df_repo[df_repo['start_opt_day'] >= low1]
    df_repo1 = df_repo1[df_repo1['start_opt_day'] <= high1]

    high = datetime(2022, 7, 31, hour=10)
    low = datetime(2022, 3, 10, hour=0)
    df_send2 = df_send[df_send['signed_time_day'] >= low]
    df_repo2 = df_repo[df_repo['start_opt_day'] >= low]
    df_repo2 = df_repo2[df_repo2['start_opt_day'] <= high]
    df_send2 = df_send2[df_send2['signed_time_day'] <= high]

    df_zy_tt = pandas.read_csv('F:/myStuff/供应预测/数据/妥投数据.csv', engine='python', skip_blank_lines=True
                               , parse_dates=['realtime_finish_dt'])
    df_zy_tt.dropna(subset=['countwaybill'], inplace=True)
    df_zy_tt.dropna(subset=['realtime_finish_dt'], inplace=True)
    df_zy_tt = df_zy_tt[df_zy_tt['realtime_finish_dt'] >= low]
    df_zy_tt = df_zy_tt[df_zy_tt['realtime_finish_dt'] <= high]
    # df_zy_tt['md'] = df_zy_tt['real_delv_day'].apply(lambda x: int(x.timestamp()))
    df_zy_tt['md'] = df_zy_tt['realtime_finish_dt'].apply(lambda x: int(x.timestamp()))

    df_zy_repo = pandas.read_csv('F:/myStuff/供应预测/数据/仓处理数据-对应到营业站.csv', engine='python', skip_blank_lines=True
                                 , parse_dates=['dt'])
    df_zy_repo.dropna(subset=['countwaybill'], inplace=True)
    df_zy_repo.dropna(subset=['dt'], inplace=True)

    df_zy_repo['md'] = df_zy_repo['dt'].apply(lambda x: int(x.timestamp()))
    # df_zy_repo['md'] = df_zy_repo['dt'].apply(lambda x: x.strftime('%m-%d'))

    # 2021
    df_zy_tt_1 = pandas.read_csv('F:/myStuff/供应预测/数据/常规数据/常规妥投.csv', engine='python', skip_blank_lines=True
                                 , parse_dates=['real_delv_day'])
    # df_zy_tt.dropna(subset=['countwaybill'], inplace=True)
    # df_zy_tt.dropna(subset=['realtime_finish_dt'], inplace=True)
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
    fig.suptitle('自营和三方两指标对比', fontsize=20)
    xaxis = np.arange(1646841600, 1659225601, 86400)
    # subplot1
    axes1 = axes[0, 0]

    df_t1 = draw(df_zy_tt, 'node_code', 'countwaybill')
    df_t2 = draw(df_zy_repo, 'node_code', 'countwaybill')

    axes1.plot(xaxis, df_t1['res'], color='#ff7f0e', ls='--', label='自营-营业部当日妥投总量')
    axes1.plot(xaxis, df_t2['res'], color='#007f0e', ls='--', label='自营-仓库当日处理量')
    ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks_]

    axes1.set_xticks(my_x_ticks_)  # 设置x轴
    axes1.set_xticklabels(ax_xlabels, rotation=30)

    # axes1.xaxis.set_major_locator(MultipleLocator(604800))
    axes1.set_title('2022年自营的站点妥投量和仓库处理量对比')
    axes1.set_ylabel('日总量')  # 设置子图的小标题
    axes1.grid(True)  # 显示网格
    axes1.legend()

    df_t3 = draw(df_send2, 'signed_sitecode', 'shipid_num')
    df_t4 = draw(df_repo2, 'signed_sitecode', 'shipid_num')
    df_t3 = fillna(df_t3, 2022)
    df_t4 = fillna(df_t4, 2022)
    axes2 = axes[0, 1]
    axes2.plot(xaxis, df_t3['res'], color='#ff7f0e', ls='--', label='三方-营业部当日妥投总量')
    axes2.plot(xaxis, df_t4['res'], color='#007f0e', ls='--', label='三方-仓库当日处理量')
    axes2.set_xticks(my_x_ticks_)  # 设置x轴
    axes2.set_xticklabels(ax_xlabels, rotation=30)
    axes2.set_title('2022年三方的站点妥投量和仓库处理量对比')
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
    df_t7 = fillna(df_t7, 2021)
    df_t8 = fillna(df_t8, 2021)
    axes4 = axes[1, 1]
    axes4.plot(xaxis, df_t7['res'], color='#ff7f0e', ls='--', label='三方-营业部当日妥投总量')
    axes4.plot(xaxis, df_t8['res'], color='#007f0e', ls='--', label='三方-仓库当日处理量')
    axes4.set_title('2021年三方的站点妥投量和仓库处理量对比')
    axes4.set_ylabel('日总量')  # 设置子图的小标题
    axes4.set_xticks(my_x_ticks_)  # 设置x轴
    axes4.set_xticklabels(ax_xlabels, rotation=30)
    axes4.grid(True)  # 显示网格
    axes4.legend()

    # plt.ylabel('日总单量')
    # plt.xlabel('日期')
    # plt.title('自营 仓库每日处理量 和 妥投量分析(0301-0731)')
    plt.savefig('./三方和自营对比分析(0310-0731)')
    plt.show()
