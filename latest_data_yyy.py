import datetime
import re

import pandas
from folium import folium, plugins
from matplotlib.ticker import MultipleLocator

from delay_check import levelize, remove_outliers, toHours, delevelize
from util import plotDotforDataframe


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
        '/Users/lyam/同步空间/数据/全阶段/分拣中心addr.csv', engine='python',
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

        df_res.apply(lambda x: plotDotforDataframe(x, map), axis=1)

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
        df_dis_waybill = remove_outliers(df_dis_waybill, attr2)

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
    col3 = attr + '_hours'
    col4 = attr + '_unsent'
    col5 = 'avg_' + attr + '_days'
    col6 = 'avg_' + attr + '_hours'
    col7 = 'sum_' + attr + '_unsent'
    df.dropna(subset=[dt1], inplace=True)
    df.dropna(subset=[dt2], inplace=True)

    df[col1] = df.apply(
        lambda x: (x[dt2] - x[dt1]).total_seconds(), axis=1)
    df[col4] = df.apply(
        lambda x: unsent(x, dt1, dt2), axis=1)
    df[[col2, col3]] = df.apply(
        lambda x: toHours(x[col1]), axis=1, result_type='expand')

    df['dt'] = df[dt2].dt.strftime('%m-%d')
    df.drop_duplicates(inplace=True)
    df = remove_outliers(df, col3, 'dt')

    df[col5] = (
        df[col2].groupby(df['dt']).transform('mean'))
    df[col6] = (
        df[col3].groupby(df['dt']).transform('mean'))
    df[col7] = (
        df[col4].groupby(df['dt']).transform('sum'))
    df = df[['dt', col5, col6, col7]]
    df.drop_duplicates(inplace=True)
    return col5, df


def cal_Quantity(df, attr, dt1, dt2):
    df[dt2] = df[dt2].dt.strftime('%m-%d')
    df.drop_duplicates(inplace=True)

    return df


def TimingStackedAnalysis(ware_dfg, df):
    for k, df_dis in ware_dfg:
        print(k)
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
                                                                 'end_sorting_real_ship_tm')
        col_site_delv, df_site_delv = cal_timing(df_dis_waybill, 'site_delv',
                                                 'end_sorting_real_ship_tm',
                                                 'real_delv_tm')
        df_res = pandas.merge(df_warehouse, df_ware_center, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_start_center_in_out, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_start_center_out_end_in, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_end_center_in_out, on='dt', how='outer')
        df_res = pandas.merge(df_res, df_site_delv, on='dt', how='outer')

        # df_dis_waybill = df_dis_waybill[
        #     ['dt', col_warehouse, col_ware_center, col_start_center_in_out, col_start_center_out_end_in,
        #      col_end_center_in_out, col_site_delv]]
        df_res.drop_duplicates(inplace=True)
        # df.drop('Unnamed: 0', inplace=True, axis=1)
        df_res.sort_values(by='dt', inplace=True)
        from matplotlib import pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))

        ax = df_res.set_index('dt').plot(kind='bar', stacked=True,
                                         color=['#D98880', '#7DCEA0', '#F19F6A', '#7EA1E1', '#6ECAD0', '#90909F'])
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('日期')
        ax.set_ylabel('天数')
        ax.legend(labels=['入仓-出仓', '出仓-入始分拣中心', '始分拣中心的入和出', '出始分拣中心-入末分拣中心',
                          '末分拣中心入和出', '末分拣中心-妥投'])
        ax.tick_params(axis='x', labelrotation=0)
        ax.set_title('{km} 仓库各阶段耗时分析'.format(km=delevelize(k)))

        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig('pngs/全阶段/{km}_timing.png'.format(km=k))
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


