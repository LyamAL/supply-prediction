import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from pylab import *

from delay_check import levelize


def set_size(w, h, ax=None):
    """ w, h: width, height in inches """
    if not ax: ax = plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w) / (r - l)
    figh = float(h) / (t - b)
    ax.figure.set_size_inches(figw, figh)


def analyse():
    df = pandas.read_excel('/Users/lyam/Documents/mystuff/dynamic_pricing/海哥_民旺9-10月小哥画像ok1.xlsx',
                           sheet_name='cp_courier')
    df.sort_values(by='日均单量', ascending=False, inplace=True)
    df = df.head(10)

    # 收集所有路区id
    main_range = df['主要路区id'].value_counts().sort_index().index.tolist()
    secondary_range = df['次要路区id'].value_counts().sort_index().index.tolist()
    user_range = df['用户名'].value_counts().sort_index().index.tolist()
    map1 = dict(zip(main_range, list(range(len(main_range)))))
    map2 = dict(zip(secondary_range, list(range(len(main_range), len(main_range) + len(secondary_range)))))
    map3 = dict(zip(user_range, list(range(len(user_range)))))
    df['user_id'] = df['用户名'].map(map3)
    df['main_id'] = df['主要路区id'].map(map1)
    df['secondary_id'] = df['次要路区id'].map(map2)
    df['third_id'] = df['secondary_id'].max() + 1

    df_res = pandas.DataFrame(columns=['user_id', 'area_id', 'count'])
    dfg = df.groupby('user_id')
    for k, v in dfg:
        for i, r in v.iterrows():
            a1 = {'user_id': k, 'area_id': r['main_id'], 'count': 1}
            a2 = {'user_id': k, 'area_id': r['secondary_id'], 'count': 1}
            a3 = {'user_id': k, 'area_id': r['third_id'], 'count': 1}
            # a1 = {'user_id': k, 'area_id': r['main_id'], 'count': r['主要路区']}
            # a2 = {'user_id': k, 'area_id': r['secondary_id'], 'count': r['次要路区']}
            # a3 = {'user_id': k, 'area_id': r['third_id'], 'count': r['其他路区']}
            df_res = df_res.append([a1], ignore_index=True)
            df_res = df_res.append([a2], ignore_index=True)
            df_res = df_res.append([a3], ignore_index=True)
    df_res = df_res.pivot(index='user_id', columns='area_id', values='count').fillna(0)
    df_res.drop(18, inplace=True, axis=1)
    df_res.to_csv('t.csv', index=False)
    exit(0)

    df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/四步骤时间/03_xkw_供应_王桥_20221008202603.csv', encoding='gbk',
        parse_dates=['end_node_insp_tm', 'real_delv_tm'],
        engine='python', skip_blank_lines=True)

    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams.update({'font.size': 30})
    plt.figure(figsize=(12, 10))

    import seaborn as sns
    sns.heatmap(df_res, cbar=True, cmap='OrRd')
    plt.xlabel('Areas')
    plt.ylabel('Couriers')
    plt.savefig('pngs/海哥/heatmap.png')
    plt.show()


def heatmap():
    df = pandas.read_csv('t.csv', engine='python', skip_blank_lines=True)
    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams.update({'font.size': 50})
    plt.figure(figsize=(15.4, 12.8))

    clist = ['MistyRose', 'LightSalmon']
    # clist = ['Wheat', 'Orange']
    # clist = ['LightGoldenrodYellow', 'Gold']
    newcmp = LinearSegmentedColormap.from_list('chaos', clist)
    # sns.heatmap(df, cbar=True, cmap='OrRd')
    sns.heatmap(df, cbar=True, cmap=newcmp)
    plt.xlabel('Delivery Area No.')
    plt.ylabel('Courier No.')
    plt.savefig('pngs/海哥/heatmap_50.png')
    plt.show()


