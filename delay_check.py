import datetime
import seaborn as sns
import numpy as np
import pandas
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def reIndex(df):
    length = df.shape[0]
    df.index = range(length)
    return df


def levelize(row):
    if row['city_dis'] < 100:
        return 1
    if row['city_dis'] < 200:
        return 2
    if row['city_dis'] < 300:
        return 3
    return 4
    pass


def delevelize(level):
    if level == 1:
        return '100km内'
    if level == 2:
        return '100km～200km'
    if level == 3:
        return '200km～300km'
    return '300km或更远'


def toHours(seconds):
    seconds_in_day = 60 * 60 * 24
    seconds_in_hour = 60 * 60
    seconds_in_minute = 60

    days = seconds // seconds_in_day
    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
    # print(days, hours, minutes)
    return days + hours / 24, days * 24 + hours


def convertSeconds(x, attr1, attr2):
    if x[attr1].strftime("%m%d") == x[attr2].strftime("%m%d"):
        # unsent = 0
        sent = 1
    else:
        # unsent = 1
        sent = 0
    return sent, toHours(x['delay_seconds'])


start_m = 1
start_d = 1
end_m = 8
end_d = 15


def out_delv():
    # get real city of 1621 warehouses
    address_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    city_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/城市到上海距离.csv', engine='python',
        skip_blank_lines=True)

    # this is single one site, delay condition, x: dates, y: delay_times
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)
    df.dropna(subset=['end_node_insp_tm'], inplace=True)
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df = df.rename(columns={'delv_center_num': 'delv_center_num_c'})
    warehouse_df = df.drop_duplicates(subset=['store_id_c', 'delv_center_num_c'])
    warehouse_df = warehouse_df[['store_id_c', 'delv_center_num_c']]  # all warehouses in table
    warehouse_df = pandas.merge(address_df, warehouse_df, on=['store_id_c', 'delv_center_num_c'], how='right')
    warehouse_df = pandas.merge(city_df, warehouse_df, on=['city'], how='right')
    warehouse_df['distance_level'] = warehouse_df.apply(lambda x: levelize(x), axis=1)
    ware_dfg = warehouse_df.groupby('distance_level')

    for k, df_dis in ware_dfg:
        print(k)

        df_dis_waybill = pandas.merge(df_dis, df, on=['store_id_c', 'delv_center_num_c'], how='left')
        # delayed time, get seconds, this is supposed to be y-axis values
        df_dis_waybill['delay_seconds'] = df_dis_waybill.apply(
            lambda x: (x['real_delv_tm'] - x['end_node_insp_tm']).total_seconds(), axis=1)
        df_dis_waybill[['sent', 'unsent', 'delay_time']] = df_dis_waybill.apply(
            lambda x: convertSeconds(x, 'end_node_insp_tm', 'real_delv_tm'), axis=1,
            result_type='expand')
        # dates, this is supposed to be x-axis values
        # df_dis_waybill['arrival_dt'] = df_dis_waybill['end_node_insp_tm'].apply(
        #     lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
        df_dis_waybill['arrival_dt'] = df_dis_waybill['end_node_insp_tm'].dt.strftime('%m-%d')
        df_dis_waybill.drop_duplicates(inplace=True)
        # df_dis_waybill['arrival_dt'] = df_dis_waybill['end_node_insp_tm'].apply(
        #     lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))

        # average_delayed_time = df_dis_waybill.groupby(['arrival_dt'])['delay_time'].mean()
        # average_delayed_time_df = average_delayed_time.to_frame()
        # average_delayed_time_df.reset_index(drop=False, inplace=True)
        # all_parcels_unsent = df_dis_waybill.groupby(['arrival_dt'])['unsent'].sum()
        # all_parcels_unsent_df = all_parcels_unsent.to_frame()
        # all_parcels_unsent_df.reset_index(drop=False, inplace=True)
        #
        # average_delayed_time_df.to_csv('1.csv', index=False)
        # all_parcels_unsent_df.to_csv('2.csv', index=False)
        # Exclude all rows that are max or min within group
        time_mask = (
            df_dis_waybill['delay_time'].eq(df_dis_waybill.groupby('arrival_dt')['delay_time'].transform('max')))
        # | df_dis_waybill['delay_time'].eq(
        # df_dis_waybill.groupby('arrival_dt')['delay_time'].transform('min')))
        df_dis_waybill['mean_time'] = (
            df_dis_waybill['delay_time'].mask(time_mask).groupby(df_dis_waybill['arrival_dt']).transform('mean'))

        df_dis_waybill['sum_unsent'] = (
            df_dis_waybill['unsent'].groupby(df_dis_waybill['arrival_dt']).transform('sum'))
        df_dis_waybill['sum_sent'] = (
            df_dis_waybill['sent'].groupby(df_dis_waybill['arrival_dt']).transform('sum'))

        df_dis_waybill = df_dis_waybill[['mean_time', 'sum_unsent', 'sum_sent', 'arrival_dt']]
        df_dis_waybill.drop_duplicates(inplace=True)
        df_dis_waybill.fillna(0, inplace=True)
        df_dis_waybill.reset_index(drop=True, inplace=True)
        df_dis_waybill.sort_values(by='arrival_dt', inplace=True)
        # df_dis_waybill['arrival_dt'] = df_dis_waybill['arrival_dt'].apply(lambda x: x[5:])

        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))

        ax = sns.barplot(data=df_dis_waybill, x="arrival_dt", y="mean_time")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('日期')
        ax.set_ylabel('延迟时间')
        ax.set_title('{km}仓库运单-时效性分析（入站-妥投）'.format(km=delevelize(k)))

        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig('pngs/{km}_time_.png'.format(km=k))
        plt.show()
        df_dis_waybill = df_dis_waybill[['arrival_dt', 'sum_unsent', 'sum_sent']]
        ax = df_dis_waybill.set_index('arrival_dt').plot(kind='bar', stacked=True, color=['LightCoral', 'LightGreen'])
        # ax = sns.barplot(data=df_dis_waybill, x="arrival_dt", y="sum_unsent")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('日期')
        ax.set_ylabel('未完成运单数/完成运单数')
        ax.tick_params(axis='x', labelrotation=0)
        ax.set_title('{km} 仓库运单-单量完成情况分析（入站-妥投）'.format(km=delevelize(k)))
        s1 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig('pngs/{km}_unsent_.png'.format(km=k))
    pass


