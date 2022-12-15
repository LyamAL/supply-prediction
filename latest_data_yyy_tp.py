import datetime
import os
import pickle
import re

import pandas
import folium
from folium import plugins
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from tqdm import tqdm

import util
from delay_check import levelize, remove_outliers, toHours, delevelize
from draw_util import series_cdf
from root_util import changePath, DISK_PATH_MACHINE


def center():
    df_u = pandas.read_csv(
        't.csv', engine='python',
        skip_blank_lines=True)
    df_names = pandas.read_csv(
        'names.csv', engine='python',
        skip_blank_lines=True)
    re_express = re.compile('([^\u4e00-\u9fa5]+)([一-龥]+分拣中心)')
    df_u[['node', 'name']] = df_u['0'].str.extract(re_express, expand=True)
    df_u['name'] = df_u.apply(lambda x: x['0'] if pandas.isnull(x['name']) else x['name'], axis=1)
    df_u.drop(['0', 'node'], inplace=True, axis=1)
    df_names = df_names[~df_names['0'].str.contains('退货组')]
    df_u = df_u[~df_u['name'].str.contains('退货组')]
    df_u.drop_duplicates(inplace=True)
    print(len(df_u['name'].unique()))

    name_df = pandas.merge(df_names, df_u, left_on='0', right_on='name', how='outer')
    name_df.drop(['0'], inplace=True, axis=1)
    name_df.to_csv('csvs/center.csv', index=False)
    pass


def OutOfTime(ware_dfg, df):
    for k, df_dis in ware_dfg:
        print(k)
        df_dis_waybill = pandas.merge(df_dis, df, left_on='store_name_c', right_on=['start_node_name'], how='left')
        df_dis_waybill['delay_seconds'] = df_dis_waybill.apply(
            lambda x: (x['real_delv_tm'] - x['plan_delv_tm']).total_seconds(), axis=1)

        df_dis_waybill['delay_days'] = df_dis_waybill.apply(
            lambda x: toHours(x['delay_seconds']), axis=1)

        df_dis_waybill['plan_delv_dt'] = df_dis_waybill['plan_delv_dt'].dt.strftime('%m-%d')
        df_dis_waybill.drop_duplicates(inplace=True)
        # 删除异常值
        df_dis_waybill = remove_outliers(df_dis_waybill, 'plan_delv_dt')

        df_dis_waybill['avg_delay_days'] = (
            df_dis_waybill['delay_days'].groupby(df_dis_waybill['plan_delv_dt']).transform('mean'))

        df_dis_waybill_res = df_dis_waybill[['avg_delay_days', 'plan_delv_dt']]
        df_dis_waybill_res.drop_duplicates(inplace=True)
        df_dis_waybill_res.sort_values(by='plan_delv_dt', inplace=True)

        from matplotlib import pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))
        import seaborn as sns
        ax = sns.barplot(data=df_dis_waybill_res, x="plan_delv_dt", y="avg_delay_days")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)
        ax.set_xlabel('计划妥投日期')
        ax.set_ylabel('延迟天数')
        ax.set_title(f'{delevelize(k)}仓库运单-超时分析(下单-妥投)')
        s1 = 200 / plt.gcf().dpi * 10
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig(f'pngs/下单-妥投/{k}_超时分析.png')
        plt.show()
    pass


nodes = ['first_sorting_real_arv_node', 'second_sorting_real_arv_node', 'third_sorting_real_arv_node',
         'fourth_sorting_real_arv_node', 'fifth_sorting_real_arv_node', 'sixth_sorting_real_arv_node',
         'seventh_sorting_real_arv_node']


def countRoutes(row):
    if pandas.isna(row['end_sorting_name']):
        return 0

    # names_ls = ['second_sorting_name', 'fourth_sorting_name']
    count = 0
    for i in nodes:
        if pandas.notna(row[i]):
            count += 1
    if count == 0:
        return 1
    return count


# 'end_sorting_name' != None 表示 分拣中心>=1
def Routing(df):
    # 路由分布分析 top10 路由变化情况
    # 'end_sorting_name' == None 表示 无分拣中心直接仓到站
    df = df[df['end_sorting_name'].notna()]
    df['route_dt'] = df['start_opt_tm'].dt.strftime('%m-%d')
    df.sort_values(by='route_dt', inplace=True)
    node_addr_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/全阶段/分拣中心addr.csv', engine='python',
        skip_blank_lines=True)
    node_addr_df.drop(['Unnamed: 0', 'update_time', 'node_name'], inplace=True, axis=1)

    map = folium.Map(location=[31.38383, 121.25309], zoom_start=13)
    data_all = list()

    for k, g in df.groupby('route_dt'):
        g_ = g[nodes]
        g_ = g_.melt(var_name='node_name', value_name='node_code')
        g_ = g_[g_['node_code'] != '021F103']  # 退货组
        df_res = g_['node_code'].value_counts().nlargest(10).to_frame(name='count')
        df_res.reset_index(inplace=True)
        df_res = pandas.merge(df_res, node_addr_df, left_on='index', right_on='node_code', how='left')
        df_res.drop_duplicates(subset=['index'], keep='first', inplace=True)
        df_res.sort_values(by='count', ascending=True, inplace=True)
        # df_res['weight'] = df_res['count'] / df_res['count'].max()
        df_res['weight'] = range(1, 1 + df_res.shape[0])
        df_res['weight'] = df_res['weight'] / df_res.shape[0]
        data = df_res[['lat', 'lng', 'weight']].values.tolist()
        data_all.append(data)

        df_res.apply(lambda x: util.plotDotforDataframe(x, map), axis=1)

    gradient = {.2: "blue", .4: "cyan", .6: "lime", .8: "yellow", 1: "red"}
    hm = plugins.HeatMapWithTime(data_all, radius=50, position='topleft', gradient=gradient,
                                 display_index=True, index=list(df['route_dt'].unique()))
    hm.add_to(map)

    map.save('htmls/heatmap_routes_distribution_over_months.html')
    exit(0)