def cdf():
    df = pandas.read_csv('csvs/delivery_area.text', header=None, engine='python', skip_blank_lines=True)
    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # plt.rcParams.update({'font.size': 50})

    # x = np.random.randn(200)
    # kwargs = {'cumulative': True}
    sns.distplot(df.T, kde=True)
    # sns.distplot(df.T, hist_kws=kwargs, kde_kws=kwargs, fit=norm)
    # plt.xlabel('Delivery Area No.')
    # plt.ylabel('Courier No.')
    # plt.savefig('pngs/海哥/heatmap_50.png')
    plt.show()

    pass


def draw_Barh(i, df1, df2):
    df1 = df1[df1['dt'] == i]
    df2 = df2[df2['dt'] == i]
    df2 = df2[['waybill_code', 'operator_name', 'tm']]
    df1 = df1[['waybill_code', 'operator_name', 'tm']]
    df1['distinct_count1'] = df1.groupby(['operator_name'])['tm'].transform('nunique')
    df2['distinct_count2'] = df2.groupby(['operator_name'])['tm'].transform('nunique')
    df1['pc'] = df1.groupby(['operator_name'])['waybill_code'].transform('size')
    df2['dl'] = df2.groupby(['operator_name'])['waybill_code'].transform('size')
    df1_ = df1.drop(['waybill_code', 'tm'], axis=1)
    df1_.drop_duplicates(inplace=True)
    df2_ = df2.drop(['waybill_code', 'tm'], axis=1)
    df2_.drop_duplicates(inplace=True)
    # df11 = df1.groupby(['operator_name', 'tm']).size().reset_index(name='pc')
    # df22 = df2.groupby(['operator_name', 'tm']).size().reset_index(name='dl')
    df = pandas.merge(df1_, df2_, on=['operator_name'], how='inner')
    df['total'] = df['pc'] + df['dl']
    df.sort_values(by=['distinct_count1', 'distinct_count2', 'total'], ascending=False, inplace=True)
    df = df.head(1)
    df1 = df1[df1['operator_name'].isin(list(df['operator_name']))]
    df2 = df2[df2['operator_name'].isin(list(df['operator_name']))]
    df1_res = df1.groupby(['operator_name', 'tm']).size().reset_index(name='pickup')
    df2_res = df2.groupby(['operator_name', 'tm']).size().reset_index(name='delv')
    df_res = pandas.merge(df2_res, df1_res, on=['operator_name', 'tm'], how='inner')
    city_range = df_res['operator_name'].value_counts().sort_index().index.tolist()
    city_map = dict(zip(city_range, list(range(len(city_range)))))
    df_res['operator_name'] = df_res['operator_name'].map(city_map)
    df_res['operator_name'] = df_res['operator_name'].apply(lambda x: 'Courier No.' + str(x + 1))
    df_res_1 = df_res[['operator_name', 'tm', 'pickup']]
    df_res_2 = df_res[['operator_name', 'tm', 'delv']]
    df_res_1 = df_res_1.pivot(index='tm', columns='operator_name', values='pickup')
    df_res_2 = df_res_2.pivot(index='tm', columns='operator_name', values='delv')
    df_res_1.reset_index(inplace=True)
    df_res_2.reset_index(inplace=True)
    df_res_1.fillna(0, inplace=True)
    df_res_2.fillna(0, inplace=True)
    # df_res.sort_values(by='tm', ascending=True, inplace=True)
    # df1_res = df1.groupby(['operator_name', 'tm']).size().unstack(fill_value=0)
    # df2_res = df2.groupby(['operator_user', 'tm']).size().unstack(fill_value=0)
    # df2_res["res"] = df2_res.apply(lambda x: x.sum(), axis=1)
    # df1_res["res"] = df1_res.apply(lambda x: x.sum(), axis=1)
    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    sns.set_theme(style="whitegrid")
    fsz = 50
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15.4, 12.8), sharey=True,
                                   # gridspec_kw={'wspace': 0})
                                   gridspec_kw={'wspace': 0, 'width_ratios': [1, 3]})
    df_res_2 = df_res_2.rename(columns={'Courier No.1': 'Delivery'})
    df_res_1 = df_res_1.rename(columns={'Courier No.1': 'Pick-up'})
    # draw delivery subplot at the right
    df_res_2.plot(x='tm', y='Delivery', kind='barh', label='Delivery', ax=ax2, width=0.8,
                  color='#F8C471').legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    # color=['#F8C471', '#7DCEA0', '#85C1E9', '#BB8FCE', '#D98880'])
    # sns.barplot(data=df_res, x='delv', y='tm', hue='operator_name',
    #             ci=False, orient='horizontal', dodge=True, ax=ax2)
    ax2.tick_params(labelright=False, right=False)
    ax2.set_ylabel('')
    ax2.set_xlabel('# of Delivery', fontsize=45)
    # draw juvenile subplot at the left
    # sns.barplot(data=df_res_1, x='pickup', y='tm', hue='operator_name',
    #             ci=False, orient='horizontal', dodge=True, ax=ax1)
    df_res_1.plot(x='tm', kind='barh', ax=ax1, label='Pick-up', width=0.8,
                  color=['#D98880'])
    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    # ax1.plot(df_res_1['tm'], df_res_2['Pickup Request'], kind='barh', label='Pickup Request',
    #          color='#D98880')
    # xmax = max(ax1.get_xlim()[1], ax2.get_xlim()[1])
    # ax1.set_xlim(xmax=xmax)
    # ax2.set_xlim(xmax=xmax)
    ax1.set_ylabel('Hour of the day', fontsize=fsz)
    ax1.set_xlabel('  # of Request', fontsize=45)
    ax1.set_xlim(0, 15)
    ax1.set_xticks([0, 5, 10, 15])

    ax1.tick_params(axis='y', labelleft=True, left=True)
    ax1.invert_xaxis()  # reverse the direction
    ax1.legend_.remove()  # remove the legend; the legend will be in ax1
    # ax2.legend(loc='upper right')
    ax2.legend(l1 + l2, lb1 + lb2, loc='upper right', fontsize=38, bbox_to_anchor=(1, 0.75))
    for label in (ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_xticklabels() + ax2.get_yticklabels()):
        label.set_fontsize(fsz)
    plt.tight_layout()

    plt.savefig(f'pngs/海哥/confict-{i}_v2.png')
    plt.show()
    exit(0)