def out_delv_no_distance():
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)
    df.dropna(subset=['end_node_insp_tm'], inplace=True)
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df = df.rename(columns={'delv_center_num': 'delv_center_num_c'})
    df['real_delv_tm'] = pandas.to_datetime(df['real_delv_tm'], format='%Y-%m-%d')
    df['end_node_insp_tm'] = pandas.to_datetime(df['end_node_insp_tm'], format='%Y-%m-%d')
    # df = df[df['real_delv_tm'] > datetime.datetime(2022, 3, 1)]
    # df = df[df['real_delv_tm'] < datetime.datetime(2022, 4, 12)]
    df['delay_seconds'] = df.apply(
        lambda x: (x['real_delv_tm'] - x['end_node_insp_tm']).total_seconds(), axis=1)
    df = df[df['delay_seconds'] > 0]  # 去除负值

    df['delay_days'] = df.apply(
        lambda x: toHours(x['delay_seconds']), axis=1,
        result_type='expand')
    df['arrival_dt'] = df['end_node_insp_tm'].dt.strftime('%m-%d')
    df['departure_dt'] = df['real_delv_tm'].dt.strftime('%m-%d')
    df.drop_duplicates(inplace=True)

    # 删除异常值
    df = remove_outliers(df)

    df['avg_delay_days'] = (
        df['delay_days'].groupby(df['departure_dt']).transform('mean'))

    # 每天营业部收到的订单
    df_inflow = df.groupby('arrival_dt').size().reset_index(name='inflow')
    # 每天营业部投出去的订单
    df_outflow = df.groupby('departure_dt').size().reset_index(
        name='outflow')

    df_dis_waybill_res = df[['avg_delay_days', 'departure_dt']]
    # df_dis_waybill_res = df[['avg_delay_days', 'departure_dt', 'store_name_c', 'store_id_c', 'delv_center_num_c']]
    df_dis_waybill_res.drop_duplicates(inplace=True)

    df_dis_waybill_res.index = df_dis_waybill_res['departure_dt']
    # 营业部积压的订单　
    df_dis_waybill_res['stay'] = 0
    for k2 in list(df_dis_waybill_res['departure_dt']):
        df_t = df[(df['departure_dt'] > k2) & (df['arrival_dt'] <= k2)]
        df_dis_waybill_res.at[k2, 'stay'] = df_t.shape[0]
    df_dis_waybill_res.reset_index(drop=True, inplace=True)

    df_dis_waybill_res = pandas.merge(df_dis_waybill_res, df_outflow, on=['departure_dt'], how='left')
    df_dis_waybill_res = pandas.merge(df_dis_waybill_res, df_inflow, left_on=['departure_dt'],
                                      right_on=['arrival_dt'], how='left')

    df_dis_waybill_res.fillna(0, inplace=True)
    df_dis_waybill_res.drop_duplicates(inplace=True)
    df_dis_waybill_res.sort_values(by='departure_dt', inplace=True)
    df_dis_waybill_res.reset_index(drop=True, inplace=True)
    df_low_income = df_dis_waybill_res[df_dis_waybill_res['inflow'] < 200]
    # df_warehouse = df_warehouse.drop_duplicates(subset=['store_name_c', 'store_id_c', 'delv_center_num_c'])
    # df_warehouse = df_warehouse[['store_name_c', 'store_id_c', 'delv_center_num_c']]
    df_low_income.to_csv('csvs/days_low_income.csv', index=False)
    df_dis_waybill_res.to_csv('csvs/all_days_condition.csv', index=False)
    exit(0)

    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 10))

    ax = sns.barplot(data=df_dis_waybill_res, x="departure_dt", y="avg_delay_days")
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.grid(True)  # 显示网格
    ax.set_xlabel('妥投日期')
    ax.set_ylabel('延迟天数')
    ax.set_title('仓库运单-时效性分析(入站-妥投)')

    ax2 = ax.twinx()
    sns.lineplot(data=df_dis_waybill_res, x='departure_dt', y='inflow', marker='o', color='red', ax=ax2)
    ax2.set_ylabel('当日入站总量')
    ax2.legend(labels=['当日入站总量'])

    s1 = 200 / plt.gcf().dpi * 10
    margin = 0.5 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])

    plt.savefig('pngs/入站-妥投/time_v2.png')
    plt.show()

    # 2 箱形图
    df.sort_values(by=['departure_dt'], inplace=True)
    ax = sns.boxplot(data=df, x="departure_dt", y="delay_days", orient="v", whis=4, fliersize=1)
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.grid(True)
    ax.set_xlabel('妥投日期')
    ax.set_ylabel('延迟天数')
    ax.tick_params(axis='x', labelrotation=0)
    ax.set_title('仓库运单-时效性 箱形图分析(入站-妥投)')
    s2 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
    margin2 = 0.5 / plt.gcf().get_size_inches()[1]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin, bottom=margin2, top=1. - margin2)
    plt.gcf().set_size_inches(s1, s2)
    plt.savefig('pngs/入站-妥投/delay_box_v2.png')
    plt.show()

    # 3 单量比例
    df_dis_waybill_res_ = df_dis_waybill_res[
        ['departure_dt', 'inflow', 'outflow', 'stay']]
    df_dis_waybill_res_.columns = ['departure_dt', '当日入站量', '当日妥投量', '历史积压单量']
    ax = df_dis_waybill_res_.set_index('departure_dt').plot(kind='bar', stacked=True)
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.grid(True)
    ax.set_xlabel('妥投日期')
    ax.set_ylabel('运单数')
    ax.tick_params(axis='x', labelrotation=0)
    ax.set_title('仓库运单-单量处理情况分析(入站-妥投)')

    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
    plt.savefig('pngs/入站-妥投/unsent_v2.png')
    plt.show()