def RoutingCount(ware_dfg, df):
    df['routes_count'] = df.apply(lambda x: countRoutes(x), axis=1)
    for k, df_dis in ware_dfg:
        df_dis_waybill = pandas.merge(df_dis, df, left_on='store_name_c', right_on=['start_node_name'], how='left')

        df_dis_waybill['route_dt'] = df_dis_waybill['start_opt_tm'].dt.strftime('%m-%d')
        df_dis_waybill.drop_duplicates(inplace=True)

        df_dis_waybill['avg_routes'] = (
            df_dis_waybill['routes_count'].groupby(df_dis_waybill['route_dt']).transform('mean'))

        df_dis_waybill_res = df_dis_waybill[['avg_routes', 'route_dt']]
        df_dis_waybill_res.drop_duplicates(inplace=True)
        df_dis_waybill_res.sort_values(by='route_dt', inplace=True)

        from matplotlib import pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))
        import seaborn as sns
        ax = sns.barplot(data=df_dis_waybill_res, x="route_dt", y="avg_routes")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)
        ax.set_xlabel('订单日期')
        ax.set_ylabel('路由个数')
        ax.set_title(f'{delevelize(k)}订单的分拨中心路由平均个数')
        s1 = 200 / plt.gcf().dpi * 10
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig(f'pngs/分拨中心/路由个数/{k}_路由个数分析.png')
        plt.show()
    pass


def TimingAnalysis(ware_dfg, df, info, attr1, attr2):
    for k, df_dis in ware_dfg:
        print(k)
        df_dis_waybill = pandas.merge(df_dis, df, left_on='store_name_c', right_on=['start_node_name'], how='left')
        df_dis_waybill['delay_seconds'] = df_dis_waybill.apply(
            lambda x: (x[attr2] - x[attr1]).total_seconds(), axis=1)

        df_dis_waybill['delay_days'] = df_dis_waybill.apply(
            lambda x: toHours(x['delay_seconds']), axis=1)

        df_dis_waybill[attr2] = df_dis_waybill[attr2].dt.strftime('%m-%d')
        df_dis_waybill.drop_duplicates(inplace=True)
        # 删除异常值
        df_dis_waybill = remove_outliers(df_dis_waybill, 'delay_days', attr2)

        df_dis_waybill['avg_delay_days'] = (
            df_dis_waybill['delay_days'].groupby(df_dis_waybill[attr2]).transform('mean'))

        df_dis_waybill_res = df_dis_waybill[['avg_delay_days', attr2]]
        df_dis_waybill_res.drop_duplicates(inplace=True)
        df_dis_waybill_res.sort_values(by=attr2, inplace=True)

        from matplotlib import pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))
        import seaborn as sns
        ax = sns.barplot(data=df_dis_waybill_res, x=attr2, y="avg_delay_days")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)
        ax.set_xlabel('日期')
        ax.set_ylabel('时间')
        ax.set_title(f'{delevelize(k)}仓库运单时效性分析({info})')
        s1 = 200 / plt.gcf().dpi * 10
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig(f'pngs/{info}/v3/{k}_时效分析.png')
        plt.show()
    pass


def unsent(x, dt1, dt2):
    if x[dt1].strftime("%m%d") == x[dt2].strftime("%m%d"):
        unsent = 0
    else:
        unsent = 1
    return unsent


def cal_timing(df, attr, dt1, dt2):
    col1 = attr + '_seconds'
    col2 = attr + '_days'
    # col4 = attr + '_unsent'
    col5 = 'avg_' + attr + '_days'
    # col7 = 'sum_' + attr + '_unsent'
    df.dropna(subset=[dt1], inplace=True)
    df.dropna(subset=[dt2], inplace=True)

    df[col1] = df.apply(
        lambda x: (x[dt2] - x[dt1]).total_seconds(), axis=1)
    # df[col4] = df.apply(
    #     lambda x: unsent(x, dt1, dt2), axis=1)
    df[col2] = df.apply(
        lambda x: toHours(x[col1]), axis=1)

    df['dt'] = df[dt2].dt.strftime('%m-%d')
    df.drop_duplicates(inplace=True)
    df = remove_outliers(df, col2, 'dt')

    df[col5] = (
        df[col2].groupby(df['dt']).transform('mean'))
    # df[col7] = (
    #     df[col4].groupby(df['dt']).transform('sum'))
    df = df[['dt', col5]]
    # df = df[['dt', col5, col7]]
    df.drop_duplicates(inplace=True)
    return col5, df


def cal_Quantity(df, attr, dt1, dt2):
    df[dt2] = df[dt2].dt.strftime('%m-%d')
    df.drop_duplicates(inplace=True)

    return df


def TimingStackedAnalysis(df, info):
    # 上海苏州
    # df['start_opt_dt'] = df['start_opt_tm'].apply(
    #     lambda x: x.replace(hour=0, minute=0, second=0))
    # df = df[
    #     (df['start_opt_dt'] < datetime.datetime(2022, 7, 1)) & (df['start_opt_dt'] >= datetime.datetime(2022, 3, 1))]
    # col_opt, df_warehouse_opt = cal_timing(df, 'warehouse', 'route_start_node_real_arv_tm',
    #                                        'route_start_node_real_send_tm')
    # col_start_center_in_out, df_start_center_in_out = cal_timing(df, 'start_center_in_out',
    #                                                              'start_sorting_real_insp_tm',
    #                                                              'start_sorting_real_send_tm')
    # col_end_center_in_out, df_end_center_in_out = cal_timing(df, 'end_center_in_out',
    #                                                          'end_sorting_real_arv_tm',
    #                                                          'end_sorting_real_ship_tm')
    # col_site_delv, df_site_delv = cal_timing(df, 'site_delv',
    #                                          'end_sorting_real_ship_tm',
    #                                          'real_delv_tm')
    # df_res = pandas.merge(df_warehouse_opt, df_start_center_in_out, on='dt', how='outer')
    # df_res = pandas.merge(df_res, df_end_center_in_out, on='dt', how='outer')
    # df_res = pandas.merge(df_res, df_site_delv, on='dt', how='outer')
    # df_res.dropna(inplace=True)
    # df_res.to_csv(f'csvs/{info}four_stages_timing.csv', index=False)
    df_res = pandas.read_csv(
        f'csvs/{info}four_stages_timing.csv', engine='python',
        skip_blank_lines=True)
    df_res = df_res[
        ['dt', 'avg_warehouse_days', 'avg_start_center_in_out_days', 'avg_end_center_in_out_days',
         'avg_site_delv_days']]
    # df_res = df_res[
    #     ['dt', col_opt, col_start_center_in_out, col_end_center_in_out, col_site_delv]]
    df_res.drop_duplicates(inplace=True)
    df_res.sort_values(by='dt', inplace=True)
    from matplotlib import pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    ax = df_res.set_index('dt').plot(kind='bar', stacked=True,
                                     color=['#D98880', '#7DCEA0', '#F19F6A', '#7EA1E1', '#6ECAD0', '#90909F'])
    ax.xaxis.set_major_locator(MultipleLocator(15))
    ax.grid(True)  # 显示网格
    ax.set_xlabel('日期')
    ax.set_ylabel('天数')
    ax.set_ylim(0, 20)
    ax.legend(labels=['出仓', '始分拣中心', '末分拣中心', '入站'])
    ax.tick_params(axis='x', labelrotation=0)
    ax.set_title(f'{info}仓库各阶段耗时分析')

    plt.savefig(f'pngs/全阶段/{info}_timing.png')
    plt.show()
    pass