def barline():
    df2 = pandas.read_csv(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/548ec422e4ad642faa6bf06ed0418eca/File/conflict/deli_474899_(220201-220227).csv',
        engine='python', skip_blank_lines=True, parse_dates=['create_time'])
    df1 = pandas.read_csv(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/548ec422e4ad642faa6bf06ed0418eca/File/conflict/pick_474899_(220201-220227).csv',
        engine='python', skip_blank_lines=True, parse_dates=['assign_time'])
    df1['dt'] = df1['assign_time'].dt.strftime('%m-%d')
    df2['dt'] = df2['create_time'].dt.strftime('%m-%d')
    df1['tm'] = df1['assign_time'].dt.strftime('%H')
    df2['tm'] = df2['create_time'].dt.strftime('%H')
    df2 = df2.rename(columns={'operator_user': 'operator_name'})
    df1_names = df1[['operator_name']].drop_duplicates()
    df2_names = df2[['operator_name']].drop_duplicates()
    names = pandas.merge(df1_names, df2_names, on='operator_name', how='inner')
    names_ls = list(names['operator_name'])
    df1 = df1[df1['operator_name'].isin(names_ls)]
    df2 = df2[df2['operator_name'].isin(names_ls)]
    # df_get = df1.groupby(['operator_name', 'dt', 'tm']).size().reset_index(name='get')
    # df_put = df2.groupby(['operator_name', 'dt', 'tm']).size().reset_index(name='put')
    # df = pandas.merge(df_put, df_get, on=['operator_name', 'dt', 'tm'], how='inner')
    # dts = list(df['dt'].unique())
    dts = ['02-16', '02-21', '02-22', '02-23', '02-24', '02-25', '02-20']
    for i in dts:
        draw_Barh('02-24', df1, df2)
        # df_res.loc[:, ['delv']].plot.barh(ax=ax, edgecolor='k')
        # df_res.loc[:, ['pickup']].plot.barh(ax=ax, label='pickup', color=['navy', 'red'], alpha=.6, edgecolor='k',
        #                                           hatch='/')
        pass


if __name__ == '__main__':
    barline()