def testTimestamp(start_m, start_d, end_m, end_d):
    dt1 = datetime.datetime(year=2022, month=start_m, day=start_d)
    dt2 = datetime.datetime(year=2022, month=end_m, day=end_d)
    return int(dt1.timestamp()), int(dt2.timestamp())


def remove_outliers(df, dt_col, dt_attr):
    from matplotlib.cbook import boxplot_stats
    dfg = df.groupby(dt_attr)
    for k, df_daily in dfg:
        fliers = boxplot_stats(df_daily[dt_col], whis=5).pop(0)['fliers']
        df_drop_daily = df_daily[df_daily[dt_col].isin(fliers)]
        drop_index = df_drop_daily.index
        df.drop(drop_index, inplace=True, axis=0)
    return df


def analyse(attr1, attr2, info, considerDelvCenter):
    address_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)
    city_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/城市到上海距离.csv', engine='python',
        skip_blank_lines=True)
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=[attr1, attr2],
        engine='python', skip_blank_lines=True)
    df.dropna(subset=[attr1], inplace=True)
    df.dropna(subset=[attr2], inplace=True)

    df = df.rename(columns={'delv_center_num': 'delv_center_num_c'})
    warehouse_df = df.drop_duplicates(subset=['store_id_c', 'delv_center_num_c'])
    warehouse_df = warehouse_df[['store_id_c', 'delv_center_num_c']]  # all warehouses in table
    warehouse_df = pandas.merge(address_df, warehouse_df, on=['store_id_c', 'delv_center_num_c'], how='right')
    warehouse_df = pandas.merge(city_df, warehouse_df, on=['city'], how='right')
    warehouse_df['distance_level'] = warehouse_df.apply(lambda x: levelize(x), axis=1)
    ware_dfg = warehouse_df.groupby('distance_level')
    for k, df_dis in ware_dfg:
        df_dis_waybill = pandas.merge(df_dis, df, on=['store_id_c', 'delv_center_num_c'], how='left')
        df_dis_waybill['delay_seconds'] = df_dis_waybill.apply(
            lambda x: (x[attr2] - x[attr1]).total_seconds(), axis=1)
        df_dis_waybill = df_dis_waybill[df_dis_waybill['delay_seconds'] > 0]  # 去除负值

        df_dis_waybill['delay_days'] = df_dis_waybill.apply(
            lambda x: toHours(x['delay_seconds']), axis=1)
        df_dis_waybill['arrival_dt'] = df_dis_waybill[attr1].dt.strftime('%m-%d')
        df_dis_waybill['departure_dt'] = df_dis_waybill[attr2].dt.strftime('%m-%d')
        df_dis_waybill.drop_duplicates(inplace=True)

        # 删除异常值
        df_dis_waybill = remove_outliers(df_dis_waybill)
        if (considerDelvCenter):
            df_temp = df_dis_waybill.groupby(['departure_dt', 'delv_center_num_c'])['delay_days'].sum().unstack(
                fill_value=0)
            df_temp["avg_delay_days"] = df_temp.apply(lambda x: x.mean(), axis=1)
            df_temp.reset_index(inplace=True, drop=False)
            df_temp = df_temp[['departure_dt', 'avg_delay_days']]

        df_dis_waybill['avg_delay_days'] = (
            df_dis_waybill['delay_days'].groupby(df_dis_waybill['departure_dt']).transform('mean'))

        # 每天收到的订单
        df_inflow = df_dis_waybill.groupby('arrival_dt').size().reset_index(name='inflow')
        # 每天出去的订单
        df_outflow = df_dis_waybill.groupby('departure_dt').size().reset_index(
            name='outflow')

        df_dis_waybill_res = df_dis_waybill[['avg_delay_days', 'departure_dt']]
        df_dis_waybill_res.drop_duplicates(inplace=True)

        df_dis_waybill_res.index = df_dis_waybill_res['departure_dt']
        # 营业部积压的订单　
        df_dis_waybill_res['stay'] = 0
        for k2 in list(df_dis_waybill_res['departure_dt']):
            df_t = df_dis_waybill[(df_dis_waybill['departure_dt'] > k2) & (df_dis_waybill['arrival_dt'] <= k2)]
            df_dis_waybill_res.at[k2, 'stay'] = df_t.shape[0]
        df_dis_waybill_res.reset_index(drop=True, inplace=True)
        df_dis_waybill_res = pandas.merge(df_dis_waybill_res, df_inflow, left_on=['departure_dt'],
                                          right_on=['arrival_dt'], how='left')
        df_dis_waybill_res = pandas.merge(df_dis_waybill_res, df_outflow, on=['departure_dt'], how='left')

        if considerDelvCenter:
            df_temp = pandas.merge(df_temp, df_inflow, left_on=['departure_dt'],
                                   right_on=['arrival_dt'], how='left')
            df_temp = pandas.merge(df_temp, df_outflow, on=['departure_dt'], how='left')

        df_dis_waybill_res.fillna(0, inplace=True)
        df_dis_waybill_res.drop_duplicates(inplace=True)
        df_dis_waybill_res.sort_values(by='departure_dt', inplace=True)
        df_dis_waybill_res.reset_index(drop=True, inplace=True)

        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))
        if considerDelvCenter:
            ax = sns.barplot(data=df_temp, x="departure_dt", y="avg_delay_days")
        else:
            ax = sns.barplot(data=df_dis_waybill_res, x="departure_dt", y="avg_delay_days")
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel(f'{info[3:5]}日期')
        ax.set_ylabel('延迟天数')
        ax.set_title(f'{delevelize(k)}配送中心运单-时效性分析({info})')

        ax2 = ax.twinx()
        if considerDelvCenter:
            sns.lineplot(data=df_temp, x='departure_dt', y='inflow', marker='o', color='red', ax=ax2)
        else:
            sns.lineplot(data=df_dis_waybill_res, x='departure_dt', y='inflow', marker='o', color='red', ax=ax2)
        ax2.set_ylabel('当日{info}总量'.format(info=info[0:2]))
        ax2.legend(labels=['当日{info}总量'.format(info=info[0:2])])

        s1 = 200 / plt.gcf().dpi * 10
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])

        plt.savefig(f'pngs/配送中心-入站/{k}_time.png')
        plt.show()

        # # 2 箱形图
        # df_dis_waybill.sort_values(by=['departure_dt'], inplace=True)
        # ax = sns.boxplot(data=df_dis_waybill, x="departure_dt", y="delay_days", orient="v", whis=4, fliersize=1)
        # ax.xaxis.set_major_locator(MultipleLocator(7))
        # ax.grid(True)
        # ax.set_xlabel(f'{info[3:5]}日期')
        # ax.set_ylabel('延迟天数')
        # ax.tick_params(axis='x', labelrotation=0)
        # ax.set_title('{km} 仓库运单-时效性 箱形图分析({info})'.format(km=delevelize(k), info=info))
        # s2 = 200 / plt.gcf().dpi * 10 + 2 * 0.2
        # margin2 = 0.5 / plt.gcf().get_size_inches()[1]
        # plt.gcf().subplots_adjust(left=margin, right=1. - margin, bottom=margin2, top=1. - margin2)
        # plt.gcf().set_size_inches(s1, s2)
        # plt.savefig('pngs/{info}/{km}_delay_box_v2.png'.format(km=k, info=info))
        # plt.show()

        # 3 单量比例
        df_dis_waybill_res_ = df_dis_waybill_res[
            ['departure_dt', 'inflow', 'outflow', 'stay']]
        df_dis_waybill_res_.columns = ['departure_dt', f'当日{info[0:2]}量', f'当日{info[3:5]}总量', '历史积压单量']
        if considerDelvCenter:
            df_temp = df_temp[['departure_dt', 'inflow', 'outflow']]
            df_temp.columns = ['departure_dt', f'当日{info[0:2]}量', f'当日{info[3:5]}总量']
            ax = df_temp.set_index('departure_dt').plot(kind='bar', stacked=True)
        else:
            ax = df_dis_waybill_res_.set_index('departure_dt').plot(kind='bar', stacked=True)
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)
        ax.set_xlabel(f'{info[3:5]}日期')
        ax.set_ylabel('运单数')
        ax.tick_params(axis='x', labelrotation=0)
        ax.set_title('{km} 配送中心运单-单量处理情况分析({info})'.format(km=delevelize(k), info=info))

        # ax2 = ax.twinx()
        # df_dis_waybill_res_ = df_dis_waybill_res[['arrival_dt', '']]
        # sns.lineplot(data=df_dis_waybill_res_, markers=['>'], ax=ax2)
        # ax2.set_ylabel('总运单数')
        # ax2.sharey(ax)

        # lines, labels = ax.get_legend_handles_labels()
        # lines2, labels2 = ax2.get_legend_handles_labels()
        # ax2.legend(lines + lines2, labels + labels2, loc=0)

        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        plt.savefig(f'pngs/配送中心-入站/{k}_unsent_delv.png')
        plt.show()