def TimingSidedAnalysis(ware_dfg, df):
    for k, df_dis in ware_dfg:
        df_dis_waybill = pandas.merge(df_dis, df, left_on='store_name_c', right_on=['start_node_name'], how='left')
        col_warehouse, df_warehouse = cal_timing(df_dis_waybill, 'warehouse', 'route_start_node_real_arv_tm',
                                                 'route_start_node_real_send_tm')
        col_ware_center, df_ware_center = cal_timing(df_dis_waybill, 'ware_center', 'route_start_node_real_send_tm',
                                                     'start_sorting_real_insp_tm')
        col_start_center_in_out, df_start_center_in_out = cal_timing(df_dis_waybill, 'start_center_in_out',
                                                                     'start_sorting_real_insp_tm',
                                                                     'start_sorting_real_send_tm')
        col_start_center_out_end_in, df_start_center_out_end_in = cal_timing(df_dis_waybill, 'start_center_out_end_in',
                                                                             'start_sorting_real_send_tm',
                                                                             'end_sorting_real_arv_tm')
        col_end_center_in_out, df_end_center_in_out = cal_timing(df_dis_waybill, 'end_center_in_out',
                                                                 'end_sorting_real_arv_tm',
                                                                 'end_sorting_real_send_tm')
        col_site_delv, df_site_delv = cal_timing(df_dis_waybill, 'site_delv',
                                                 'end_sorting_real_ship_tm',
                                                 'real_delv_tm')

        col_start_center_vehicle, df_start_center_vehicle = cal_timing(df_dis_waybill, 'start_center_vehicle',
                                                                       'start_sorting_real_ship_tm',
                                                                       'start_sorting_real_send_tm')
        col_end_center_vehicle, df_end_center_vehicle = cal_timing(df_dis_waybill, 'end_center_vehicle',
                                                                   'end_sorting_real_ship_tm',
                                                                   'end_sorting_real_send_tm')

        df_res = pandas.merge(df_warehouse, df_ware_center, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_start_center_in_out, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_start_center_out_end_in, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_end_center_in_out, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_site_delv, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_end_center_vehicle, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_start_center_vehicle, on='dt', how='outer')

        df_res.drop_duplicates(inplace=True)
        df_res.sort_values(by='dt', inplace=True)
        df_res.to_csv(f'csvs/{k}df_timing_unsent.csv', index=False)
    pass


def drawSided():
    from matplotlib import pyplot as plt
    for k in range(1, 5):
        df = pandas.read_csv(
            f'csvs/{k}df_timing_unsent.csv',
            engine='python', skip_blank_lines=True)
        df.fillna(0, inplace=True)
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        df['dt'] = df.apply(lambda x: datetime.datetime.strptime(x['dt'], "%m-%d"), axis=1)
        df['dt'] = df['dt'].apply(lambda x: x.replace(year=2022))

        # 运输方面
        # df = df[['dt', 'avg_ware_center_days', 'avg_start_center_out_end_in_days', 'avg_site_delv_days']]
        # 仓库处理方面
        # df = df[['dt', 'avg_warehouse_days', 'avg_start_center_in_out_days', 'avg_end_center_in_out_days']]
        # 运力方面
        # df = df[['dt', 'avg_start_center_vehicle_days', 'avg_end_center_vehicle_days']]
        # 单量
        df = df[['dt', 'sum_warehouse_unsent', 'sum_start_center_in_out_unsent', 'sum_end_center_in_out_unsent']]
        # 1,2,7,8常规场景
        df_covid = df[(df['dt'] < datetime.datetime(2022, 7, 1)) & (df['dt'] >= datetime.datetime(2022, 3, 1))]
        df_normal = df[(df['dt'] < datetime.datetime(2022, 3, 1)) | (df['dt'] >= datetime.datetime(2022, 7, 1))]
        df_covid.sort_values(by='dt', inplace=True, ascending=True)
        df_covid['dt'] = df_covid['dt'].dt.strftime('%m-%d')
        df_normal['dt'] = df_normal['dt'].dt.strftime('%m-%d')
        l1 = df_covid.shape[0]
        l2 = df_normal.shape[0]
        if l1 < l2:
            df_normal = df_normal[:l1 - l2]
        else:
            df_covid = df_covid[l1 - l2:]
        df_normal['dt'] = list(df_covid['dt'])
        # df_normal = df_normal.melt(id_vars=['dt'], var_name='type', value_name='avg_days')
        # df_covid = df_covid.melt(id_vars=['dt'], var_name='type', value_name='avg_days')

        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 10), sharey=True,
                                       gridspec_kw={'wspace': 0, 'width_ratios': [1, 2]})
        df_covid.plot(x='dt', kind='barh', ax=ax2, color=['#52BE80', '#C39BD3', '#F7DC6F'], stacked=True)
        ax2.tick_params(labelright=False, right=False)
        ax2.set_ylabel('')
        ax2.set_xlabel('疫情场景')
        ax2.tick_params(width=0, length=0)
        # plt.title(f'{delevelize(k)} 订单耗时天数（均值）分析')
        # plt.title(f'{delevelize(k)} 各阶段处理时间分析')
        # plt.title(f'{delevelize(k)} 发货-封车分析')
        plt.title(f'{delevelize(k)} 当天未处理单量分析')
        # draw juvenile subplot at the left
        df_normal.plot(x='dt', kind='barh', ax=ax1, color=['#52BE80', '#C39BD3', '#F7DC6F'], stacked=True)
        l1, lb1 = ax1.get_legend_handles_labels()
        l2, lb2 = ax2.get_legend_handles_labels()
        # ax2.legend(l1 + l2, ['仓库-分拣中心', '始末分拣中心', '末分拣中心-妥投'], loc='upper right')
        # ax2.legend(l1 + l2, ['仓库', '始分拣中心', '末分拣中心'], loc='upper right')
        ax2.legend(l1 + l2, ['仓库', '始分拣中心', '末分拣中心'], loc='upper right')
        xmax = max(ax1.get_xlim()[1], ax2.get_xlim()[1])
        ax1.set_xlim(xmax=xmax)
        ax2.set_xlim(xmax=xmax)
        ax1.set_ylabel('日期')
        ax1.yaxis.set_major_locator(MultipleLocator(7))
        ax1.set_xlabel('常规场景')
        ax1.tick_params(axis='y', labelleft=True, left=True)
        ax1.invert_xaxis()  # reverse the direction
        ax1.legend_.remove()  # remove the legend; the legend will be in ax1
        plt.tight_layout()
        # plt.savefig(f'pngs/全阶段/timing_dealing_{k}_v2.png')
        # plt.savefig(f'pngs/全阶段/timing_vehicle_{k}_v2.png')
        plt.savefig(f'pngs/全阶段/unsent_{k}_v2.png')
        plt.show()