def draw():
    from matplotlib import pyplot as plt
    import seaborn as sns
    for k in range(1, 5):
        df = pandas.read_csv(
            f'csvs/{k}df_timing_unsent.csv',
            engine='python', skip_blank_lines=True)
        df.dropna(inplace=True)
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        df['dt'] = df.apply(lambda x: datetime.datetime.strptime(x['dt'], "%m-%d"), axis=1)
        df['dt'] = df['dt'].apply(lambda x: x.replace(year=2022))
        df = df[['dt', 'avg_ware_center_days', 'avg_start_center_out_end_in_days', 'avg_site_delv_days']]
        # df = df[['dt', 'avg_warehouse_days', 'avg_ware_center_days', 'avg_start_center_in_out_days',
        #          'avg_start_center_out_end_in_days', 'avg_end_center_in_out_days', 'avg_site_delv_days']]
        # 1,2,7,8常规场景
        df_covid = df[(df['dt'] < datetime.datetime(2022, 7, 1)) & (df['dt'] >= datetime.datetime(2022, 3, 1))]
        df_normal = df[(df['dt'] < datetime.datetime(2022, 3, 1)) | (df['dt'] >= datetime.datetime(2022, 7, 1))]
        df_covid.sort_values(by='dt', inplace=True)
        df_covid['dt'] = df_covid['dt'].dt.strftime('%m-%d')
        df_normal['dt'] = df_normal['dt'].dt.strftime('%m-%d')
        df_normal = df_normal[:-3]
        df_normal['dt'] = list(df_covid['dt'])
        df_normal = df_normal.melt(id_vars=['dt'], var_name='type', value_name='avg_days')
        df_covid = df_covid.melt(id_vars=['dt'], var_name='type', value_name='avg_days')

        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15.4, 12.8), sharey=True,
                                       gridspec_kw={'wspace': 0, 'width_ratios': [1, 5]})
        # color=['#F8C471', '#7DCEA0', '#85C1E9', '#BB8FCE', '#D98880'])
        sns.barplot(data=df_covid, x='avg_days', y='dt', hue='type',
                    ci=False, dodge=True, ax=ax2)
        ax2.tick_params(labelright=False, right=False)
        ax2.set_ylabel('')
        ax2.set_xlabel('疫情场景')
        plt.title('耗时天数分析')
        # draw juvenile subplot at the left
        sns.barplot(data=df_normal, x='avg_days', y='dt', hue='type',
                    ci=False, dodge=True, ax=ax1)
        l1, lb1 = ax1.get_legend_handles_labels()
        l2, lb2 = ax2.get_legend_handles_labels()
        ax2.legend(l1 + l2, ['仓库-分拣中心', '始末分拣中心耗时', '末分拣中心-妥投'], loc='upper right')

        ax1.set_xlim(0, 1)
        ax1.set_xticks([0, 1])
        ax1.set_ylabel('日期')
        ax1.yaxis.set_major_locator(MultipleLocator(7))
        ax1.set_xlabel('常规场景')
        ax1.tick_params(axis='y', labelleft=True, left=True)
        ax1.invert_xaxis()  # reverse the direction
        ax1.legend_.remove()  # remove the legend; the legend will be in ax1

        plt.savefig(f'pngs/全阶段/timing_on_the_way_{k}.png')
        plt.show()
        exit(0)
        ax = df_res.set_index('dt').plot(kind='bar', stacked=True,
                                         color=['#D98880', '#7DCEA0', '#F19F6A', '#7EA1E1', '#6ECAD0', '#90909F'])
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('日期')
        ax.set_ylabel('天数')
        ax.legend(labels=['入仓-出仓', '出仓-入始分拣中心', '始分拣中心的入和出', '出始分拣中心-入末分拣中心',
                          '末分拣中心入和出', '末分拣中心-妥投'])
        ax.tick_params(axis='x', labelrotation=0)
        ax.set_title('{km} 仓库各阶段耗时分析'.format(km=delevelize(k)))

        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig('pngs/全阶段/{km}_timing.png'.format(km=k))
        plt.show()


def analyse():
    # df = pandas.read_csv(
    #     'df_temp.csv', engine='python',
    #     skip_blank_lines=True).fillna(0)
    # # df_dis_waybill = df_dis_waybill[
    # #     ['dt', col_warehouse, col_ware_center, col_start_center_in_out, col_start_center_out_end_in,
    # #      col_end_center_in_out, col_site_delv]]
    # df.drop_duplicates(inplace=True)
    # df.drop('Unnamed: 0', inplace=True, axis=1)
    # df.sort_values(by='dt', inplace=True)
    # from matplotlib import pyplot as plt
    # plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    # plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # plt.figure(figsize=(12, 10))
    #
    # ax = df.set_index('dt').plot(kind='bar', stacked=True, color=['#D98880', '#7DCEA0', '#F19F6A', '#7EA1E1', '#6ECAD0', '#90909F'])
    # ax.xaxis.set_major_locator(MultipleLocator(7))
    # ax.grid(True)  # 显示网格
    # ax.set_xlabel('日期')
    # ax.set_ylabel('天数')
    # ax.tick_params(axis='x', labelrotation=0)
    #
    # s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
    # margin = 0.5 / plt.gcf().get_size_inches()[0]
    # plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    # plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
    # plt.show()
    # exit(0)
    dt_ls = ['plan_delv_dt', 'start_opt_tm', 'plan_delv_tm', 'real_delv_tm', 'route_start_node_real_arv_tm',
             'route_start_node_real_send_tm', 'start_sorting_real_insp_tm', 'start_sorting_real_send_tm',
             'start_sorting_real_ship_tm', 'end_sorting_real_arv_tm', 'end_sorting_real_ship_tm',
             'end_sorting_real_send_tm']
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/全阶段/所有订单数据.csv',
        parse_dates=dt_ls,
        engine='python', skip_blank_lines=True)
    for i in dt_ls:
        df.dropna(subset=[i], inplace=True)
    # Routing(df)

    address_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    city_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/城市到上海距离.csv', engine='python',
        skip_blank_lines=True)
    warehouse_df = df.drop_duplicates(subset=['start_node_name'])
    warehouse_df = warehouse_df[['start_node_name']]  # all warehouses in table
    warehouse_df = pandas.merge(address_df, warehouse_df, left_on='store_name_c', right_on=['start_node_name'],
                                how='right')
    warehouse_df.dropna(inplace=True, subset=['city'])
    warehouse_df = pandas.merge(city_df, warehouse_df, on=['city'], how='right')
    warehouse_df['distance_level'] = warehouse_df.apply(lambda x: levelize(x), axis=1)
    ware_dfg = warehouse_df.groupby('distance_level')
    # OutOfTime(ware_dfg, df)
    # TimingAnalysis(ware_dfg, df, '入仓-出仓', 'route_start_node_real_arv_tm', 'route_start_node_real_send_tm')
    # TimingStackedAnalysis(ware_dfg, df)
    # RoutingCount(ware_dfg, df)

    TimingSidedAnalysis(ware_dfg, df)

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


if __name__ == '__main__':
    draw()