def findWarehouse():
    df = pandas.read_csv(
        'csvs/days_low_income.csv', parse_dates=['departure_dt'],
        engine='python', skip_blank_lines=True)

    df['departure_dt'] = pandas.to_datetime(df['departure_dt'], format='%m-%d')

    df['departure_dt'] = df['departure_dt'].apply(
        lambda x: (x.replace(year=2022)))
    df['departure_dt'] = df['departure_dt'].dt.strftime('%m-%d')
    df_dt = df[['departure_dt', 'inflow']]

    df_all = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)

    df_all.dropna(subset=['end_node_insp_tm'], inplace=True)
    df_all.dropna(subset=['real_delv_tm'], inplace=True)
    df_all['departure_dt'] = df_all['real_delv_tm'].dt.strftime('%m-%d')
    df_all.drop_duplicates(inplace=True)

    df_filtered = pandas.merge(df_dt, df_all, on='departure_dt', how='inner')
    df_filtered.drop_duplicates(inplace=True)
    df_filtered.sort_values(by='departure_dt', inplace=True)

    df_filtered_store = df_filtered[['store_name_c']]
    df_filtered_store.drop_duplicates(inplace=True)  # 日期内单量少的所有仓
    df_filtered_store.to_csv('csvs/warehouses_low.csv', index=False)