def merge():
    dt_ls = ['plan_delv_dt', 'start_opt_tm', 'plan_delv_tm', 'real_delv_tm', 'route_start_node_real_arv_tm',
             'route_start_node_real_send_tm', 'start_sorting_real_insp_tm', 'start_sorting_real_send_tm',
             'start_sorting_real_ship_tm', 'end_sorting_real_arv_tm', 'end_sorting_real_ship_tm',
             'end_sorting_real_send_tm', 'end_node_insp_tm']
    df = pandas.read_csv(
        'csvs/all_waybills_timing.csv',
        parse_dates=dt_ls,
        engine='python', skip_blank_lines=True)
    print(df.shape[0])


def centerAnaysis():
    pass


def draw():
    from matplotlib import pyplot as plt
    for k in range(1, 5):
        df = pandas.read_csv(
            f'csvs/{k}df_timing_unsent.csv',
            engine='python', skip_blank_lines=True)
        df.fillna(0, inplace=True)
        df['dt'] = df.apply(lambda x: datetime.datetime.strptime(x['dt'], "%m-%d"), axis=1)
        df['dt'] = df['dt'].apply(lambda x: x.replace(year=2022))
        df['dt'] = df['dt'].dt.strftime('%m-%d')
        df.sort_values(by='dt', inplace=True)
        # 运输方面
        # df = df[['dt', 'avg_ware_center_days', 'avg_start_center_out_end_in_days', 'avg_site_delv_days']]
        # 仓库处理方面
        # df = df[['dt', 'avg_warehouse_days', 'avg_start_center_in_out_days', 'avg_end_center_in_out_days']]
        # 运力方面
        # df = df[['dt', 'avg_start_center_vehicle_days', 'avg_end_center_vehicle_days']]
        # 单量
        df = df[['dt', 'sum_warehouse_unsent', 'sum_start_center_in_out_unsent', 'sum_end_center_in_out_unsent']]
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))

        ax = df.set_index('dt').plot(kind='bar', stacked=True,
                                     color=['#52BE80', '#C39BD3', '#F7DC6F'])
        # color=['#D98880', '#7DCEA0', '#F19F6A', '#7EA1E1', '#6ECAD0', '#90909F'])
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('日期')
        ax.set_ylabel('单量')

        # ax.legend(labels=['仓库-始分拨中心', '始末分拣中心', '末分拣中心-妥投'])
        # ax.legend(labels=['仓库', '始分拣中心', '末分拣中心'])
        # ax.legend(labels=['始分拣中心', '末分拣中心'])
        ax.legend(labels=['仓库', '始分拣中心', '末分拣中心'])
        ax.tick_params(axis='x', labelrotation=0)
        ax.set_title('{km}订单各阶段单量分析'.format(km=delevelize(k)))

        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        # plt.savefig('pngs/全阶段/horizontal/{km}_timing_transport_v2.png'.format(km=k))
        # plt.savefig('pngs/全阶段/horizontal/{km}_timing_dealing_v2.png'.format(km=k))
        plt.savefig('pngs/全阶段/horizontal/{km}_unsent_v2.png'.format(km=k))
        plt.show()


def raw_data():
    df = pandas.read_csv(
        'csvs/temp_raw_route_data.csv',
        engine='python',
        skip_blank_lines=True)
    # df.apply(lambda x: countSorting(x), axis=1)
    seq_data = pandas.DataFrame(columns=['dt', 'no', 'name', 'in', 'out', 'type'])
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        if type(row['recommended_routing']) != str:
            continue
        ls = row['recommended_routing'].split('->')
        seqth = ['second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
        first_poor_boy = True
        dt_in = None
        dt_out = None
        for idx, name in (enumerate(ls)):
            node_name = name.split('_')[-1]
            if idx == 0:
                data_in = {'name': node_name, 'type': 0, 'dt': row['start_opt_tm'], 'in': 1}
                data_out = {'name': node_name, 'type': 0, 'dt': row['route_start_node_real_send_tm'], 'out': 1}
                seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
                seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_out])])
                continue
            if '接货仓' in name:
                continue
            if idx == len(ls) - 1:  # 营业站
                data_in = {'name': node_name, 'type': 2, 'dt': row['real_delv_tm'], 'out': 1, 'no': row['end_node_id']}
                seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
                continue
            # 分拣中心们
            sorting_code = name.split('_')[1]
            data_in = {'no': sorting_code, 'name': node_name, 'type': 1}
            data_out = {'no': sorting_code, 'name': node_name, 'type': 1}
            if row['end_sorting_name'] == node_name:  # 如果末节点是该分拣中心
                dt_in = row['end_sorting_real_arv_tm']
                dt_out = row['end_sorting_real_send_tm']
            elif first_poor_boy and row['first_sorting_real_arv_node'] == sorting_code or pandas.isna(
                    row['first_sorting_real_arv_node']):
                if row['second_sorting_real_arv_node'] != sorting_code:
                    # 第一个没有出入货时间信息
                    first_poor_boy = False
                    dt_in = row['start_sorting_real_send_tm']
                    dt_out = row['second_sorting_real_arv_tm']
            else:
                for i in seqth:
                    if row[f'{i}_sorting_real_arv_node'] == sorting_code:
                        dt_in = row[f'{i}_sorting_real_arv_tm']
                        dt_out = row[f'{i}_sorting_real_send_tm']
                        break
            data_in['dt'] = dt_in
            data_in['in'] = 1
            data_out['dt'] = dt_out
            data_out['out'] = 1
            seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
            seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_out])])
    seq_data.to_csv('csvs/seq_of_nodes_v1.csv', index=False)
    exit(0)
    # def rename_store(x):
    #     for idx, name in enumerate(old_names):
    #         if name == x:
    #             print(x, new_names[idx])
    #             return new_names[idx]
    #     return x

    # df['start_node_name'] = df['start_node_name'].apply(lambda x: rename_store(x))
    # df.drop(['reject_reason_name', 'start_node_id', 'end_node_name', 'end_area_name', 'route_type', 'plan_delv_tm'],
    #         axis=1,
    #         inplace=True)
    # df.to_csv('csvs/temp_raw_route_data.csv', index=False)

    exit(0)


def analyse():
    raw_data()
    dt_ls = ['plan_delv_dt', 'start_opt_tm', 'plan_delv_tm', 'real_delv_tm', 'route_start_node_real_arv_tm',
             'route_start_node_real_send_tm', 'start_sorting_real_insp_tm', 'start_sorting_real_send_tm',
             'start_sorting_real_ship_tm', 'end_sorting_real_arv_tm', 'end_sorting_real_ship_tm',
             'end_sorting_real_send_tm']
    df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/全阶段/所有订单数据.csv',
        parse_dates=dt_ls,
        engine='python', skip_blank_lines=True)
    # for i in dt_ls:
    #     df.dropna(subset=[i], inplace=True)
    route_distribution_meta_path_check(df)
    # Routing(df)
    address_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    # city_df = pandas.read_csv(
    #     DISK_PATH_MACHINE + '数据/仓_gps_营业部_polygon_/城市到上海距离.csv', engine='python',
    #     skip_blank_lines=True)
    warehouse_df = df.drop_duplicates(subset=['start_node_name'])
    warehouse_df = warehouse_df[['start_node_name']]  # all warehouses in table
    warehouse_df = pandas.merge(address_df, warehouse_df, left_on='store_name_c', right_on=['start_node_name'],
                                how='right')
    warehouse_df.dropna(inplace=True, subset=['city'])
    warehouse_df_ss = warehouse_df[warehouse_df['city'].isin(['上海市', '苏州市'])]
    warehouse_df_nss = warehouse_df[~warehouse_df['city'].isin(['上海市', '苏州市'])]
    warehouse_df_nss = warehouse_df_nss[['city', 'start_node_name']].drop_duplicates()
    warehouse_df_ss = warehouse_df_ss[['city', 'start_node_name']].drop_duplicates()

    df_covid = pandas.merge(df, warehouse_df_ss, how='left', on='start_node_name').dropna(subset=['city'])
    df_safe = pandas.merge(df, warehouse_df_nss, how='left', on='start_node_name').dropna(subset=['city'])

    TimingStackedAnalysis(df_covid, '上海-苏州')
    TimingStackedAnalysis(df_safe, '其他城市')
    exit(0)
    # warehouse_df = pandas.merge(city_df, warehouse_df, on=['city'], how='right')
    # warehouse_df['distance_level'] = warehouse_df.apply(lambda x: levelize(x), axis=1)
    # ware_dfg = warehouse_df.groupby('distance_level')
    # OutOfTime(ware_dfg, df)
    # TimingAnalysis(ware_dfg, df, '入仓-出仓', 'route_start_node_real_arv_tm', 'route_start_node_real_send_tm')
    # TimingStackedAnalysis(ware_dfg, df)
    # RoutingCount(ware_dfg, df)

    # TimingSidedAnalysis(ware_dfg, df)

    # 已经保存的预处理
    # df.drop(['Unnamed: 0', 'waybill_type'], inplace=True, axis=1)
    # for c in df.columns:
    #     if df[c].isnull().all():
    #         df.drop(c, inplace=True, axis=1)
    # df.fillna('', inplace=True)

    # df['second'] = df.apply(
    #     lambda x: str(x['second_sorting_real_arv_node']) + x['second_sorting_name'], axis=1)
    # df['third'] = df.apply(
    #     lambda x: str(x['third_sorting_real_arv_node']) + x['third_sorting_name'], axis=1)
    # df['fourth'] = df.apply(
    #     lambda x: str(x['fourth_sorting_real_arv_node']) + x['fourth_sorting_name'], axis=1)
    # df['fifth'] = df.apply(
    #     lambda x: str(x['fifth_sorting_real_arv_node']) + x['fifth_sorting_name'], axis=1)
    # df['sixth'] = df.apply(
    #     lambda x: str(x['sixth_sorting_real_arv_node']) + x['sixth_sorting_name'], axis=1)
    # df['seventh'] = df.apply(
    #     lambda x: str(x['seventh_sorting_real_arv_node']) + x['seventh_sorting_name'], axis=1)
    # unqiues = pandas.unique(
    #     df[['second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']].values.ravel('K'))
    # names = df['end_sorting_name'].unique()
    # df_u = pandas.DataFrame(names)
    # df_u.to_csv('names.csv', index=False)
    # exit(0)