def draw():
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)

    df.dropna(subset=['end_node_insp_tm'], inplace=True)
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.drop_duplicates(inplace=True)

    df['real_delv_tm'] = pandas.to_datetime(df['real_delv_tm'], format='%Y-%m-%d')
    df['end_node_insp_tm'] = pandas.to_datetime(df['end_node_insp_tm'], format='%Y-%m-%d')

    df_warehouse = pandas.read_csv(
        'csvs/warehouses_low.csv',
        engine='python', skip_blank_lines=True)

    # 重点分析这些仓库
    df = pandas.merge(df, df_warehouse, on='store_name_c', how='inner')

    df['arrival_dt'] = df['end_node_insp_tm'].dt.strftime('%m-%d')
    df['departure_dt'] = df['real_delv_tm'].dt.strftime('%m-%d')

    # 每天营业部收到的来自不同仓库的订单
    df_inflow_from_warehouses = df.groupby(['store_name_c', 'arrival_dt']).size().unstack(fill_value=0)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 10))
    s1 = 200 / plt.gcf().dpi * 10
    margin = 0.5 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])

    for idx, row in df_inflow_from_warehouses.iterrows():
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.figure(figsize=(12, 10))
        s1 = 200 / plt.gcf().dpi * 10
        margin = 0.5 / plt.gcf().get_size_inches()[0]
        plt.gcf().subplots_adjust(left=margin, right=1. - margin)
        plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
        print(idx)
        print(row.values)
        ax = sns.barplot(x=df_inflow_from_warehouses.columns, y=row.values)
        ax.xaxis.set_major_locator(MultipleLocator(7))
        ax.grid(True)  # 显示网格
        ax.set_xlabel('入站日期')
        ax.set_ylabel('单量')
        ax.set_title(idx)
        plt.show()