def splitRoutes(df):
    df_res = pandas.DataFrame()
    for i, x in df.iterrows():
        routes = x.recommended_routing.split('->')
        if not '王桥' in routes[-1]:
            continue
        data = {}
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
                data[col] = pairs[1]
                k += 1
                if '王桥' in pairs[2]:
                    break
                if '021F008' == pairs[1]:
                    break
        df_res = df_res.append([data], ignore_index=False)

    return df_res


def routesPairs(df):
    rts = df.columns
    df_ = pandas.DataFrame()
    for i, r in df.iterrows():
        path = {}
        flag = True
        lastCol = None
        for col in rts:
            if col == 'warehouse':
                continue
            if pandas.notna(r[col]):
                if flag:
                    path['route_a'] = r['warehouse']
                    path['route_b'] = r[col]
                    lastCol = col
                    flag = False
                    df_ = df_.append([path], ignore_index=True)
                else:
                    path['route_a'] = r[lastCol]
                    path['route_b'] = r[col]
                    lastCol = col
                    df_ = df_.append([path], ignore_index=True)
            else:
                break
        pass
    df_.drop_duplicates(inplace=True)
    return df_


m = folium.Map(location=[31.3004, 121.294], zoom_start=6,
               attr='疫情物流路由', )


def plotDotforDataframe(x):
    ls = ['四川省', '广东省', '北京省', '湖南省', '湖北省', '天津省']
    if x.province in ls:
        c = 'yellow'
    else:
        c = 'green'
    folium.CircleMarker(location=[x.lat, x.lng],
                        radius=1, fillOpacity=0.5, color=c,
                        weight=4).add_to(m)


def plotLine(x):
    loc = [(x.lat_a, x.lng_a), (x.lat_b, x.lng_b)]
    if x['flag'] == 1:
        color = '#EC5F36'
        opacty = 0.7
        wt = 3
    else:
        color = 'blue'
        opacty = 0.5
        wt = 1.5
    folium.PolyLine(loc,
                    color=color,
                    weight=wt,
                    opacity=opacty).add_to(m)
    folium.CircleMarker(location=[x.lat_a, x.lng_a],
                        radius=1, fillOpacity=0.5, color='yellow',
                        weight=4).add_to(m)
    folium.CircleMarker(location=[x.lat_b, x.lng_b],
                        radius=1, fillOpacity=0.5, color='green',
                        weight=4).add_to(m)
    pass


# seq_data = pandas.DataFrame(columns=['dt', 'no', 'name', 'in', 'out', 'type'])


def seq_data_agg():
    df = pandas.read_csv(
        'csvs/seq_of_nodes_v1.csv',
        engine='python', date_parser='dt',
        skip_blank_lines=True)
    df.groupby(['dt', 'name'])['Number'].sum()
    pass


# 获得序列特征
def countSorting(row):
    global seq_data
    if type(row['recommended_routing']) != str:
        return
    ls = row['recommended_routing'].split('->')
    seqth = ['second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
    first_poor_boy = True
    dt_in = None
    dt_out = None
    for idx, name in (enumerate(ls)):
        node_name = name.split('_')[-1]
        if idx == 0:
            data_in = {'name': node_name, 'type': 0, 'dt': row['start_opt_tm'], 'in': 1}
            data_out = {'name': node_name, 'type': 0, 'dt': row['route_start_node_real_send_tm'], 'out': 1}
            seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
            seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_out])])
            continue
        if '接货仓' in name:
            sorting_idx = 1
            continue
        if idx == len(ls) - 1:  # 营业站
            data_in = {'name': node_name, 'type': 2, 'dt': row['real_delv_tm'], 'out': 1, 'no': row['end_node_id']}
            seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
            continue
        # 分拣中心们
        sorting_code = name.split('_')[1]
        data_in = {'no': sorting_code, 'name': node_name, 'type': 1}
        data_out = {'no': sorting_code, 'name': node_name, 'type': 1}
        if row['end_sorting_name'] == node_name:  # 如果末节点是该分拣中心
            dt_in = row['end_sorting_real_arv_tm']
            dt_out = row['end_sorting_real_send_tm']
        elif first_poor_boy and row['first_sorting_real_arv_node'] == sorting_code or pandas.isna(
                row['first_sorting_real_arv_node']):
            if row['second_sorting_real_arv_node'] != sorting_code:
                # 第一个没有出入货时间信息
                first_poor_boy = False
                dt_in = row['start_sorting_real_send_tm']
                dt_out = row['second_sorting_real_arv_tm']
        else:
            for i in seqth:
                if row[f'{i}_sorting_real_arv_node'] == sorting_code:
                    dt_in = row[f'{i}_sorting_real_arv_tm']
                    dt_out = row[f'{i}_sorting_real_send_tm']
                    break
        data_in['dt'] = dt_in
        data_in['in'] = 1
        data_out['dt'] = dt_out
        data_out['out'] = 1
        seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_in])])
        seq_data = pandas.concat([seq_data, pandas.DataFrame.from_records([data_out])])
    pass


def route_distribution_draw():
    df_normal = pandas.read_csv(
        'temp_routes_pair_normal.csv', engine='python',
        skip_blank_lines=True)
    df_covid = pandas.read_csv(
        'temp_routes_pair_covid.csv', engine='python',
        skip_blank_lines=True)

    df_covid_new = pandas.concat([df_covid, df_normal, df_normal]).drop_duplicates(keep=False)
    center_addr_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/全阶段/分拣中心addr.csv', engine='python',
        skip_blank_lines=True)
    center_addr_df['province_name'] = center_addr_df['province_name'].apply(lambda x: x + '省')
    ware_addr_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    pro_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/公开数据/省份-省会城市gps.csv', engine='python',
        skip_blank_lines=True)
    center_addr_df = center_addr_df[['node_code', 'province_name']].drop_duplicates().dropna()
    ware_addr_df = ware_addr_df[['store_name_c', 'province']].drop_duplicates().dropna()

    df_normal = pandas.merge(df_normal, center_addr_df, left_on='route_a', right_on='node_code', how='left')
    df_normal = pandas.merge(df_normal, ware_addr_df, left_on='route_a', right_on='store_name_c', how='left')
    df_normal['province_a'] = df_normal.apply(
        lambda x: x['province'] if pandas.isna(x['province_name']) else x['province_name'], axis=1)
    df_normal = df_normal[['route_b', 'province_a']].dropna()

    df_normal = pandas.merge(df_normal, center_addr_df, left_on='route_b', right_on='node_code', how='left').dropna()
    df_normal = df_normal[['province_a', 'province_name']].drop_duplicates().dropna()

    df_covid_new = pandas.merge(df_covid_new, center_addr_df, left_on='route_a', right_on='node_code', how='left')
    df_covid_new = pandas.merge(df_covid_new, ware_addr_df, left_on='route_a', right_on='store_name_c', how='left')
    df_covid_new['province_a'] = df_covid_new.apply(
        lambda x: x['province'] if pandas.isna(x['province_name']) else x['province_name'], axis=1)
    df_covid_new = df_covid_new[['route_b', 'province_a']].dropna()

    df_covid_new = pandas.merge(df_covid_new, center_addr_df, left_on='route_b', right_on='node_code',
                                how='left').dropna()
    df_covid_new = df_covid_new[['province_a', 'province_name']].drop_duplicates().dropna()
    df_covid_new = pandas.concat([df_covid_new, df_normal, df_normal]).drop_duplicates(keep=False)
    df_covid_new = df_covid_new[~df_covid_new['province_name'].isin(['内蒙古自治区', '甘肃省'])]
    df_normal = df_normal[~df_normal['province_name'].isin(['内蒙古自治区', '甘肃省'])]
    df_covid_new = df_covid_new[
        ~df_covid_new['province_a'].isin(['内蒙古自治区', '甘肃省'])]
    df_normal = df_normal[
        ~df_normal['province_a'].isin(['内蒙古自治区', '甘肃省'])]

    df_normal = pandas.merge(df_normal, pro_df, left_on='province_a', right_on='province', how='left').dropna()
    df_normal = df_normal.rename(columns={'lng': 'lng_a', 'lat': 'lat_a'})
    df_normal = pandas.merge(df_normal, pro_df, left_on='province_name', right_on='province', how='left').dropna()
    df_normal = df_normal.rename(columns={'lng': 'lng_b', 'lat': 'lat_b'})

    df_covid_new = pandas.merge(df_covid_new, pro_df, left_on='province_a', right_on='province', how='left').dropna()
    df_covid_new = df_covid_new.rename(columns={'lng': 'lng_a', 'lat': 'lat_a'})
    df_covid_new = pandas.merge(df_covid_new, pro_df, left_on='province_name', right_on='province', how='left').dropna()
    df_covid_new = df_covid_new.rename(columns={'lng': 'lng_b', 'lat': 'lat_b'})

    df_covid_new['flag'] = 1
    df_normal['flag'] = 0
    df = pandas.concat([df_normal, df_covid_new])
    df.apply(plotLine, axis=1)
    m.save('htmls/routes_distribution_province_level.html')
    # m = folium.Map(location=[31.3004, 121.294], zoom_start=6,
    #                attr='疫情物流路由', )
    # df_normal.apply(plotLine, axis=1)
    # m.save('htmls/routes_distribution_province_level_common.html')
    exit(0)


def countPaths(x):
    ls = x.split('->')
    if '接货仓' in x:
        return len(ls) - 1
    return len(ls)


# 只留分拣中心
def interPath(x):
    ls = x.split('->')
    res = ''
    for idx, name in enumerate(ls):
        if idx == 0:  # 不要仓
            continue
        if '接货仓' in name:
            continue
        if idx == len(ls) - 1:  # 不要站
            continue
        res = res + name + '->'
    return res


def route_distribution_meta_path_check(df):
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.dropna(subset=['recommended_routing'], inplace=True)
    df.dropna(subset=['start_opt_tm'], inplace=True)
    df['start_opt_tm'] = df['start_opt_tm'].apply(
        lambda x: x.replace(hour=0, minute=0, second=0))
    date_list = pandas.date_range(start=df['start_opt_tm'].min(), end=df['start_opt_tm'].max()).to_pydatetime().tolist()
    dates_interval = list(util.chunks(date_list, 14))
    df_after_group = pandas.DataFrame()
    for idx, interval in enumerate(dates_interval):
        df_ = df[(df['start_opt_tm'].isin(interval))]
        # 检查中间路由占比
        df_.drop_duplicates(subset=['recommended_routing'], inplace=True)
        df_['resigned_routes'] = df_['recommended_routing'].apply(lambda x: interPath(x))
        res = df_['resigned_routes'].value_counts(ascending=True)

        total = df_.shape[0]
        series_cdf(res, attr='resigned_routes',
                   title=f'中间路由占比cdf图{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}-total({total})')

        # res.plot.pie(autopct='%.2f')
        # plt.title(f'inter_path{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}-total({total})')
        # plt.savefig(f'pngs/pies/中间路由占比{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}.png')
        # plt.show()
        # 检查元路径长度
        # df_.drop_duplicates(subset=['recommended_routing'], inplace=True)
        # df_['length'] = df_['recommended_routing'].apply(lambda x: countPaths(x))
        # res = df_['length'].value_counts(ascending=True)
        # total = df_.shape[0]
        # res.plot.pie(autopct='%.2f')
        # plt.title(f'length_percentage{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}-total({total})')
        # plt.savefig(f'pngs/pies/元路径个数占比{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}.png')
        # plt.show()

        # 检查仓的重复性1
        # df_.drop_duplicates(subset=['recommended_routing'], inplace=True)
        # res = df_['start_node_name'].value_counts()
        # series_cdf(res, attr='start_node_name',
        #            title=f'仓库重复的cdf图{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}')
        # 检查仓的重复性2
        # df_['group'] = f'{interval[0].strftime("%m%d")}{interval[-1].strftime("%m%d")}'
        # df_after_group = pandas.concat([df_after_group, df_], ignore_index=True)  # 每个csv都concat起来
        # 检查路径的数量
        # df_['group'] = f'{interval[0].strftime("%m%d")}{interval[-1].strftime("%m%d")}'
        # df_after_group = pandas.concat([df_after_group, df_], ignore_index=True)  # 每个csv都concat起来
        # 检查路径重复的次数的cdf图
        # res = df_['recommended_routing'].value_counts()
        # series_cdf(res, attr='recommended_routing',
        #            title=f'路径数量cdf图{interval[0].strftime("%Y%m%d")}-{interval[-1].strftime("%Y%m%d")}')
    # plt.figure(figsize=(12, 12))
    # df_after_group.groupby('group')['start_node_name'].nunique().plot(kind='bar')
    # plt.title('warehouse_unique_count_each_14_days')
    # plt.savefig('pngs/仓库重复情况.png')
    # plt.show()

    exit(0)