def stay_priority_check():
    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)
    df.dropna(subset=['end_node_insp_tm'], inplace=True)
    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.drop_duplicates(inplace=True)
    df = df.rename(columns={'delv_center_num': 'delv_center_num_c'})
    df['real_delv_tm'] = pandas.to_datetime(df['real_delv_tm'], format='%Y-%m-%d')
    df['end_node_insp_tm'] = pandas.to_datetime(df['end_node_insp_tm'], format='%Y-%m-%d')

    df = df[df['real_delv_tm'] > datetime.datetime(2022, 5, 20)]
    df = df[df['real_delv_tm'] < datetime.datetime(2022, 6, 20)]

    df['delv_dt'] = df['real_delv_tm'].dt.strftime('%m-%d')
    df['in_dt'] = df['end_node_insp_tm'].dt.strftime('%m-%d')
    df['hour'] = df['end_node_insp_tm'].dt.strftime('%H')  # 送达到day1 到小时
    df['stay'] = df.apply(lambda x: 1 if x['in_dt'] != x['delv_dt'] else 0, axis=1)  # day1没妥投
    df['isAfternoon'] = df.apply(lambda x: 1 if int(x['hour']) >= 12 else 0, axis=1)

    df_all = df
    df = df[df['stay'] == 1]
    df['delay_days'] = df.apply(lambda x: toHours((x['real_delv_tm'] - x['end_node_insp_tm']).total_seconds()), axis=1)
    # 关注那些当天没送到的订单，检查延迟订单的送达时间，看上下午的比例
    df['sum_afternoon'] = (
        df['isAfternoon'].groupby(df['in_dt']).transform('sum'))

    df_inflow = df.groupby('in_dt').size().reset_index(name='all')
    df_inflow = df_inflow[['in_dt', 'all']]
    df_inflow.drop_duplicates(inplace=True)
    df_res = df[['sum_afternoon', 'in_dt']]
    df_res.drop_duplicates(inplace=True)
    df_res = pandas.merge(df_inflow, df_res, on='in_dt', how='outer')
    df_res['ratio'] = df_res['sum_afternoon'] / df_res['all']

    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 10))
    ax = sns.lineplot(data=df_res, x='in_dt', y='ratio')
    ax.xaxis.set_major_locator(MultipleLocator(3))
    ax.grid(True)  # 显示网格
    ax.set_xlabel('妥投日期')
    ax.set_ylabel('下午入站的单量比例')
    ax.set_title('当天未妥投单量')
    plt.savefig('pngs/入站-妥投/积压单量时间.png')
    plt.show()


if __name__ == '__main__':
    # analyse('sale_ord_tm', 'first_sorting_tm', '入仓-出仓')
    analyse('first_sorting_tm', 'end_node_insp_tm', '出仓-入站', True)
    # out_delv_no_distance()
    # findWarehouse()
    # draw()
    exit(0)
    stay_priority_check()
    exit(0)