def route_distribution(df):
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.dropna(subset=['recommended_routing'], inplace=True)
    df.dropna(subset=['start_opt_tm'], inplace=True)
    df['start_opt_tm'] = df['start_opt_tm'].apply(
        lambda x: x.replace(hour=0, minute=0, second=0))

    df_covid = df[(df['start_opt_tm'] < datetime.datetime(2022, 7, 1)) & (
            df['start_opt_tm'] >= datetime.datetime(2022, 3, 1))]
    df_normal = df[(df['start_opt_tm'] < datetime.datetime(2022, 3, 1)) | (
            df['start_opt_tm'] >= datetime.datetime(2022, 7, 1))]

    df_covid = df_covid[['recommended_routing']].drop_duplicates()
    df_normal = df_normal[['recommended_routing']].drop_duplicates()
    df_covid_routes = splitRoutes(df_covid).drop_duplicates()
    df_normal_routes = splitRoutes(df_normal).drop_duplicates()
    df_covid_routes_pairs = routesPairs(df_covid_routes)
    df_normal_routes_pairs = routesPairs(df_normal_routes)

    df_normal_routes_pairs.to_csv('temp_routes_pair_normal.csv', index=False)
    df_covid_routes_pairs.to_csv('temp_routes_pair_covid.csv', index=False)
    exit(0)


def filter_warehouses(df):
    warehouse_df_all = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/warehouse_features_v3.csv',
        engine='python',
        skip_blank_lines=True)
    df = df[df['start_node_name'].isin(warehouse_df_all['store_name_c'].tolist())]
    return df


def filter_sites(df):
    site_df_all = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/site_features_covid.csv',
        engine='python',
        skip_blank_lines=True)
    df = df[df['end_node_name'].isin(site_df_all['node_name'].tolist())]
    return df


def AddEdge(data, nodeName):
    nodeAdded = 0
    for tpl in data:
        if nodeName == tpl[0]:
            tpl[1] += 1
            # ls = list(tpl)
            # ls[1] += 1
            # tpl = tuple(ls)
            nodeAdded = 1
            break
    if not nodeAdded:
        data.append([nodeName, 1])
    return data


def get_graph_dict(path):
    df = pandas.read_csv(
        path,
        parse_dates=['real_delv_tm', 'start_opt_tm'],
        engine='python', skip_blank_lines=True)

    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.dropna(subset=['recommended_routing'], inplace=True)
    df.dropna(subset=['start_opt_tm'], inplace=True)
    df = df[['start_node_name', 'recommended_routing', 'end_node_name', 'start_opt_tm']].drop_duplicates()
    df = filter_warehouses(df)
    df = filter_sites(df)

    date_list = pandas.date_range(start=df['start_opt_tm'].min(), end=df['start_opt_tm'].max()).to_pydatetime().tolist()
    dates_interval = list(util.chunks(date_list, 14))
    res_dict = dict()
    res_list = list()
    for idx, interval in enumerate(dates_interval):
        df_ = df[(df['start_opt_tm'].isin(interval))]
        dfg_ = df_.groupby('start_node_name')
        for warehouse_nm, group in dfg_:
            # 第一个分拣中心是仓的邻居，最后一个分拣中心是站的邻居，分拣中心和分拣中心之间互为邻居
            warehouse_data = res_dict[warehouse_nm] if warehouse_nm in res_dict else list()
            for idx, row in group.iterrows():
                re_center = re.compile('([\u4e00-\u9fa5]+分拣中心)')
                center_list = re_center.findall(row['recommended_routing'])
                site_nm = row['end_node_name']

                if len(center_list) == 0:
                    warehouse_data = AddEdge(warehouse_data, site_nm)
                    # 站的聚合
                    site_data = res_dict[site_nm] if site_nm in res_dict else list()
                    site_data = AddEdge(site_data, warehouse_nm)
                    res_dict[site_nm] = site_data
                    continue

                first_center = center_list[0]
                last_center = center_list[-1]
                warehouse_data = AddEdge(warehouse_data, first_center)
                # 站的聚合
                site_data = res_dict[site_nm] if site_nm in res_dict else list()
                site_data = AddEdge(site_data, last_center)
                res_dict[site_nm] = site_data
                # 分拣中心的聚合：前后节点
                for i, center_nm in enumerate(center_list):
                    cur_center_data = res_dict[center_nm] if center_nm in res_dict else list()
                    if i == 0:
                        cur_center_data = AddEdge(cur_center_data, warehouse_nm)
                    else:
                        cur_center_data = AddEdge(cur_center_data, center_list[i - 1])
                    if i + 1 == len(center_list):
                        cur_center_data = AddEdge(cur_center_data, site_nm)
                    else:
                        cur_center_data = AddEdge(cur_center_data, center_list[i + 1])
                    res_dict[center_nm] = cur_center_data

            res_dict[warehouse_nm] = warehouse_data

        res_list.append(res_dict)
        res_dict = dict()
    with open('heterogeneous_relation.pkl', 'wb') as f:
        pickle.dump(res_list, f)


if __name__ == '__main__':
    changePath(1)
    # TimingStackedAnalysis(None, '上海-苏州')
    # TimingStackedAnalysis(None, '其他城市')
    # TimingStackedAnalysis(None, '其他城市')
    # route_distribution_draw()
    analyse()
    # drawSided()
    path = DISK_PATH_MACHINE + '数据/全阶段/所有订单数据.csv'
    get_graph_dict(path)
